import tkinter as tk

from view import SudokuView
from model import SudokuModel

# Hauptfenster
root = tk.Tk()

# View, Controller etc erstellen
sudoku_view = SudokuView(root)

sudoku_model = SudokuModel()

sudoku_view.set_grid_values(sudoku_model.unsolved_sudoku)



# Mainloop starten
root.mainloop()
