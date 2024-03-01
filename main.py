import tkinter as tk
from tkinter import ttk

state = "pressed"
bitchy
def btn_start_click():
    if state == "pressed":
        for i in range(20 + cmb_lvl.current() * 3):
            btn_current = tk.Button(
                master=frm_game,
                bg="red",
                width=10,
                height=10
            )
            btn_current.grid(
                row=2,
                column=2,
                padx=5,
                pady=5
            )


if __name__ == '__main__':
    # GUI
    win = tk.Tk()

    frm_bg = tk.Frame(
        master=win,
        bg="gray",
        width=1,
        height=1,
        padx=10,
    )
    frm_bg.pack(fill=tk.BOTH, expand=True)
    # Header
    frm_header = tk.Frame(
        master=frm_bg,
        padx=10
    )
    frm_header.pack(fill=tk.X)
    # label
    lbl_head = tk.Label(
        master=frm_header,
        text="Игра N-Back Training"
    )
    lbl_head.pack(side=tk.TOP)
    # combobox
    levels = [x for x in range(1, 11)]

    cmb_lvl = ttk.Combobox(
        master=frm_header
    )
    cmb_lvl['values'] = levels
    cmb_lvl['state'] = 'readonly'
    cmb_lvl.pack(side=tk.LEFT)
    # start button
    btn_start = tk.Button(
        master=frm_header,
        command=btn_start_click,
        borderwidth=2,
        text="start",
        fg="white",
        bg="gray",
        width=7,
        height=1
    )
    btn_start.pack(side=tk.RIGHT)
    # Game
    frm_game = tk.Frame(
        master=frm_bg,
        bg="white",
        borderwidth=2
    )

    win.mainloop()
