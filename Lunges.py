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
improvement = "Lower your knee properly."
max_angle = 160
min_angle = 100
proper_depth_range = (80, 100)  # Ideal knee angle for counting a lunge

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        panel_width = int(w * 0.4)
        right_panel = np.full((h, panel_width, 3), (0, 0, 0), dtype=np.uint8)
        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        try:
            landmarks = results.pose_landmarks.landmark
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            angle = calculate_angle(hip, knee, ankle)

            if angle > max_angle:
                stage = "up"
            elif proper_depth_range[0] < angle < proper_depth_range[1] and stage == "up":
                counter += 1
                stage = "down"
                feedback = "Good lunge! Keep your form steady."
                improvement = "Maintain balance and control."
            else:
                feedback = "Ensure full range of motion."
                improvement = "Bend your knee properly and maintain stability."

        except:
            feedback = "Make sure your legs are visible."
            improvement = "Adjust camera for full-body view."

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

        def put_centered_text(panel, text, y, font_scale=0.6):
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(text, font, font_scale, 2)[0]
            text_x = (panel_width - text_size[0]) // 2
            cv2.putText(panel, text, (text_x, y), font, font_scale, (255, 255, 255), 2, cv2.LINE_AA)

        put_centered_text(right_panel, "Lunge Counter", 40, font_scale=1)
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
        cv2.imshow('Lunge Tracker', combined_view)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
