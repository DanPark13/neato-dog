import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Open a connection to the webcam
cap = cv2.VideoCapture(0)

# Define a function to interpret basic gestures
def interpret_gesture(landmarks):
    """
    Interpret Basic Gestures

    ::landmarks:: detected hand points
    """
    # Convert normalized landmarks to a more usable form
    points = [(landmark.x, landmark.y, landmark.z) for landmark in landmarks.landmark]

    # Example 1: "Thumbs Up"
    # Ensure tip of thumb is vertically higher than middle and base joints
    # Verifies base of index finger is higher than middle joint
    if points[mp_hands.HandLandmark.THUMB_TIP][1] < points[mp_hands.HandLandmark.THUMB_IP][1] < points[mp_hands.HandLandmark.THUMB_MCP][1]:
        if points[mp_hands.HandLandmark.INDEX_FINGER_MCP][1] < points[mp_hands.HandLandmark.INDEX_FINGER_PIP][1]:
            return "Thumbs Up"

    # Example 2: "Fist" (All fingers folded)
    # If all finger MCP joints are vertically above their respective PIP joints
    if all(points[i][1] > points[i + 1][1] for i in [mp_hands.HandLandmark.INDEX_FINGER_MCP, 
                                                     mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
                                                     mp_hands.HandLandmark.RING_FINGER_MCP,
                                                     mp_hands.HandLandmark.PINKY_MCP]):
        return "Fist"

    # If no gesture recognized
    return None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Captures frames from webcam
    frame = cv2.flip(frame, 1) # Flip camera which is more intuitive for hand tracking
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # To RBG
    results = hands.process(rgb_frame)

    # Draw hand landmarks, recognize gestures, and display confidence
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get the recognized gesture
            gesture = interpret_gesture(hand_landmarks)
            confidence = handedness.classification[0].score  # Get the confidence score
            if gesture:
                # Display the gesture and confidence on the frame
                cv2.putText(frame, f"Gesture: {gesture}, Confidence: {confidence:.2f}", 
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                print(f"Detected gesture: {gesture} with confidence: {confidence:.2f}")

    # Display the frame with landmarks and gesture text
    cv2.imshow("Hand Gesture Recognition", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close windows
cap.release()
cv2.destroyAllWindows()
