import copy


class SudokuModel:

    def __init__(self):
        self._sudoku = []
        self.read_sudoku('sudoku.txt')

        self._lives = 3

        # Unsolved Sudoku für die Ausgabe in der GUI, _sudoku ist die "Lösung"
        self._unsolved_sudoku = copy.deepcopy(self._sudoku)

        if self.solve_sudoku():
            self.print_sudoku()



    def read_sudoku(self, file):
        sudoku_file =  open(file, 'r')
        for zeile in sudoku_file:
            row = []
            for number in zeile:
                if number.isdigit():
                    row.append(int(number))
            self._sudoku.append(row)

    def print_sudoku(self):
        for i in range(9):
            if i % 3 == 0:
                print("+-------+-------+-------+")
            for j in range(9):
                if j % 3 == 0:
                    print("|", end=" ")
                value = self._sudoku[i][j]
                print(value, end=" ")
            print("|")
        print("+-------+-------+-------+")

    def is_valid(self):
        for i in range(9):
            for j in range(9):
                number_found = self._sudoku[i][j]
                if number_found != 0:
                    for k in range(9):
                        if (self._sudoku[i][k] == number_found and k != j) or (self._sudoku[k][j] == number_found and k != i):
                            return False

        for big_row in range(0, 9, 3):
            for big_col in range(0, 9, 3):
                for row in range(3):
                    for col in range(3):
                        number_found = self._sudoku[big_row + row][big_col + col]
                        if number_found != 0:
                            # Prüfe alle Zellen im Block auf Duplikate
                            for row_test in range(3):
                                for col_test in range(3):
                                    if (row_test != row or col_test != col) and \
                                            self._sudoku[big_row + row_test][big_col + col_test] == number_found:
                                        return False
        return True

    def solve_sudoku(self):
        for i in range(9):
            for j in range(9):
                if self._sudoku[i][j] == 0:
                    for num in range(1, 10):
                        self._sudoku[i][j] = num
                        if self.is_valid() and self.solve_sudoku():
                            return True
                        self._sudoku[i][j] = 0
                    return False
        return True

    def remove_life(self):
        self._lives -= 1
        return self._lives

    @property
    def lives(self):
        return self.lives

    @property
    def unsolved_sudoku(self):
        return self._unsolved_sudoku

    @property
    def sudoku(self):
        return self._sudoku