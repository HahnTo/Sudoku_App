import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from sudoku_app.controller import SudokuController
from sudoku_app.model import SudokuModel
from sudoku_app.view import SudokuView


def main():
    root = tk.Tk()

    sudoku_view = SudokuView(root)
    sudoku_model = SudokuModel()
    SudokuController(sudoku_model, sudoku_view)

    root.mainloop()


if __name__ == "__main__":
    main()
