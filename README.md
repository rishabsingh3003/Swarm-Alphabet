# Swarm Alphabet

An easy to implement project on Swarm Robotics! Multiple robots are scattered in the frame. The objective is to form recognizable shapes from them, without any collisions, in the least time possible. Multiple path planning algorithms (like A* and Djikstra), with swarm optimization algorithms will be applied to achieve this goal. ArUco markers are used to detect the position of the bots, and movement commands are sent through UDP packets to individual bots using in-build WiFi in ESP8266. The ESP8266 controls the robot's movement using a motor controller. 

**Note: This project is a work in progress.** 

 ![Demo](Docs/demo.gif)


## Getting Started

The project is divided into several subsections. A non-technical summary is given below:
- Localising the position of the robot's (i.e OpenCV + ArUco Markers)
- Planning the path of the robot using current, goal, and obstacle positions.
- Transforming the planned path to a control system equation. The error generated ('goal loc - present loc') is fed into PID loops.
- The error is therefore converted to pwm signal and transmitted to the microcontrollers via UDP connection,which can be used by the motor controller to physically move the bots.
- The present location and the path followed by each bot is plotted on pygame for easy visualization. 

## Prerequisites

### Software
The project uses several dependencies for faster prototyping. *These dependencies will be removed in the later stages.*
The project is entirely built on python (The ESP8266 use's C (Arduino) which will be gradually shifted to micropython).
The updated list of python packages needed are listed here:
```
- Numpy
- OpenCV 4.2
- Pygame
- Pandas
- Sympy
- Simple-Pid

```
**Please Make sure you have the latest version of these packages installed**

### Hardware

```
- Webcam (Minimum 30 fps recommended)
- Small chassis 
- Wheels
- ESP 8266 NodeMCU (Micro-Controller)
- Battery's
- Wires, switches, jumper cables, etc.
```

## Deployment
 - Assemble the basic bots. Please keep in mind the following details, while connecting peripherals to the NodeMCU
 
 ![GPIO Limitations](Docs/GPIO_Limitations.jpg)
 
 - Upload the code, found [here](/Motor_Controller) onto the MCU
 - Run [aruco_thread.py](OpenCV/aruco_thread.py) to switch on ArUco detection
 - Run [bot_x.py](Navigation/) (in a separate terminal) to send moving signal to the robots
 - Run [pygame_display.py](GUI/pygame_display.py) (in a separate terminal) to view the bots in pygame 

**Easier deployment technique to run from a single command window is being worked upon**



## License

This project is licensed under the GPL 3.0 License - see the [LICENSE.md](LICENSE.md) file for details



