import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog as fd


def increment(var: tk.IntVar):
    var.set(var.get() + 1)


def decrement(var: tk.IntVar):
    var.set(var.get() - 1)


def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)

    window.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
