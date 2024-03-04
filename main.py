import random
import tkinter as tk
from PIL import ImageTk, Image
win = tk.Tk()


class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.width = 200
        self.height = 200
        """
        Задаем персонажу его спрайт по пути файла спрайта
        инициализируем нашего персонажа на начальных координатах, данных при инициализации класса
        """
        self.current_sprite = None
        self.pers = canvas.create_image(self.x, self.y, anchor='nw', image=self.current_sprite)
        self.change_current_sprite(r"sprites\MoxStand.png")

        # Все, что связано с действиями персонажа
        # массив нужен для случайного выбора действия
        self.action_list = ["moveRight", "moveLeft", "jumpRight", "jumpLeft"]
        self.action = None
        self.action_count = 0
        self.impulse_x = 0
        self.impulse_y = 0

    # Создает объект картинки по строке пути картинки
    def change_current_sprite(self, path):
        self.current_sprite = ImageTk.PhotoImage((Image.open(path).resize((self.width, self.height))))
        canvas.itemconfigure(self.pers, image=self.current_sprite)

    # Она возвращает координаты нашего персонажа
    def get_cords(self):
        return self.x, self.x + self.width, self.y, self.y + self.height

    # Она возвращает скорость нашего персонажа по оси х и у
    def get_speed(self):
        return self.impulse_x, self.impulse_y

    def set_impulse(self, impulse_x, impulse_y):
        self.impulse_y = impulse_y
        self.impulse_x = impulse_x

    # Смещение персонажа направо, налево и по вертикали
    def move(self, direction, speed):

        # перемещение по горизонтали
        if (direction == "horizontal" and
                ((speed > 0 and self.x + self.width + speed <= max_x) or (speed < 0 and self.x + speed >= 1))):
            self.x += speed
        # доводит положение персонажа до правого края, но не дает выйти за него
        elif direction == "horizontal" and self.x + self.width + speed > max_x:
            self.x = max_x - self.width
        # то же самое что выше, но только с левым краем
        elif direction == "horizontal" and self.x + speed <= 1:
            self.x = 1

        # перемещение по вертикали
        if direction == "vertical" and self.y + self.height + speed <= max_y:
            self.y += speed
        # доводит положение персонажа до нижнего края, но не дает выйти за него, за верхний выходить можно
        elif direction == "vertical" and self.y + self.height + speed > max_y:
            self.y = max_y - self.height
        else:
            return 'Direction can accept only "right"/"left/vertical" arguments'

        canvas.coords(self.pers, self.x, self.y)

    # Функция инерции, постепенно увеличивает скорость, с которой падает наш персонаж, пока в воздухе,
    # А так же постепенно останавливает его движение по горизонтали, если тот в воздухе
    def inertia(self):
        if self.y + self.height < max_y:
            self.impulse_y += y_gravity

        # если шлепается об землю, то импульс приравнивается нулю
        elif self.y + self.height == max_y:
            self.impulse_y = 0

        # снижение скорости при положительном импульсе (движение вправо)
        if (self.impulse_x >= 0) and self.impulse_x - x_gravity >= 0 and self.y + self.height < max_y:
            self.impulse_x -= x_gravity

        # снижение скорости при отрицательном импульсе (движение влево)
        elif (self.impulse_x <= 0) and self.impulse_x + x_gravity <= 0 and self.y + self.height < max_y:
            self.impulse_x += x_gravity

        # если его импульс меньше, чем значение гравитации, то мы приравниваем его нулю, что бы персонаж
        # не полетел в обратную сторону
        elif self.impulse_x - x_gravity < 0 and self.y + self.height < max_y:
            self.impulse_x = 0


# набор пресетов для движения
def pers_action(action):
    action_weight = 0
    match action:
        case "moveLeft":
            mox.change_current_sprite("sprites/MoxLeft.png")
            mox.set_impulse(-5, 0)
            action_weight = 5
        case "moveRight":
            if mox.action_count % 3 == 0:
                mox.change_current_sprite("sprites/MoxRight_stepOne.jpg")
            else:
                mox.change_current_sprite("sprites/MoxRight_stepTwo.jpg")
            mox.set_impulse(5, 0)
            action_weight = 5
        case "jumpLeft":
            mox.change_current_sprite("sprites/MoxLeft.png")
            mox.set_impulse(-5, -15)
            action_weight = 100
            win.after(100)
        case "jumpRight":
            mox.change_current_sprite("sprites/MoxRight.png")
            mox.set_impulse(5, -15)
            mox.action_count = 200
            win.after(100)
        case "idle":
            mox.change_current_sprite("sprites/MoxStand.png")
            mox.set_impulse(0, 0)
            action_weight = 2
    mox.action_count -= action_weight


def update():
    x_speed, y_speed = mox.get_speed()
    mox.move("vertical", y_speed)
    mox.move("horizontal", x_speed)
    mox.inertia()
    x1, x2, y1, y2 = mox.get_cords()

    # Здесь будут происходить события с нашим персонажем, если он стоит на земле
    if y2 >= max_y:
        if mox.action_count <= 0:
            mox.action = random.choice(mox.action_list)
            mox.action_count = random.randint(300, 500)
            win.after(1000 // FPS, update)

        # Делает так, чтобы персонаж стоял на месте между действиями.
        elif mox.action_count <= 200:
            pers_action("idle")
            win.after(1000 // FPS, update)
        else:
            pers_action(mox.action)
            win.after(1000 // FPS, update)
    else:
        win.after(1000 // FPS, update)


FPS = 25
y_gravity = 1
x_gravity = 0.2
max_x = win.winfo_screenwidth()
max_y = win.winfo_screenheight()

# Создаем Canvas, на котором будет перемещаться персонаж и заливаем его прозрачным цветом
canvas = tk.Canvas(win, bg='white', bd=0, highlightthickness=0)
canvas.place(x=0, y=0, width=max_x, height=max_y)
win.overrideredirect(True)
win.state('zoomed')
win.wm_attributes("-topmost", True)
win.wm_attributes("-transparentcolor", "white")

# Создаем персонажа на определенных координатах
mox = Person(500, 1)

# Зацикливаем нашу программу с фиксированным FPS
if __name__ == '__main__':
    win.after(1000 // FPS, update)
    win.mainloop()

