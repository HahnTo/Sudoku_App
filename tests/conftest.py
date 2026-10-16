"""Gemeinsame Fixtures für die Tests."""
import gc
import sys
import tkinter as tk
from pathlib import Path
from types import SimpleNamespace

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from sudoku_app.controller import SudokuController
from sudoku_app.model import SudokuModel
from sudoku_app.view import SudokuView

OFFSCREEN = "+9000+9000"


def clear_children(root):
    for child in root.winfo_children():
        try:
            child.destroy()
        except tk.TclError:
            pass


@pytest.fixture(scope="session")
def tk_root():
    root = tk.Tk()
    root.geometry(OFFSCREEN)
    yield root
    root.destroy()


@pytest.fixture
def app(tk_root, monkeypatch):
    clear_children(tk_root)
    # PhotoImage-Destruktoren nicht mitten in der nächsten image create laufen lassen
    gc.collect()

    view = None
    for _ in range(3):
        try:
            view = SudokuView(tk_root)
            break
        except tk.TclError:
            clear_children(tk_root)
            gc.collect()
    if view is None:
        view = SudokuView(tk_root)

    tk_root.geometry(OFFSCREEN)
    model = SudokuModel()
    controller = SudokuController(model, view)

    messages = []
    monkeypatch.setattr(view, "show_fail", lambda: messages.append("fail"))
    monkeypatch.setattr(view, "show_loose", lambda: messages.append("loose"))
    monkeypatch.setattr(view, "show_win", lambda: messages.append("win"))
    monkeypatch.setattr(tk.messagebox, "showerror",
                        lambda *args, **kwargs: messages.append("error"))

    tk_root.update()

    yield SimpleNamespace(root=tk_root, view=view, model=model,
                          controller=controller, messages=messages)

    view.stop_timer()
    clear_children(tk_root)
