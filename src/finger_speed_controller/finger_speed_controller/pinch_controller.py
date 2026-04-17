import rclpy
from rclpy.node import Node
import cv2
import mediapipe as mp
import math
import serial
import time

class StartStopController(Node):
    def __init__(self):
        super().__init__('start_stop_controller')
        
        # Connect to Arduino 
        try:
            self.arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
            time.sleep(2) # Wait for connection to establish
            self.get_logger().info('Serial connected on /dev/ttyUSB0.')
        except Exception as e:
            self.get_logger().error(f'Connection failed: {e}')
            return

        # Initialize MediaPipe Hand Tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

        # Initialize Camera
        self.cap = cv2.VideoCapture(0)

        # Create a timer to run the processing loop at ~20 Hz
        self.timer = self.create_timer(0.05, self.process_frame) 

    def process_frame(self):
        success, img = self.cap.read()
        if not success:
            return

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get coordinates for Thumb Tip (ID 4) and Index Finger Tip (ID 8)
                h, w, c = img.shape
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                
                x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
                x2, y2 = int(index_tip.x * w), int(index_tip.y * h)

                # Draw circles and connecting line
                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)

                # Calculate the distance between fingers
                length = math.hypot(x2 - x1, y2 - y1)

                # START/STOP LOGIC
                pinch_threshold = 40 # Pixels
                
                if length < pinch_threshold:
                    speed = 0
                    cv2.putText(img, "MOTOR: STOPPED", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                else:
                    speed = 255
                    cv2.putText(img, "MOTOR: RUNNING", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                
                # Send the speed command to the Arduino
                speed_str = f"{speed}\n"
                self.arduino.write(speed_str.encode('utf-8'))
                
                # Draw the rest of the hand skeleton
                self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Start/Stop Gesture Control", img)
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = StartStopController()
    rclpy.spin(node)
    
    # Cleanup
    node.cap.release()
    cv2.destroyAllWindows()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
