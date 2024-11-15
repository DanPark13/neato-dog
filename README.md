# Neato Dog: Can you teach a Neato new tricks?

**Author:** Daniel Park

## Project Overview

This project integrates real-time hand gesture recognition with ROS2 and finite state control to manage a Neato robot's movement based on detected gestures. Using [MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/guide) for recognizing hands and identifying gestures and [OpenCV](https://opencv.org/) for real-time video processing, the system identifies specific hand gestures (such as thumbs up, thumbs down, and a fist) through a webcam feed, each mapped to distinct robot states (of forwards, backwards, and stop, respectively).

## Hand Recognition

The project leverages MediaPipe’s hand tracking module to detect and track hand landmarks in real time. These landmarks represent specific 21 points on the hand (e.g., fingertips and knuckles), which are normalized to ensure consistency regardless of hand position or camera angle. The 21 handmark points make it easy to locate where each part of the hand is for specific hand gestures.

|                                 ![hand landmarks](img/hand-landmarks.png)                                 |
| :-----------------------------------------------------------------------------------------------------------------------: |
| _Fig 1. Diagram of a [MediaPipe](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker) hand landmark_ |

In real time using OpenCV, the hand marking detection looks like the following:

**Please insert gif of hand here**

## Gesture Recognition

The core of the project lies in the gesture recognition, which analyzes the positional relationships of the 21 detected hand landmarks to identify predefined gestures. The `interpret_gesture` utilizes MediaPipe's hand tracking module to extract the normalized coordinates of key hand point landmark.

### Landmark Data and Processing

As said before, MediaPipe provides 21 hand landmarks for each detected hand, corresponding to fingertips, joints, and the base of the palm. Each landmark contains normalized (x, y, z) coordinates:

- x: Horizontal position relative to the image frame.
- y: Vertical position relative to the image frame.
- z: Depth information indicating how far the point is from the camera.

For gesture detection, the function focuses primarily on the relative y coordinates (vertical positioning) of selected landmarks, as these relationships are intuitive indicators of hand posture.

### Defined Gestures

#### Thumbs Up

For a thumbs up, the key joints to look at are the following
- `THUMB_TIP`: tip of the thumb
- `THUMB_IP` and `THUMB_MCP`: intermediate joints of the thumb
- `INDEX_FINGER_MCP` and `INDEX_FINGER_PIP`: lower parts of the index finger

In the implementation, the tip of the thumb (`THUMB_TIP`) is vertically higher, represented by a lower `y` value, than its intermediate joints (`THUMB_IP`, `THUMB_MCP`). Additionally, the index finger base (`INDEX_FINGER_MCP`) must be above its middle joint (`INDEX_FINGER_PIP`).

**Please insert gif of thumbs up here**

#### Thumbs Down

The thumbs down interaction is mirrored to the thumbs up, but instead the tip of the thumb is vertically lower, represented by a higher `y` value, than the intermediate joints. The index finger condition remains the same. 

**Please insert gif of thumbs down here**

#### Fist

For a fist position, the key joints to look at are the following
- `MCP`: base of the finger joints 
- `PIP`: middle bottom of the finger joints

A fist is best represented by the knuckles peering through, so the implmentation has the base of the finger joints represented as `MCP` and the middle joint represented by `PIP` need to align so that the `MCP` is vertically higher than the `PIP`.

**Please insert gif of fist here**

## Finite State Machine Implementation

Now that the gestures were recognizable, the gestures are now ready to control a robot. I represented the controls through a finite state machine (FSM), or a system with discrete states and transitions in between states as well as inputs that can trigger these transitions.

The FSM for this project includes the following components:

**States:**
- Idle: The robot remains stationary and waits for a gesture command.
- Forward: The robot moves forward.
- Backward: The robot moves backward.
- Stopped: The robot halts its movement completely.

**Inputs:**
- Thumbs Up: Triggers the robot to transition to the Forward state.
- Thumbs Down: Triggers the robot to transition to the Backward state.
- Fist or Open Hand: Triggers the robot to transition to the Stopped state.
- No Gesture Recognized: Keeps the robot in its current state.

**Transitions:**
- Idle -> Forward: On detecting a thumbs-up gesture.
- Idle -> Backward: On detecting a thumbs-down gesture.
- Idle -> Stopped: On detecting a fist or open-hand gesture.
- Forward -> Stopped: On detecting a fist or open-hand gesture.
- Backward -> Stopped: On detecting a fist or open-hand gesture.

**Create FSM loop diagram**

The FSM implemented within the ROS2 node that handles gesture recognition and robot control. When a gesture is identified on the camera, the node publishes velocity commands to the `/cmd_vel` ROS2 topic using the `Twist` message. If a thumbs-up is shown, then the robot moves forward. If a thumbs-down is shown, then the robot moves backwards. If a fist is shown, then the robot stops moving.

|                                 ![hand landmarks](img/fsc.gif)                                 |
| :-----------------------------------------------------------------------------------------------------------------------: |
| _Fig 5. Working moving Neato with Hand Gestures_ |

## Possible Improvements

The project provides a good base leveraging prebuilt tools like MediaPipe for gesture recognition, OpenCV for real time recognition, and ROS2 for robot control. Considering the timeline I built the project in, there are a couple of areas I could have made improvements in.

### More Gestures

The most obvious improvement I could have made is add more improvements. In this project I included three gestures, but there are a multitude of gestures I could have added such as a open hand and a peace sign. Adding more gestures would allow the robot to make additional moveements such as turning or strafing in four directions. 

### More Theory-based approach

The biggest improvement I could make to this project is instead of primiarly using prebuil tools, I could have gone in a more theory-driven approach. This approach could deepen my understanding and broadening the system's capabilities. This could include developing a custom hand gesture model where I could collect and annotate data to train a convolutional neurl network for gesture classification.

I could also go in depth into a computer vision area such as feature detection algorithms such as SURF to identify key points in an image or pose estimation to learn how mediapipe detects and tracks hand landmarks in real time.

## Closing Remarks

This project supports a simple, yet robust base of combining gesture recognition and finite state control to create a responsive robot. By leveraging MediaPipe, OpenCV, and ROS2, in this implementation I was able to control a Neato that can easily be expanded on.