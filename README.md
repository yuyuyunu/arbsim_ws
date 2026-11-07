# ArbSim ROS 2

## Building the Workspace

You can use the given Linux VM environment which has ROS 2 installed.
Before running the simulation, you need to build the ROS 2 package and source your environment.

1. Open a terminal and navigate to the root of your ROS 2 workspace (e.g., `~/arbsim_ws`):
   ```bash
   cd ~/arbsim_ws
   ```
2. Build the package using `colcon`:
   ```bash
   colcon build 
   ```

3. Source the setup file so your terminal recognizes the newly built nodes:
   ```bash
   source install/setup.bash
   ```
   *(You will need to run this `source` command in **every new terminal** you open).*
---

## Running the Code

The simulation requires two separate nodes running simultaneously. You will need two terminal windows.

**Terminal 1: Start the Simulator Window**
Ensure you have sourced your workspace, then run:
```bash
ros2 run arbsim arbsim_node
```
*This will open the Pygame window displaying the drone on the ground.*

**Terminal 2: Start the Controller (The Drone's Brain)**
Open a new terminal, source the workspace (`source ~/arbsim_ws/install/setup.bash`), and run:
```bash
ros2 run arbsim sim_control
```
*As soon as this node starts, the drone will begin executing the logic programmed in the controller.*

---

* **`sim_control.py`**: **EDIT THIS FILE**. This is the file that sends commands to the drone. You will write all your mission logic here.

---

## Task: Draw a Square

Modify `sim_control.py` so that the drone autonomously flies in a square pattern.
