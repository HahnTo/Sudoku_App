class SudokuController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # View kennt Controller
        self.view.set_controller(self)

    def validate_input(self, row, col, number):
        """
        Validiert Benutzereingabe
        Returns: True wenn Eingabe erlaubt, False sonst
        """


    def on_cell_changed(self, row, col, value):
        """Wird aufgerufen, wenn User eine Zahl eingibt"""
        number = int(value) if value else 0

        sudoku = self.model.sudoku
        if sudoku[row][col] == number or number == 0:
            return True
        else:
            lives = self.model.remove_life()
            self.view.loose_life(lives)
            return False