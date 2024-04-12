import random
import tkinter as tk
import json
import os.path
from PIL import ImageTk, Image
from tkinter import messagebox
win = tk.Tk()


# Класс для спрайтов, по сути делает объект Sprite, имеющий все нужные свойства для создания анимаций
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


# Класс, характеризующий нашего персонажа
class Person:
    def __init__(self, start_x, start_y, width, height, action_list, default_fly, r_fly, l_fly):
        # Все, что касается размеров и положения персонажа
        self.x = start_x
        self.y = start_y
        self.width = width
        self.height = height

        # Все, что касается отображения персонажа на экране
        self.current_sprite = default_fly
        self.r_fly = r_fly
        self.l_fly = l_fly
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
            self.cur_sprites = self.r_fly
        elif self.impulse_x < 0:
            self.cur_sprites = self.l_fly
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
                self.cur_sprites[self.sprite_num].max_duration = abs(self.impulse_y) // y_gravity + 1
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
    def __init__(self, impulse_x, impulse_y, duration, delay, sprites):
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

    # Стартует длительность этого действия
    def act_start(self, pers):
        self.current_delay = self.max_delay
        self.current_duration = self.max_duration
        canvas.itemconfigure(pers.pers, image=self.current_sprite.sprite)


def user_config(e):
    def entry_generator(labels, master_frm):
        # генерация полей
        for idx, (key, text) in enumerate(labels.items()):
            # Создает ярлык с текстом из списка ярлыков.
            label = tk.Label(master=master_frm, text=key)
            # Создает текстовое поле которая соответствует ярлыку.
            entry = tk.Entry(master=master_frm, width=5)
            entry.insert(0, string=text)
            # Использует менеджер геометрии grid для размещения ярлыков и
            # текстовых полей в строку, чей индекс равен idx.
            label.grid(row=idx, column=0, sticky="e")
            entry.grid(row=idx, column=1)
            entries.append(entry)

    def conf_update(config_type):
        upd_f = open("settings.json", mode="r+")
        upd_const = json.load(upd_f)
        upd_f.seek(0)

        for upd_entry, setting in zip(entries, upd_const[config_type].keys()):
            try:
                upd_const[config_type][setting] = float(upd_entry.get())
            except ValueError:
                messagebox.showwarning("Ошибка!", "Введите численные значение!")
                return
            except AttributeError:
                continue

        upd_f.truncate()
        json.dump(upd_const, upd_f, indent=4)
        upd_f.close()

        ask = tk.Tk()
        ask.title("Вы уверены?")

        frm_confirm = tk.Frame(master=ask, padx=10, pady=10)
        frm_confirm.pack()

        lbl_confirm_txt = tk.Label(
            master=frm_confirm,
            text="Для того, что бы изменения вступили в силу, \n необходимо перезагрузить приложение. Выйти?"
        )
        lbl_confirm_txt.pack()

        btn_confirm_yes = tk.Button(master=frm_confirm, text="Да", command=exit, padx=5)
        btn_confirm_yes.pack(side=tk.LEFT, fill='both', expand=True, padx=20, pady=5)

        btn_confirm_no = tk.Button(master=frm_confirm, text="Нет", command=ask.destroy, padx=5)
        btn_confirm_no.pack(side=tk.LEFT, fill='both', expand=True, padx=20, pady=5)

    def general_conf():
        frm_pers_conf.pack_forget()
        frm_general_conf.pack(fill=tk.BOTH, expand=True)
        entries.clear()

        entry_generator(
            {
                "FPS:": general_const["FPS"],
                "Вертикальная гравитация:": general_const["yGravity"],
                "Горизонтальная гравитация:": general_const["xGravity"]
            }, frm_pers_conf
        )

        entries.append("general")

    def pers_conf():
        frm_general_conf.pack_forget()
        frm_pers_conf.pack(fill=tk.BOTH, expand=True)
        entries.clear()

        entry_generator(
            {
                "width": pers_const["width"],
                "height": pers_const["height"]
            }, frm_general_conf
        )

        entries.append(const["choice"])

    conf = tk.Tk()
    conf.title("configure")
    entries = []

    frm_conf = tk.Frame(master=conf)
    frm_conf.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    frm_general_conf = tk.Frame(master=frm_conf, padx=10, pady=10)
    frm_general_conf.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    frm_pers_conf = tk.Frame(master=frm_conf, padx=10, pady=10)
    frm_pers_conf.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    general_conf()

    frm_switch = tk.Frame(master=conf)
    frm_switch.pack(side=tk.LEFT, fill='x', expand=True)

    btn_gen_switch = tk.Button(master=frm_switch, text="Общие", command=general_conf, width=10)
    btn_gen_switch.grid(row=1, column=1)

    btn_pers_switch = tk.Button(master=frm_switch, text="Персонажи", command=pers_conf, width=10)
    btn_pers_switch.grid(row=2, column=1)

    btn_update = tk.Button(master=conf, text="Обновить", command=lambda: conf_update(entries[-1]), padx=5)
    btn_update.pack(side=tk.LEFT, fill='both', expand=True, padx=20, pady=5)


def mouse_action(event):
    person.x = event.x - person.width / 2
    person.y = event.y - person.height / 2
    person.impulse_y = 0


# Ф-ция в которой происходят все действия; функция вызывается столько же раз в секунду, сколько у нас FPS
def update():
    person.move("vertical", person.impulse_y)
    person.move("horizontal", person.impulse_x)
    person.inertia()
    x1, x2, y1, y2 = person.get_cords()
    canvas.bind('<Button-3>', user_config)
    canvas.bind('<B1-Motion>', mouse_action)

    # Здесь будут происходить события с нашим персонажем, если он стоит на земле
    if y2 == max_y:
        # Если действие для персонажа еще не задано, или оно закончилось, то задаем новое
        if person.action is None or person.action.current_duration == 0:
            # Эта проверка делает так, что бы персонаж стоял, между действиями
            if person.action == idle:
                person.action = random.choice(person.action_list)
            else:
                person.action = idle
            person.action.act_start(person)
            win.after(1000 // FPS, update)
        else:
            person.action.act_update(person)
            win.after(1000 // FPS, update)
    else:
        person.fly()
        win.after(1000 // FPS, update)


max_x = win.winfo_screenwidth()
max_y = win.winfo_screenheight()
# Создаем Canvas, на котором будет перемещаться персонаж и заливаем его прозрачным цветом
canvas = tk.Canvas(win, bg='gray', bd=0, highlightthickness=0)
canvas.place(x=0, y=0, width=max_x, height=max_y)
win.overrideredirect(True)
win.state('zoomed')
win.wm_attributes("-topmost", True)
win.wm_attributes("-transparentcolor", "gray")

# Объявляем константы и записываем их в файл, если он еще не создан
pers_width = 200
pers_height = 200
# 1000 // FPS
FPS = 1000 // 30
y_gravity = 1
x_gravity = 0.1
# Набор стандартных движений
# Delay добавляет задержку перед активацией движения, при этом смена первого кадра происходит
# P.s. delay должен быть всегда меньше, чем общая длительность действия
move_right = PersAction(5, 0, 3, 0, [
        Sprite("sprites/MoxRight_1.png", 0.5, pers_width, pers_height),
        Sprite("sprites/MoxRight_2.png", 0.5, pers_width, pers_height)
    ]
)

move_left = PersAction(-5, 0, 3, 0, [
        Sprite("sprites/MoxLeft_1.png", 0.5, pers_width, pers_height),
        Sprite("sprites/MoxLeft_2.png", 0.5, pers_width, pers_height)
    ]
)

jump_right = PersAction(7, -17, "not_repeatable", 1, [
        Sprite("sprites/MoxRJump_1.png", 1, pers_width, pers_height),
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height)
    ]
)

jump_left = PersAction(-7, -17, "not_repeatable", 1, [
        Sprite("sprites/MoxLJump_1.png", 1, pers_width, pers_height),
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height)
    ]
)

idle = PersAction(0, 0, 5, 0, [
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height),
        Sprite("sprites/MoxIdle_1.png", 1, pers_width, pers_height)
    ]
)

# список анимаций для полета влево и вправо
default_falling = Sprite("sprites/MoxJump_2.png", 0, pers_width, pers_height)

pers_r_fly = (
    Sprite("sprites/MoxRJump_2.png", 0, pers_width, pers_height),
    Sprite("sprites/MoxRJump_3.png", 0, pers_width, pers_height)
)
pers_l_fly = (
    Sprite("sprites/MoxLJump_2.png", 0, pers_width, pers_height),
    Sprite("sprites/MoxLJump_3.png", 0, pers_width, pers_height)
)


def config(state):
    default_f = open("settings.json", mode="w")
    default_const = {
        "general": {
            "FPS": FPS,
            "yGravity": y_gravity,
            "xGravity": x_gravity
        },
        "mox": {
            "width": pers_width,
            "height": pers_height,
            "actions": [
                {
                    "xImpulse": 5,
                    "yImpulse": 0,
                    "duration": 3,
                    "delay": 0,
                    "sprites": (
                        {
                            "path": "sprites/MoxRight_1.png",
                            "duration": 1
                        },
                        {
                            "path": "sprites/MoxRight_2.png",
                            "duration": 1
                        }
                    )
                },
                {
                    "xImpulse": -5,
                    "yImpulse": 0,
                    "duration": 3,
                    "delay": 0,
                    "sprites": (
                        {
                            "path": "sprites/MoxLeft_1.png",
                            "duration": 1
                        },
                        {
                            "path": "sprites/MoxLeft_2.png",
                            "duration": 1
                        }
                    )
                },
                {
                    "xImpulse": 7,
                    "yImpulse": -17,
                    "duration": "not_repeatable",
                    "delay": 1,
                    "sprites": (
                        {
                            "path": "sprites/MoxRJump_1.png",
                            "duration": 1
                        },
                        {
                            "path": "sprites/MoxIdle_1.png",
                            "duration": 1
                        }
                    )
                },
                {
                    "xImpulse": -7,
                    "yImpulse": -17,
                    "duration": "not_repeatable",
                    "delay": 1,
                    "sprites": (
                        {
                            "path": "sprites/MoxLJump_1.png",
                            "duration": 1
                        },
                        {
                            "path": "sprites/MoxLJump_2.png",
                            "duration": 1
                        }
                    )
                }
            ],
            "idle": {
                "duration": 5,
                "sprite": {
                    "path": "sprites/MoxIdle_1.png",
                    "duration": 5
                }
            },
            "defaultFalling": "sprites/MoxJump_2.png",
            "rFly": {
                "path1": "sprites/MoxRJump_2.png",
                "path2": "sprites/MoxRJump_3.png"
            },
            "lFly": {
                "path1": "sprites/MoxLJump_2.png",
                "path2": "sprites/MoxLJump_3.png"
            },
        },
        "choice": "mox"
    }

    json.dump(default_const, default_f, indent=4)
    default_f.close()

    if state:
        exit()


if not os.path.exists("settings.json"):
    # Если вызвать config с True, то после выполнения ф-ции программа закроется
    config(False)
try:
    # Читаем все из файла конфигурации
    f = open("settings.json", mode="r")
    const = json.load(f)
    general_const = const["general"]
    pers_const = const[const["choice"]]

    # Объявляем константы заново, основываясь на прочитанной информации из файла
    FPS = 1000 // int(general_const["FPS"])
    y_gravity = general_const["yGravity"]
    x_gravity = general_const["xGravity"]
    js_width = int(pers_const["width"])
    js_height = int(pers_const["height"])

    # Парсим idle из
    idle = PersAction(
        0, 0, pers_const["idle"]["duration"], 0,
        [
            Sprite(pers_const["idle"]["sprite"]["path"], pers_const["idle"]["sprite"]["duration"], js_width, js_height),
            Sprite(pers_const["idle"]["sprite"]["path"], pers_const["idle"]["sprite"]["duration"], js_width, js_height)
        ]
    )

    # Собираем все вместе и инициализируем нашего персонажа
    actions = []
    js_acts = pers_const["actions"]

    # Парсим действия из json файла
    for action in js_acts:
        js_sprites = []
        for sprite in action["sprites"]:
            js_sprites.append(Sprite(sprite["path"], sprite["duration"], js_width, js_height))
        actions.append(
            PersAction(action["xImpulse"], action["yImpulse"], action["duration"], action["delay"], js_sprites)
        )

    defaultFalling = Sprite(pers_const["defaultFalling"], 0, js_width, js_height)

    js_l_fly = []
    for js_path in pers_const["lFly"].values():
        js_l_fly.append(Sprite(js_path, 0, js_width, js_height))
    js_r_fly = []
    for js_path in pers_const["rFly"].values():
        js_r_fly.append(Sprite(js_path, 0, js_width, js_height))

    f.close()

    person = Person(500, 0, js_width, js_height, actions, defaultFalling, js_r_fly, js_l_fly)

except json.decoder.JSONDecodeError:
    # Создаем окно ошибки
    err = tk.Tk()
    err.title("ERROR!")

    # Создаем текст, оповещающий пользователя, а так же кнопки, что бы выбрать, возвращать ли файл конфига в
    # исходное состояние
    frm_error = tk.Frame(master=err, padx=10, pady=10)
    frm_error.pack()

    lbl_err_txt = tk.Label(
        master=frm_error,
        text="Произошла ошибка при обработке файла конфигурации, \nвернуть файл в исходное состояние?"
    )
    lbl_err_txt.pack()

    btn_yes = tk.Button(master=frm_error, text="Да", command=lambda: config(True), padx=5)
    btn_yes.pack(side=tk.LEFT, fill='both', expand=True, padx=20, pady=5)

    btn_no = tk.Button(master=frm_error, text="Нет", command=exit, padx=5)
    btn_no.pack(side=tk.LEFT, fill='both', expand=True, padx=20, pady=5)

    err.mainloop()

if __name__ == '__main__':
    win.after(1000 // FPS, update)
    win.mainloop()
