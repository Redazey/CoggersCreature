import random
import tkinter as tk
import keyboard

win = tk.Tk()


class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        # инициализируем нашего персонажа на начальных координатах, данных при инициализации класса
        self.pers = canvas.create_oval(self.x, self.y, self.x + 100, self.y + 100, fill='black')

    # Эта функция нужна для того, что бы получать X нашего персонажа
    def getx(self):
        return self.x

    # Эта функция нужна для того, что бы получать Y нашего персонажа
    def gety(self):
        return self.y

    # Смещение персонажа направо или налево
    def move(self, direction):
        if direction == "right" and self.x < win.winfo_screenheight():
            self.x += 5
            canvas.coords(self.pers, self.x, self.y, self.x + 100, self.y + 100)

        elif direction == "left":
            self.x -= 5
            canvas.coords(self.pers, self.x, self.y, self.x + 100, self.y + 100)
        else:
            return 'Direction can accept only "right"/"left" arguments'


def update(e=None):
    # здесь будут происходить события с нашим персонажем
    ralsei.move("right")


FPS = 30

# Создаем Canvas, на котором будет перемещаться персонаж и заливаем его прозрачным цветом

canvas = tk.Canvas(win, bg='white', bd=0, highlightthickness=0)
canvas.place(x=0, y=0, width=win.winfo_screenwidth(), height=win.winfo_screenheight())
win.overrideredirect(True)
win.state('zoomed')
win.wm_attributes("-topmost", True)
win.wm_attributes("-transparentcolor", "white")
ralsei = Person(1, 1)

# Зацикливаем нашу программу с фиксированным FPS
if __name__ == '__main__':
    win.after(int(1000 / FPS), update)
    win.mainloop()
