import random
import tkinter as tk
from PIL import ImageTk, Image
win = tk.Tk()


class Sprite:
    def __init__(self, path: str, duration, width, height):
        self.sprite = ImageTk.PhotoImage(Image.open(path).resize((width, height)))
        # Длительность расчитывается по формуле "длительность в секундах * FPS",
        # итого получаем длительность в кадрах
        # i.e. 5sec * 25FPS = 125 frames
        self.max_duration = duration * FPS
        self.current_duration = 0

    # Обновляет длительность этого кадра
    def sprite_update(self):
        self.current_duration -= 1

    # Стартует длительность этого кадра
    def sprite_start(self):
        self.current_duration = self.max_duration


class Person:
    def __init__(self, start_x,  start_y, width, height, action_list: tuple):
        # Все, что касается размеров и положения персонажа
        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = height

        # Все, что касается отображения персонажа на экране
        self.default_sprite = Sprite("sprites/MoxJump_2.png", 0, pers_width, pers_height)
        self.current_sprite = Sprite("sprites/MoxJump_2.png", 0, pers_width, pers_height)
        self.right_flying_sprites = (
            Sprite("sprites/MoxRJump_2.png", 0, pers_width, pers_height),
            Sprite("sprites/MoxRJump_3.png", 0, pers_width, pers_height)
        )
        self.left_flying_sprites = (
            Sprite("sprites/MoxLJump_2.png", 0, pers_width, pers_height),
            Sprite("sprites/MoxLJump_3.png", 0, pers_width, pers_height)
        )
        self.cur_sprites = None
        self.sprite_num = 0
        self.pers = canvas.create_image(self.x, self.y, anchor='nw', image=self.current_sprite.sprite)

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

    # Изменение спрайта в воздухе, в зависимости от значений импульса
    def fly(self):
        if self.impulse_x > 0:
            self.cur_sprites = self.right_flying_sprites
        elif self.impulse_x < 0:
            self.cur_sprites = self.left_flying_sprites
        else:
            canvas.itemconfigure(self.pers, image=self.current_sprite.sprite)
            return
        if self.current_sprite.current_duration > 0:
            self.current_sprite.sprite_update()
        else:
            if self.sprite_num < len(self.cur_sprites) - 1:
                self.sprite_num += 1
            else:
                self.sprite_num = 0
            if self.sprite_num == 0:
                self.cur_sprites[self.sprite_num].max_duration = abs(self.impulse_y) // y_gravity
            else:
                self.cur_sprites[self.sprite_num].max_duration = self.cur_sprites[self.sprite_num - 1].max_duration
            self.cur_sprites[self.sprite_num].sprite_start()
            self.current_sprite = self.cur_sprites[self.sprite_num]
            canvas.itemconfigure(self.pers, image=self.current_sprite.sprite)

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


# Класс для создания каких либо действий персонажа. P.s. Sprites это неизменяемый массив, а значит минимальное кол-во
# спрайтов должно быть хотя бы 2, если действие использует лишь один спрайт, то дублируйте его.
class PersAction:
    # длительность в секундах если что
    def __init__(self, impulse_x, impulse_y, duration, delay, sprites: tuple):
        self.impulse_x = impulse_x
        self.impulse_y = impulse_y
        self.max_delay = delay * FPS
        self.current_delay = self.max_delay

        # not_repeatable это значение для действий, которые не должны повторяться больше одного раза (прыжки)
        if duration == "not_repeatable":
            self.max_duration = self.max_delay + 1
        else:
            self.max_duration = duration * FPS
        self.current_duration = 0

        self.sprites = sprites
        self.sprite_num = 0
        self.current_sprite = sprites[self.sprite_num]
        self.current_sprite.sprite_start()

    # Обновляет длительность действия, а так же меняет текущую анимацию, на следующую
    def act_update(self, pers):
        if self.current_delay == 0:
            # Меняет спрайт на следующий по списку, если тот не последний, в случае если последний,
            # возвращается к первому
            if self.current_sprite.current_duration > 0:
                self.current_sprite.sprite_update()
            else:
                if self.sprite_num < len(self.sprites) - 1:
                    self.sprite_num += 1
                else:
                    self.sprite_num = 0

                self.sprites[self.sprite_num].sprite_start()
                self.current_sprite = self.sprites[self.sprite_num]

            canvas.itemconfigure(pers.pers, image=self.current_sprite.sprite)
            pers.impulse_x = self.impulse_x
            pers.impulse_y = self.impulse_y
        else:
            self.current_delay -= 1

        self.current_duration -= 1

    def act_start(self, pers):
        self.current_delay = self.max_delay
        self.current_duration = self.max_duration
        canvas.itemconfigure(pers.pers, image=self.current_sprite.sprite)


def update():
    mox.move("vertical", mox.impulse_y)
    mox.move("horizontal", mox.impulse_x)
    mox.inertia()
    x1, x2, y1, y2 = mox.get_cords()

    # Здесь будут происходить события с нашим персонажем, если он стоит на земле
    if y2 >= max_y:
        # Если действие для персонажа еще не задано, или оно закончилось, то задаем новое
        if mox.action is None or mox.action.current_duration == 0:
            # Эта проверка делает так, что бы персонаж стоял, между действиями
            if mox.action == idle:
                mox.action = random.choice(mox.action_list)
            elif x2 >= max_x:
                mox.action = move_left
            elif x1 - (x2-x1) <= 0:
                mox.action = move_right
            else:
                mox.action = idle
            mox.action.act_start(mox)
            win.after(1000 // FPS, update)
        else:
            mox.action.act_update(mox)
            win.after(1000 // FPS, update)
    else:
        mox.fly()
        win.after(1000 // FPS, update)


FPS = 25
y_gravity = 1
x_gravity = 0.2
max_x = win.winfo_screenwidth()
max_y = win.winfo_screenheight()
# Создаем Canvas, на котором будет перемещаться персонаж и заливаем его прозрачным цветом
canvas = tk.Canvas(win, bg='gray', bd=0, highlightthickness=0)
canvas.place(x=0, y=0, width=max_x, height=max_y)
win.overrideredirect(True)
win.state('zoomed')
win.wm_attributes("-topmost", True)
win.wm_attributes("-transparentcolor", "gray")

# Инициализируем объект mox из класса Person, с начальными координатами и набором действий
pers_width = 200
pers_height = 200
# Набор стандартных движений
# Delay добавляет задержку перед активацией движения, при этом смена первого кадра происходит
# P.s. delay должен быть всегда меньше, чем общая длительность действия
move_right = PersAction(5, 0, 3, 0, (
        Sprite("sprites/MoxRight_1.png", 0.5, pers_width, pers_height),
        Sprite("sprites/MoxRight_2.png", 0.5, pers_width, pers_height)
    )
)

move_left = PersAction(-5, 0, 3, 0, (
        Sprite("sprites/MoxLeft_1.png", 0.5, pers_width, pers_height),
        Sprite("sprites/MoxLeft_2.png", 0.5, pers_width, pers_height)
    )
)

jump_right = PersAction(7, -17, "not_repeatable", 1, (
        Sprite("sprites/MoxRJump_1.png", 1, pers_width, pers_height),
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height)
    )
)

jump_left = PersAction(-7, -17, "not_repeatable", 1, (
        Sprite("sprites/MoxLJump_1.png", 1, pers_width, pers_height),
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height)
    )
)

idle = PersAction(0, 0, 3, 0, (
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height),
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height)
    )
)

# Суем наши действия в сам объект mox
mox = Person(0, 0, pers_width, pers_height, (move_right, move_left, jump_right, jump_left))

# Зацикливаем нашу программу с фиксированным FPS
if __name__ == '__main__':
    win.after(1000 // FPS, update)
    win.mainloop()
