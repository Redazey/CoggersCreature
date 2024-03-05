import random
import tkinter as tk
from PIL import ImageTk, Image
win = tk.Tk()


class Sprite:
    def __init__(self, path: str, duration, width, height):
        self.sprite = ImageTk.PhotoImage(Image.open(path).resize((width, height)))
        # Длительность расчитывается по формуле "длительность в секундах / (1 секунда / FPS)",
        # итого получаем длительность в кадрах
        # i.e. 5sec / (1sec / 25FPS) = 125 frames
        self.max_duration = duration / (1 / FPS)
        self.current_duration = 0

    # Обновляет длительность этого кадра
    def update(self):
        self.current_duration -= 1

    # Стартует длительность этого кадра
    def start(self):
        self.current_duration = self.max_duration


# Класс для создания каких либо действий персонажа. P.s. Sprites это неизменяемый массив, а значит минимальное кол-во
# спрайтов должно быть хотя бы 2, если действие использует лишь один спрайт, то дублируйте его.
class PersAction:
    # длительность в секундах если что
    def __init__(self, impulse_x, impulse_y, duration, sprites: tuple):
        self.impulse_x = impulse_x
        self.impulse_y = impulse_y
        self.max_duration = duration / (1 / FPS)
        self.current_duration = 0
        self.sprites = sprites
        self.current_sprite = sprites[0]
        self.current_sprite.start()

    def update(self):
        if self.current_sprite.current_duration > 0:
            self.current_sprite.update()
        else:
            for sprite in self.sprites:
                if sprite.current_duration > 0:
                    self.current_sprite = sprite
        self.current_duration -= 1
        return self.current_sprite.sprite

    def start(self):
        self.current_duration = self.max_duration
        return self.impulse_x, self.impulse_y, self.current_sprite


class Person:
    def __init__(self, start_x, start_y, action_list: tuple):
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

        # Все, что связано с действиями персонажа
        # массив нужен для случайного выбора действия
        self.action_list = action_list
        self.action = None
        self.impulse_x = 0
        self.impulse_y = 0

    # Она возвращает координаты нашего персонажа
    def get_cords(self):
        return self.x, self.x + self.width, self.y, self.y + self.height

    def set_impulse(self, impulse_x, impulse_y):
        self.impulse_y = impulse_y
        self.impulse_x = impulse_x

    # Смещение персонажа направо, налево и по вертикали
    def move(self, direction: str, impulse):
        # перемещение по горизонтали
        if (direction == "horizontal" and
                ((impulse > 0 and self.x + self.width + impulse <= max_x) or (impulse < 0 and self.x + impulse >= 1))):
            self.x += impulse
        # доводит положение персонажа до правого края, но не дает выйти за него
        elif direction == "horizontal" and self.x + self.width + impulse > max_x:
            self.x = max_x - self.width
        # то же самое что выше, но только с левым краем
        elif direction == "horizontal" and self.x + impulse <= 1:
            self.x = 1

        # перемещение по вертикали
        if direction == "vertical" and self.y + self.height + impulse <= max_y:
            self.y += impulse
        # доводит положение персонажа до нижнего края, но не дает выйти за него, за верхний выходить можно
        elif direction == "vertical" and self.y + self.height + impulse > max_y:
            self.y = max_y - self.height
        else:
            return 'Direction can accept only "horizontal/vertical" arguments'

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


def update():
    mox.move("vertical", mox.impulse_y)
    mox.move("horizontal", mox.impulse_x)
    mox.inertia()
    x1, x2, y1, y2 = mox.get_cords()

    # Здесь будут происходить события с нашим персонажем, если он стоит на земле
    if y2 >= max_y:
        # Если действие для персонажа еще не задано, или оно закончилось, то задаем новое
        if mox.action is None or mox.action.current_duration == 0:
            mox.action = random.choice(mox.action_list)
            mox.impulse_x, mox.impulse_y, mox.current_sprite = mox.action.start()
            win.after(1000 // FPS, update)
        else:
            mox.current_sprite = mox.action.update()
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

# Инициализируем объект mox из класса Person, с начальными координатами и набором действий
mox = Person(500, 0, ())
# набор стандартных движений
move_right = PersAction(5, 0, 3, (
        Sprite("sprites/MoxRight_1.jpg", 1, mox.width, mox.height),
        Sprite("sprites/MoxRight_2.jpg", 1, mox.width, mox.height)
    )
)

move_left = PersAction(-5, 0, 3, (
        Sprite("sprites/MoxLeft.png", 1, mox.width, mox.height),
        Sprite("sprites/MoxLeft.png", 1, mox.width, mox.height)
    )
)

jump_right = PersAction(5, -15, 1, (
        Sprite("sprites/MoxStand.png", 1, mox.width, mox.height),
        Sprite("sprites/MoxStand.png", 1, mox.width, mox.height)
    )
)

jump_left = PersAction(-5, -15, 1, (
        Sprite("sprites/MoxStand.png", 1, mox.width, mox.height),
        Sprite("sprites/MoxStand.png", 1, mox.width, mox.height)
    )
)

idle = PersAction(0, 0, 5, (
        Sprite("sprites/MoxStand.png", 1, mox.width, mox.height),
        Sprite("sprites/MoxStand.png", 1, mox.width, mox.height)
    )
)

# Суем наши действия в сам объект mox
mox.action_list = (move_right, move_left, jump_right, jump_left)
mox.action = idle

# Зацикливаем нашу программу с фиксированным FPS
if __name__ == '__main__':
    win.after(1000 // FPS, update)
    win.mainloop()
