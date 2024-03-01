import random
import tkinter as tk
import keyboard

win = tk.Tk()


def update(e=None):
    # здесь будут делаться функции с FPS 10
    win.after(int(1000 / FPS))


FPS = 10
CANVAS = tk.Canvas(win, bg='white', bd=0, highlightthickness=0)
CANVAS.place(x=0, y=0, width=win.winfo_screenwidth(), height=win.winfo_screenheight())
win.overrideredirect(True)
win.state('zoomed')
win.wm_attributes("-topmost", True)
win.wm_attributes("-transparentcolor", "white")
win.after(int(1000 / FPS), update)
win.mainloop()
