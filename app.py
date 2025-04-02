from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import cv2
import mediapipe as mp
from fonction import process_frame, detect_arm_position

class Pydance(Tk):
    def __init__(self):
        super().__init__()

        self.title("PyDance")
        self.geometry("1100x765")

        self.rec = True
        
        # Frame principal
        frm = ttk.Frame(self, padding=10)
        frm.grid()

        # Titre de l'application
        title_lbl = ttk.Label(frm, text="Pydance", font=("Times 24")).grid(column=0, row=0)

        # Bouton de démarrage
        start_btn = ttk.Button(frm, text="Commencer", command=self.start).grid(column=0, row=1)

        stop_btn = ttk.Button(frm, text="Arreter", command=self.stop).grid(column=0, row=2)

        # Image d'arrière-plan
        image = Image.open("./img/template.png")
        self.photo = ImageTk.PhotoImage(image) 
        photo_lbl = Label(self, image=self.photo)
        photo_lbl.grid(column=2, row=2, padx=(500, 0))

        # Texte de l'état
        self.text = StringVar()
        self.text.set("...")
        self.state_lbl = Label(self, textvariable=self.text, font=("Times 16")).grid(column=1, row=10) 

        # self.score_lbl = Label(self, textvariable=text, font=("Times 18")).grid(column=2, row=4)

        # Label pour afficher la caméra
        self.video_label = Label(self)
        self.video_label.grid(row=0, column=1)

        # Initialiser la caméra
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)


    def start(self):
        print("Commencer")
        # Lancer la capture vidéo dans un thread séparé
        self.quit_program = False
        self.video_thread = threading.Thread(target=self.display_camera)
        self.video_thread.start()

    def stop(self):
        self.rec = False
        self.quit_program = True

        self.video_label.img_tk = self.photo  # Garder une référence pour éviter la suppression automatique
        self.video_label.config(image=self.photo)

    def change_state(self, state):
        print("State changé")
        self.text.set(state)

    def display_camera(self):
        mp_holistic = mp.solutions.holistic
        mp_drawing = mp.solutions.drawing_utils
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while not self.quit_program and self.rec:
                frame, results = process_frame(self.cap, holistic)
                if frame is None:
                    break

                left_arm, right_arm = detect_arm_position(results)
                # print(f"Gauche: {left_arm}    Droit: {right_arm}")
                # self.text.set("zojzdokzdo")
                self.after(0, self.text.set, f"Gauche: {left_arm}    Droit: {right_arm}")

                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

                # Convertir l'image de la caméra en format compatible avec Tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)

                # Mettre à jour l'image dans le label Tkinter
                self.video_label.img_tk = img_tk  # Garder une référence pour éviter la suppression automatique
                self.video_label.config(image=img_tk)

                # Pause pour éviter que la fenêtre ne se bloque
                self.after(10)

    def on_close(self):
        self.quit_program = True
        self.cap.release()
        self.destroy()

# Créer et démarrer l'application
if __name__ == "__main__":
    app = Pydance()
    app.protocol("WM_DELETE_WINDOW", app.on_close)  # Gérer la fermeture de la fenêtre
    app.mainloop()
