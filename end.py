from tkinter import *
from tkinter import ttk


class EndPage(Tk):
    def __init__(self, points):
        super().__init__()

        self.points = points

        self.title("Fin")
        self.geometry("300x200")

        self.title_lbl = ttk.Label(self, text="Partie terminée !", font=("Times 16")).grid(row=1, column=1)

        self.points_lbl = ttk.Label(self, text=f"Vous avez fait {self.points} points", font=("Times 16")).grid(row=2, column=1)

    def on_close(self):
        self.quit_program = True
        self.destroy()