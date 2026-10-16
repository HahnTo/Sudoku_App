import tkinter as tk

from view import SudokuView
from model import SudokuModel
from controller import SudokuController

# Hauptfenster
root = tk.Tk()

# View, model und Controller erstellen
sudoku_view = SudokuView(root)

sudoku_model = SudokuModel()

sudoku_controller = SudokuController(sudoku_model, sudoku_view)


# Mainloop starten
root.mainloop()
