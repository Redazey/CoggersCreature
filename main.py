import random
import tkinter as tk
import keyboard
import time

win = tk.Tk()


class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y

        # инициализируем нашего персонажа на начальных координатах, данных при инициализации класса
        self.pers = canvas.create_oval(self.x, self.y, self.x + 100, self.y + 100, fill='black')

        # Все, что связано с действиями персонажа
        self.action = None 
        self.action_count = 0

    # Эта функция нужна для того, что бы получать X нашего персонажа
    def getx(self):
        return self.x

    # Эта функция нужна для того, что бы получать Y нашего персонажа
    def gety(self):
        return self.y

    # Смещение персонажа направо или налево
    def move(self, direction):
        if direction == "right" and self.x + 100 < win.winfo_screenwidth():
            self.x += 5
            canvas.coords(self.pers, self.x, self.y, self.x + 100, self.y + 100)

        elif direction == "left" and self.x > 0:
            self.x -= 5
            canvas.coords(self.pers, self.x, self.y, self.x + 100, self.y + 100)

        else:
            return 'Direction can accept only "right"/"left" arguments'


def update():
    # Здесь будут происходить события с нашим персонажем
    if mox.action_count <= 0:
        mox.action = random.choice(["moveRight", "moveLeft"])
        mox.action_count = random.randint(100, 200)
        win.after(1000 // FPS, update)

    elif mox.action_count <= 100: # Делает так, чтобы персонаж стоял на месте между действиями.
        mox.action = "doNothing"
        mox.action_count -= 2
        win.after(1000 // FPS, update)
    else:
        match mox.action:
            case "moveRight":
                mox.move("right")
                mox.action_count -= 3
                win.after(1000 // FPS, update)

            case "moveLeft":
                mox.move("left")
                mox.action_count -= 3
                win.after(1000 // FPS, update)


FPS = 25

# Создаем Canvas, на котором будет перемещаться персонаж и заливаем его прозрачным цветом
canvas = tk.Canvas(win, bg='white', bd=0, highlightthickness=0)
canvas.place(x=0, y=0, width=win.winfo_screenwidth(), height=win.winfo_screenheight())
win.overrideredirect(True)
win.state('zoomed')
win.wm_attributes("-topmost", True)
win.wm_attributes("-transparentcolor", "white")

# Создаем персонажа на определенных координатах
mox = Person(500, win.winfo_screenheight() - 100)

# Зацикливаем нашу программу с фиксированным FPS
if __name__ == '__main__':
    win.after(1000 // FPS, update)
    win.mainloop()

