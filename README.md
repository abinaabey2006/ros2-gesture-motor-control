ROS 2 Vision-to-Hardware Actuation System
Overview

This repository contains a robotics integration project that bridges high-level computer vision with low-level physical hardware control. Utilizing ROS 2 Humble on Ubuntu 22.04, the system translates human hand gestures into physical motor actuation. A custom Python node leverages OpenCV and MediaPipe to perform real-time spatial tracking of hand landmarks. By calculating the distance between the thumb and index finger, the system establishes a precise pinch-detection threshold. This boolean state is converted into control signals and transmitted via serial communication to an Arduino Uno, which regulates an L298N motor driver to enable seamless start/stop control of a DC motor based entirely on visual inputs.
System Architecture
Hardware Components

    Microcontroller: Arduino Uno

    Motor Driver: L298N Dual H-Bridge

    Actuator: DC BO Motor

    Power Supply: External 12V Battery Source (connected to L298N)

    Sensor: Standard Integrated Web Camera

Software Stack

    Operating System: Ubuntu 22.04 LTS

    Framework: ROS 2 Humble Hawksbill

    Language: Python 3, C++ (Arduino)

    Libraries: rclpy, OpenCV (cv2), MediaPipe, PySerial

Prerequisites

Before utilizing this package, ensure your system has the following dependencies installed:

    ROS 2 Humble Desktop Install

    Python computer vision and serial communication libraries:
    Bash

    pip install mediapipe opencv-python pyserial "numpy<2"

    Arduino IDE (for flashing the microcontroller)

Hardware Setup

    Connect the BO Motor to the OUT1 and OUT2 screw terminals on the L298N driver.

    Connect the positive lead of the external power source to the L298N 12V terminal, and the negative lead to the GND terminal.

    Establish a common ground by running a jumper wire from the L298N GND terminal to any GND pin on the Arduino Uno.

    Remove the ENA jumper cap and connect the control pins from the L298N to the Arduino:

        ENA -> Arduino Pin 9 (PWM)

        IN1 -> Arduino Pin 8

        IN2 -> Arduino Pin 7

Installation & Configuration
1. Microcontroller Configuration

The Arduino must be configured to listen for serial commands from the ROS 2 node.

    Open the Arduino IDE.

    Upload the provided listener sketch (which initializes serial communication at a 115200 baud rate and writes incoming parsed integers to the ENA pin).

    Ensure the Arduino remains connected to the host machine via USB.

2. System Permissions

To allow the ROS 2 node to communicate with the USB port, grant the current user serial access permissions (requires a system restart or log out to take effect):
Bash

sudo usermod -a -G dialout $USER

3. ROS 2 Workspace Build

Navigate to your workspace root and compile the package:
Bash

cd ~/gesture_motor_ws
colcon build
source install/setup.bash

Usage

    Power on the external battery connected to the motor driver.

    Verify the Arduino Uno is connected to the host machine (default configuration targets /dev/ttyUSB0).

    Source the ROS 2 environment and execute the control node:

Bash

source ~/gesture_motor_ws/install/setup.bash
ros2 run finger_speed_controller pinch_controller

    Upon execution, the camera feed will initialize.

        Pinch Gesture (Distance < 40px): Motor stops (Transmits 0).

        Open Hand Gesture (Distance > 40px): Motor runs at maximum speed (Transmits 255).

Author

Abina Abey
