"""Hilfsfunktionen für die GUI-Tests."""
import tkinter as tk

SOLVED = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def find_buttons(widget):
    buttons = []
    for child in widget.winfo_children():
        if isinstance(child, tk.Button):
            buttons.append(child)
        buttons.extend(find_buttons(child))
    return buttons


def button_by_text(widget, text):
    for button in find_buttons(widget):
        if button.cget("text") == text:
            return button
    raise AssertionError(f"Button {text!r} nicht gefunden")


def button_texts(widget):
    return [b.cget("text") for b in find_buttons(widget)]


def dialogs_of(root):
    return [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]


def grid_values(view):
    return {(i, j): view.entries[i][j].get()
            for i in range(9) for j in range(9)}


def find_empty_cell(view):
    for i in range(9):
        for j in range(9):
            if view.entries[i][j].get() == "":
                return i, j
    raise AssertionError("keine leere Zelle gefunden")


def press_key(entry, root):
    entry.focus_force()
    root.update()
    entry.event_generate("<KeyRelease>")
    root.update()
