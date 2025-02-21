import cv2
import mediapipe as mp
import numpy as np
import textwrap

# Function to calculate angle
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle

# MediaPipe Pose setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Variables
counter = 0  
stage = None  
exercise = "Bicep Curls"

# UI Colors
bg_color = (34, 177, 76)  # Green
separator_color = (169, 169, 169)  # Grey
text_color = (255, 255, 255)  # White

# MediaPipe Pose instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Increase panel width
        panel_width = int(w * 0.6)
        right_panel = np.full((h, panel_width, 3), bg_color, dtype=np.uint8)

        # Convert for MediaPipe
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Default feedback & improvement
        feedback = "Ensure proper posture."
        improvement = "Keep your back straight and engage your core."

        # Pose estimation
        try:
            landmarks = results.pose_landmarks.landmark
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calculate angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Rep counting logic
            if angle > 160:
                stage = "down"
            elif angle < 30 and stage == "down":
                stage = "up"
                counter += 1
                feedback = "Great form! Keep pushing!"
                improvement = "Remember to breathe properly."
            else:
                feedback = "Make sure to fully extend your arms."
                improvement = "Don't rush, maintain a steady pace."

            # Additional feedback based on posture
            if angle < 20:
                feedback = "Too much bending! Extend your arms more."
                improvement = "Try to keep your movements controlled."
            elif angle > 170:
                feedback = "You're overextending. Avoid locking your joints."
                improvement = "Keep a slight bend at the top."
        
        except:
            feedback = "Ensure full visibility of your arm."
            improvement = "Adjust your camera or position."

        # Draw landmarks
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=2))

        # UI Layout
        section_height = h // 4

        # Grey separators
        right_panel[section_height - 2:section_height + 2] = separator_color
        right_panel[2 * section_height - 2:2 * section_height + 2] = separator_color
        right_panel[3 * section_height - 2:3 * section_height + 2] = separator_color

        # Text styling
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7  
        font_thickness = 2

        # Function to center text in a section
        def put_centered_text(panel, text, y, font_scale=0.7):
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            text_x = (panel_width - text_size[0]) // 2
            cv2.putText(panel, text, (text_x, y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

        # Exercise Name
        put_centered_text(right_panel, exercise.upper(), section_height // 2, font_scale=1.2)

        # Rep Count
        put_centered_text(right_panel, f'Reps: {counter}', section_height + (section_height // 2), font_scale=1.2)

        # Feedback Section
        put_centered_text(right_panel, "Feedback:", 2 * section_height + 40, font_scale=0.9)
        wrapped_feedback = textwrap.wrap(feedback, width=40)
        y_text = 2 * section_height + 80
        for line in wrapped_feedback:
            put_centered_text(right_panel, line, y_text, font_scale=0.7)
            y_text += 30

        # Improvements Section
        put_centered_text(right_panel, "Improvements:", 3 * section_height + 40, font_scale=0.9)
        wrapped_improvement = textwrap.wrap(improvement, width=40)
        y_text = 3 * section_height + 80
        for line in wrapped_improvement:
            put_centered_text(right_panel, line, y_text, font_scale=0.7)
            y_text += 30

        # Combine video and UI
        combined_view = np.hstack((image, right_panel))

        # Show the window
        cv2.imshow('Workout Tracker', combined_view)

        # Quit on 'q'
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
