class SudokuController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # View kennt Controller
        self.view.set_controller(self)


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

    def get_unsolved_sudoku(self):
        return self.model.unsolved_sudoku

    def get_new_sudoku(self, difficulty):
        return self.model.create_sudoku(difficulty)

    def get_lives(self):
        return self.model.lives

    def set_lives(self, lives):
        self.model.lives = lives

    def get_tips(self):
        return self.model.tips

    def set_tips(self, tips):
        self.model.tips = tips

    def use_tip(self):
        return self.model.use_tip()

    def get_cell_value(self, row, col):
        return self.model.sudoku[row][col]