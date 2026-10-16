import tkinter as tk

from .controller import SudokuController
from .model import SudokuModel
from .view import SudokuView


def main():
    root = tk.Tk()

    sudoku_view = SudokuView(root)
    sudoku_model = SudokuModel()
    sudoku_controller = SudokuController(sudoku_model, sudoku_view)

    root.mainloop()


if __name__ == "__main__":
    main()
