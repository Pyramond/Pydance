import cv2
import mediapipe as mp
import numpy as np

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

def is_arm_straight_and_at_shoulder_level(shoulder, elbow, wrist):
    if shoulder and elbow and wrist:
        shoulder_elbow = np.linalg.norm(np.array([shoulder.x, shoulder.y]) - np.array([elbow.x, elbow.y]))
        elbow_wrist = np.linalg.norm(np.array([elbow.x, elbow.y]) - np.array([wrist.x, wrist.y]))
        shoulder_wrist = np.linalg.norm(np.array([shoulder.x, shoulder.y]) - np.array([wrist.x, wrist.y]))

        arm_straight = abs(shoulder_wrist - (shoulder_elbow + elbow_wrist)) < 0.05
        tolerance = 0.11
        arm_at_shoulder_level = abs(elbow.y - shoulder.y) < tolerance and abs(wrist.y - shoulder.y) < tolerance

        return arm_straight and arm_at_shoulder_level
    return False

def is_arm_straight_and_up(shoulder, elbow, wrist):
    if shoulder and elbow and wrist:
        shoulder_elbow = np.linalg.norm(np.array([shoulder.x, shoulder.y]) - np.array([elbow.x, elbow.y]))
        elbow_wrist = np.linalg.norm(np.array([elbow.x, elbow.y]) - np.array([wrist.x, wrist.y]))
        shoulder_wrist = np.linalg.norm(np.array([shoulder.x, shoulder.y]) - np.array([wrist.x, wrist.y]))

        arm_straight = abs(shoulder_wrist - (shoulder_elbow + elbow_wrist)) < 0.05
        tolerance = 0.11

        arm_up = wrist.y - shoulder.y < 0 and abs(wrist.y - shoulder.y) > tolerance
        return arm_straight and arm_up
    return False

def is_arm_straight_and_down(shoulder, elbow, wrist):
    if shoulder and elbow and wrist:
        shoulder_elbow = np.linalg.norm(np.array([shoulder.x, shoulder.y]) - np.array([elbow.x, elbow.y]))
        elbow_wrist = np.linalg.norm(np.array([elbow.x, elbow.y]) - np.array([wrist.x, wrist.y]))
        shoulder_wrist = np.linalg.norm(np.array([shoulder.x, shoulder.y]) - np.array([wrist.x, wrist.y]))

        arm_straight = abs(shoulder_wrist - (shoulder_elbow + elbow_wrist)) < 0.05
        tolerance = 0.11

        arm_down = wrist.y - shoulder.y > 0 and abs(wrist.y - shoulder.y) > tolerance
        return arm_straight and arm_down
    return False

def process_frame(cap, holistic):
    ret, frame = cap.read()
    if not ret:
        return frame, None

    small_frame = cv2.resize(frame, (320, 240))
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(rgb_frame)

    return frame, results

def detect_arm_position(results):
    left_arm = "none"
    right_arm = "none"

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        left_shoulder = landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER]
        left_elbow = landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW]
        left_wrist = landmarks[mp_holistic.PoseLandmark.LEFT_WRIST]

        right_shoulder = landmarks[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
        right_elbow = landmarks[mp_holistic.PoseLandmark.RIGHT_ELBOW]
        right_wrist = landmarks[mp_holistic.PoseLandmark.RIGHT_WRIST]

        left_arm_up = is_arm_straight_and_up(left_shoulder, left_elbow, left_wrist)
        left_arm_ok = is_arm_straight_and_at_shoulder_level(left_shoulder, left_elbow, left_wrist)
        left_arm_down = is_arm_straight_and_down(left_shoulder, left_elbow, left_wrist)

        right_arm_up = is_arm_straight_and_up(right_shoulder, right_elbow, right_wrist)
        right_arm_ok = is_arm_straight_and_at_shoulder_level(right_shoulder, right_elbow, right_wrist)
        right_arm_down = is_arm_straight_and_down(right_shoulder, right_elbow, right_wrist)

        if left_arm_up:
            left_arm = "top"
        elif left_arm_ok:
            left_arm = "mid"
        elif left_arm_down:
            left_arm = "bot"

        if right_arm_up:
            right_arm = "top"
        elif right_arm_ok:
            right_arm = "mid"
        elif right_arm_down:
            right_arm = "bot"

    return left_arm, right_arm
