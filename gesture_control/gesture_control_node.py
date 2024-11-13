import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# Initialize MediaPipe hands module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# GestureControlNode definition
class GestureControlNode(Node):
    def __init__(self):
        super().__init__('gesture_control_node')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.run_gesture_recognition)  # Adjust timer as needed

        # Open a connection to the webcam
        self.cap = cv2.VideoCapture(0)

    # Define a function to interpret basic gestures
    def interpret_gesture(self, landmarks):
        """
        Interpret Basic Gestures (Thumbs Up, Thumbs Down, Fist)

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
        
        # Example 3: "Thumbs Down"
        # Opposite of "Thumbs Up" Values
        if points[mp_hands.HandLandmark.THUMB_TIP][1] > points[mp_hands.HandLandmark.THUMB_IP][1] > points[mp_hands.HandLandmark.THUMB_MCP][1]:
            if points[mp_hands.HandLandmark.INDEX_FINGER_MCP][1] < points[mp_hands.HandLandmark.INDEX_FINGER_PIP][1]:
                return "Thumbs Down"

        # If no gesture recognized
        return None

    def run_gesture_recognition(self):
        """Open Camera and Identify Handmarks"""
        success, frame = self.cap.read()
        if not success:
            self.get_logger().info("Ignoring empty camera frame.")
            return

        # Captures frames from webcam
        frame = cv2.flip(frame, 1) # Flip camera which is more intuitive for hand tracking
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # To RGB format
        results = hands.process(rgb_frame)

        # Draw hand landmarks, recognize gestures, and display confidence
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = self.interpret_gesture(hand_landmarks)
                
                # Get the recognized gesture
                if gesture:
                    self.publish_velocity(gesture)
                    # Display the gesture on the frame
                    cv2.putText(frame, f"Gesture: {gesture}", (10, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        # Display the frame with landmarks and gesture text
        cv2.imshow("Hand Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            return

    # From Warmup Project
    def publish_velocity(self, gesture):
        """Based on identified hand gesture, return gesture"""
        msg = Twist()
        if gesture == "Thumbs Up":
            msg.linear.x = 0.5
            msg.angular.z = 0.0
        elif gesture == "Thumbs Down":
            msg.linear.x = -0.5
            msg.angular.z = 0.0
        elif gesture == "Fist":
            msg.linear.x = 0.0
            msg.angular.z = 0.0
        
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing velocity command: {msg}")

def main(args=None):
    rclpy.init(args=args)
    node = GestureControlNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
