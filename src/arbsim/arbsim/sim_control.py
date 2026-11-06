#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import time

# Import standard ROS 2 message types
from geometry_msgs.msg import Twist, PoseStamped
from std_msgs.msg import Bool, Float32, Empty, String

class DroneController(Node):
    def __init__(self):
        super().__init__('drone_controller')
        self.get_logger().info("Drone Controller Node Started.")
        
        # --- PUBLISHERS (Sending commands to Simulator) ---
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.arm_pub = self.create_publisher(Bool, 'arm', 10)
        self.takeoff_pub = self.create_publisher(Float32, 'takeoff', 10)
        self.land_pub = self.create_publisher(Empty, 'land', 10)
        self.trail_pub = self.create_publisher(Bool, 'trail', 10)
        
        # --- SUBSCRIBERS (Reading state from Simulator) ---
        self.create_subscription(PoseStamped, 'pose', self.pose_callback, 10)
        self.create_subscription(String, 'status', self.status_callback, 10)
        
        # --- INTERNAL STATE VARIABLES ---
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        
        self.is_armed = False
        self.is_flying = False
        self.is_landing = False

        # --- MISSION STATE MACHINE ---
        self.mission_state = "INIT"
        self.state_start_time = time.time()
        
        # Control Loop Timer (Runs at 10 Hz)
        self.timer = self.create_timer(0.1, self.control_loop)

    def pose_callback(self, msg: PoseStamped):
        """Updates internal pose variables whenever the simulator publishes them."""
        self.current_x = msg.pose.position.x
        self.current_y = msg.pose.position.y
        self.current_z = msg.pose.position.z

    def status_callback(self, msg: String):
        """Parses the status string from the simulator."""
        status_text = msg.data
        self.is_armed = "ARMED: True" in status_text
        self.is_flying = "FLYING: True" in status_text
        self.is_landing = "LANDING: True" in status_text

    def send_arm(self, state: bool):
        msg = Bool()
        msg.data = state
        self.arm_pub.publish(msg)

    def send_takeoff(self, altitude: float):
        msg = Float32()
        msg.data = altitude
        self.takeoff_pub.publish(msg)

    def send_land(self):
        self.land_pub.publish(Empty())

    def send_trail(self, state: bool):
        msg = Bool()
        msg.data = state
        self.trail_pub.publish(msg)

    def send_velocity(self, vx: float, vy: float):
        msg = Twist()
        msg.linear.x = float(vx)
        msg.linear.y = float(vy)
        msg.linear.z = 0.0  # Simulator handles Z automatically
        self.cmd_vel_pub.publish(msg)
    

    def control_loop(self):
        """
        Main State Machine. This function is called 10 times a second.
        It checks the current state, acts, and transitions to the next state.
        """
        now = time.time()
        elapsed_in_state = now - self.state_start_time

        if self.mission_state == "INIT":
            self.get_logger().info("Arming drone...")
            self.send_arm(True)
            self.mission_state = "WAIT_FOR_ARM"
            self.state_start_time = now

        elif self.mission_state == "WAIT_FOR_ARM":
            if self.is_armed:
                self.get_logger().info("Drone armed. Sending takeoff command (5m)...")
                self.send_takeoff(5.0)
                self.mission_state = "TAKEOFF"
                self.state_start_time = now

        elif self.mission_state == "TAKEOFF":
            # Wait until altitude is reached
            if self.current_z >= 4.9:
                self.get_logger().info("Takeoff complete. Starting mission...")
                self.send_trail(True) # Turn on the trail
                self.mission_state = "MISSION_FLY_FORWARD"
                self.state_start_time = now

        # ---------------------------------------------------------
        # REPLACE THIS SECTION WITH YOUR OWN ALGORITHMS / WAYPOINTS
        # ---------------------------------------------------------
        elif self.mission_state == "MISSION_FLY_FORWARD":
            self.send_velocity(3.0, 0.0) # Fly Right (X-axis) at 3m/s
            
            if elapsed_in_state > 4.0:
                self.get_logger().info("Mission complete. Landing...")
                self.send_velocity(0.0, 0.0) # Stop moving
                self.send_land()
                self.mission_state = "LANDING"
                self.state_start_time = now
        # ---------------------------------------------------------
        
        elif self.mission_state == "LANDING":
            if not self.is_flying and not self.is_landing and self.current_z <= 0.1:
                self.get_logger().info("Landed safely. Disarming...")
                self.send_trail(False)
                self.send_arm(False)
                self.mission_state = "DONE"

        elif self.mission_state == "DONE":
            # Mission finished, do nothing
            pass

def main(args=None):
    rclpy.init(args=args)
    controller_node = DroneController()
    
    try:
        rclpy.spin(controller_node)
    except KeyboardInterrupt:
        controller_node.get_logger().info("Controller stopped by user.")
    finally:
        controller_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()