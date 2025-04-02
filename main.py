import cv2
import mediapipe as mp
import threading
from app import Pydance
from fonction import process_frame, detect_arm_position

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

quit_program = False

# Fonction pour afficher la caméra
def display_camera():
    global quit_program
    with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened() and not quit_program:
            frame, results = process_frame(cap, holistic)
            if frame is None:
                break

            left_arm, right_arm = detect_arm_position(results)
            print(f"Gauche: {left_arm}    Droit: {right_arm}")

            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

            cv2.imshow("Détection du bras tendu", frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                quit_program = True

        cap.release()
        cv2.destroyAllWindows()

# Fonction pour démarrer Tkinter
def start_tkinter():
    app = Pydance()
    app.mainloop() 
    app.change_state("TESTTTT")


start_tkinter()

# Lancer la caméra dans un thread séparé
camera_thread = threading.Thread(target=display_camera)
camera_thread.start()

# Lancer l'application Tkinter dans le thread principal


# Assurer que le thread de la caméra se termine proprement
camera_thread.join()