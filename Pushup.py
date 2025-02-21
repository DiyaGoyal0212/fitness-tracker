import cv2
import mediapipe as mp
import numpy as np
import textwrap

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

# Variables
counter = 0  
stage = None  
feedback = "Keep your back straight."
improvement = "Maintain steady movement."
max_angle = 160
min_angle = 30
shoulder_threshold = 0.05  # Minimum movement to consider a valid push-up
wrist_threshold = 0.02  # Wrist movement allowance

prev_shoulder_y = None
prev_wrist_x = None
prev_wrist_y = None

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        panel_width = int(w * 0.4)
        right_panel = np.full((h, panel_width, 3), (34, 177, 76), dtype=np.uint8)
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        try:
            landmarks = results.pose_landmarks.landmark
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            
            angle = calculate_angle(shoulder, elbow, wrist)

            # Track shoulder movement
            shoulder_y = shoulder[1]  # Y-coordinate of the shoulder
            wrist_x, wrist_y = wrist[0], wrist[1]  # X, Y coordinates of the wrist

            if prev_shoulder_y is not None and prev_wrist_x is not None and prev_wrist_y is not None:
                shoulder_movement = abs(shoulder_y - prev_shoulder_y)
                wrist_movement = abs(wrist_x - prev_wrist_x) + abs(wrist_y - prev_wrist_y)

                if angle > max_angle:
                    stage = "down"
                elif angle < min_angle and stage == "down":
                    if 25 < angle < 35 and shoulder_movement > shoulder_threshold and wrist_movement < wrist_threshold:
                        counter += 1
                        stage = "up"
                        feedback = "Great form! Keep it up."
                        improvement = "Maintain controlled movement."
                    else:
                        feedback = "Incorrect movement! Ensure full range of motion."
                        improvement = "Lower your body properly and avoid shifting hands."

            prev_shoulder_y = shoulder_y
            prev_wrist_x, prev_wrist_y = wrist_x, wrist_y

        except:
            feedback = "Ensure full visibility of your arm."
            improvement = "Adjust your camera position."
        
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2))
        
        def put_centered_text(panel, text, y, font_scale=0.6, max_width=panel_width - 20):
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
            
            # If text is too long, reduce font size dynamically
            while text_size[0] > max_width and font_scale > 0.4:
                font_scale -= 0.05
                text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
            
            text_x = (panel_width - text_size[0]) // 2
            cv2.putText(panel, text, (text_x, y), font, font_scale, (255, 255, 255), 2, cv2.LINE_AA)

        # Ensuring exercise name fits properly
        put_centered_text(right_panel, "Push-Up Counter", 40, font_scale=1, max_width=panel_width - 20)

        put_centered_text(right_panel, f'Reps: {counter}', 100, font_scale=1)
        put_centered_text(right_panel, "Feedback:", 180, font_scale=0.8)
        
        y_text = 220
        for line in textwrap.wrap(feedback, width=25):
            put_centered_text(right_panel, line, y_text)
            y_text += 30
        
        put_centered_text(right_panel, "Improvements:", 350, font_scale=0.8)
        y_text = 380
        for line in textwrap.wrap(improvement, width=25):
            put_centered_text(right_panel, line, y_text)
            y_text += 30
        
        combined_view = np.hstack((image, right_panel))
        cv2.imshow('Push-Up Tracker', combined_view)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
