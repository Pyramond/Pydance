from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import cv2
import mediapipe as mp
from fonction import process_frame, detect_arm_position
import time
import random

class Pydance(Tk):
    def __init__(self):
        super().__init__()

        self.title("PyDance")
        self.geometry("1500x765")
        
        self.rec = True
        self.game = False
        self.start_time = None
        self.var = None
        self.round = False
        self.score = 0
        self.range_start = 0
        self.range_end = 3

        frm = ttk.Frame(self, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        title_lbl = ttk.Label(frm, text="Pydance", font=("Times 24")).grid(column=0, row=0)
        start_btn = ttk.Button(frm, text="Commencer", command=self.start).grid(column=0, row=1)
        stop_btn = ttk.Button(frm, text="Arreter", command=self.stop).grid(column=0, row=2)

        image = Image.open("./img/template.png")
        self.photo = ImageTk.PhotoImage(image)

        self.text = StringVar()
        self.text.set("")
        self.state_lbl = Label(self, textvariable=self.text, font=("Times 16")).grid(row=2, column=1)

        self.time_text = StringVar()
        self.time_text.set("")
        self.time_lbl = Label(self, textvariable=self.time_text, font=("Times 16")).grid(row=3, column=1)

        self.order_text = StringVar()
        self.order_text.set("")
        self.order_lbl = Label(self, textvariable=self.order_text, font=("Times 16")).grid(row=4, column=1)

        self.score_text = StringVar()
        self.score_text.set("")
        self.score_lbl = Label(self, textvariable=self.score_text, font=("Times 16")).grid(row=5, column=1)

        self.video_label = Label(self)
        self.video_label.grid(row=0, column=1)

        self.img_lbl = Label(self)
        self.img_lbl.grid(row=0, column=2)


        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)


    def start(self):
        self.game = True
        self.start_time = time.time()
        
        self.quit_program = False
        self.video_thread = threading.Thread(target=self.display_camera)
        self.video_thread.start()

        self.after(0, self.score_text.set, "Score: 0 points")

    def stop(self):
        self.rec = False
        self.quit_program = True

        self.video_label.img_tk = self.photo
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

                elapsed_time = round(time.time() - self.start_time, 1)
                
                self.after(0, self.time_text.set, f"Temps: {elapsed_time}s")
                self.after(0, self.text.set, f"Gauche: {left_arm}    Droit: {right_arm}")

                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)

                if not self.round:
                    game_mov_left = random.choice(["top", "bot", "mid", "none"])
                    game_mov_right = random.choice(["top", "bot", "mid", "none"])
                    self.round_start_time = time.time() 
                    self.round = True

                    frame_img = Image.open(f"./img/{game_mov_left}_{game_mov_right}.png")

                    width, height = frame_img.size 
                    new_width = 300
                    new_height = int((new_width / width) * height)

                    frame_img_resized = frame_img.resize((new_width, new_height))
                    frame_img_tk = ImageTk.PhotoImage(frame_img_resized)
                    self.img_lbl.frame_img_tk = frame_img_tk
                    self.img_lbl.config(image=frame_img_tk)




                round_elapsed_time = time.time() - self.round_start_time
                time_left = self.range_end - round_elapsed_time
                self.after(0, self.time_text.set, f"Temps restant : {round(time_left, 1)}s")

                self.after(0, self.order_text.set, f"Bras gauche: {game_mov_left}   Bras droit: {game_mov_right}")

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)

                self.video_label.img_tk = img_tk
                self.video_label.config(image=img_tk)

                if round_elapsed_time >= self.range_end:
                    if game_mov_right == right_arm and game_mov_left == left_arm:
                        self.score += 1
                        self.after(0, self.score_text.set, f"Score: {self.score} points")
                    self.round = False

    def on_close(self):
        self.quit_program = True
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = Pydance()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
