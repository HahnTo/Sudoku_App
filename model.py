import copy
import random
from re import fullmatch


class SudokuModel:

    def __init__(self):
        self._sudoku = []
        self.read_sudoku('sudoku.txt')

        self._lives = 3

        # Unsolved Sudoku für die Ausgabe in der GUI, _sudoku ist die "Lösung"
        self._unsolved_sudoku = copy.deepcopy(self._sudoku)

        # solang es nicht None ist, ist es gelöst
        if not self.solve_sudoku(self._sudoku) is None:
            self.print_sudoku(self._sudoku)



    def read_sudoku(self, file):
        sudoku_file =  open(file, 'r')
        sudoku = []
        for zeile in sudoku_file:
            row = []
            for number in zeile:
                if number.isdigit():
                    row.append(int(number))
            sudoku.append(row)
        self._sudoku = sudoku

    def print_sudoku(self, sudoku):
        for i in range(9):
            if i % 3 == 0:
                print("+-------+-------+-------+")
            for j in range(9):
                if j % 3 == 0:
                    print("|", end=" ")
                value = sudoku[i][j]
                print(value, end=" ")
            print("|")
        print("+-------+-------+-------+")

    def is_valid(self, sudoku):
        for i in range(9):
            for j in range(9):
                number_found = sudoku[i][j]
                if number_found != 0:
                    for k in range(9):
                        if (sudoku[i][k] == number_found and k != j) or (sudoku[k][j] == number_found and k != i):
                            return False

        for big_row in range(0, 9, 3):
            for big_col in range(0, 9, 3):
                for row in range(3):
                    for col in range(3):
                        number_found = sudoku[big_row + row][big_col + col]
                        if number_found != 0:
                            # Prüfe alle Zellen im Block auf Duplikate
                            for row_test in range(3):
                                for col_test in range(3):
                                    if (row_test != row or col_test != col) and \
                                            sudoku[big_row + row_test][big_col + col_test] == number_found:
                                        return False
        return True

    def solve_sudoku(self, sudoku):
        for i in range(9):
            for j in range(9):
                if sudoku[i][j] == 0:
                    for num in range(1, 10):
                        sudoku[i][j] = num
                        if self.is_valid(sudoku) and self.solve_sudoku(sudoku):
                            return True
                        sudoku[i][j] = 0
                    return False
        return sudoku


    def remove_life(self):
        self._lives -= 1
        return self._lives

    # Leicht: zwischen 20 und 30
    # Mittel: zwischen 35 und 40
    # Schwer: zwischen 45 und 50
    def create_sudoku(self, difficulty):
        new_sudoku = [[0 for _ in range(9)]for _ in range(9)]
        number_of_blank_fields = 0

        match difficulty:
            case 1:
                number_of_blank_fields = random.randint(20, 30)
            case 2:
                number_of_blank_fields = random.randint(35, 40)
            case 3:
                number_of_blank_fields = random.randint(45, 50)

        print(f"leere Felder:{number_of_blank_fields}")
        full_sudoku = self.fill_sudoku(new_sudoku)

        if full_sudoku is None:
            return None

        self._sudoku = full_sudoku
        self.print_sudoku(full_sudoku)

        finished_sudoku = self.remove_numbers(copy.deepcopy(full_sudoku), number_of_blank_fields)

        return finished_sudoku


    def fill_sudoku(self, new_sudoku):

        # Versuche in allen Kästchen random Zahlen. wenn eine Zahl nicht funktioniert, ist sie durch pop nicht mehr in numbers enthalten
        # und kann somit auch nicht doppelt überprüft werden
        for i in range(9):
            for j in range(9):
                # Wenn das Feld noch leer ist, wird getestet.
                numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
                if new_sudoku[i][j] == 0:
                    for _ in range(9):
                        random.shuffle(numbers)
                        new_sudoku[i][j] = numbers.pop(0)

                        if self.is_valid(new_sudoku) and self.fill_sudoku(new_sudoku):
                            return new_sudoku
                        new_sudoku[i][j] = 0
                    return None

        return new_sudoku

    def remove_numbers(self, sudoku, number_of_blank_fields):
        # numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        for _ in range(number_of_blank_fields):
            # random.shuffle(numbers)
            # i = numbers[0]
            # random.shuffle(numbers)
            # j = numbers[0]

            i = random.randint(0, 8)
            j = random.randint(0, 8)

            while sudoku[i][j] == 0:
                i = random.randint(0, 8)
                j = random.randint(0, 8)

            sudoku[i][j] = 0
        return sudoku

    @property
    def lives(self):
        return self.lives

    @property
    def unsolved_sudoku(self):
        return self._unsolved_sudoku

    @property
    def sudoku(self):
        return self._sudoku
