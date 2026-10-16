import copy

import pytest

from helpers import SOLVED
from sudoku_app.model import SudokuModel


def zeros():
    return [[0] * 9 for _ in range(9)]


def puzzle_with_blanks(positions):
    grid = copy.deepcopy(SOLVED)
    for i, j in positions:
        grid[i][j] = 0
    return grid


@pytest.fixture
def model():
    return SudokuModel()


def write_sudoku_file(tmp_path, grid):
    path = tmp_path / "sudoku.txt"
    path.write_text("\n".join("".join(str(n) for n in row) for row in grid),
                    encoding="utf-8")
    return path


class TestInitUndEinlesen:

    def test_init_loest_standard_sudoku(self, model):
        assert len(model.sudoku) == 9
        assert all(len(row) == 9 for row in model.sudoku)
        assert all(1 <= value <= 9 for row in model.sudoku for value in row)
        assert model.is_valid(model.sudoku)

    def test_init_mit_eigener_datei(self, tmp_path):
        path = write_sudoku_file(tmp_path, SOLVED)
        model = SudokuModel(sudoku_file=path)
        assert model.sudoku == SOLVED

    def test_read_sudoku_ignoriert_non_digit_zeichen(self, tmp_path):
        path = tmp_path / "sudoku.txt"
        path.write_text(
            "5, 3, 4, 6, 7, 8, 9, 1, 2\n"
            "6 7 2 1 9 5 3 4 8\n"
            "1.9.8.3.4.2.5.6.7\n"
            "8 5 9 7 6 1 4 2 3\n"
            "4 2 6 8 5 3 7 9 1\n"
            "7 1 3 9 2 4 8 5 6\n"
            "9 6 1 5 3 7 2 8 4\n"
            "2 8 7 4 1 9 6 3 5\n"
            "3 4 5 2 8 6 1 7 9\n",
            encoding="utf-8")
        model = SudokuModel(sudoku_file=path)
        assert model.sudoku == SOLVED

    def test_unsolved_sudoku_bleibt_vor_der_loesung(self, tmp_path):
        puzzle = puzzle_with_blanks([(0, 0), (4, 4)])
        path = write_sudoku_file(tmp_path, puzzle)
        model = SudokuModel(sudoku_file=path)
        assert model.unsolved_sudoku == puzzle
        assert model.sudoku != puzzle
        assert model.sudoku[0][0] != 0


class TestIsValid:

    def test_loesung_ist_valid(self, model):
        assert model.is_valid(SOLVED)

    def test_dublette_in_zeile(self, model):
        grid = copy.deepcopy(SOLVED)
        grid[0][8] = grid[0][0]
        assert not model.is_valid(grid)

    def test_dublette_in_spalte(self, model):
        grid = copy.deepcopy(SOLVED)
        grid[8][0] = grid[0][0]
        assert not model.is_valid(grid)

    def test_dublette_im_block(self, model):
        grid = copy.deepcopy(SOLVED)
        grid[1][1] = grid[0][0]
        assert not model.is_valid(grid)

    def test_nullen_sind_erlaubt(self, model):
        grid = puzzle_with_blanks([(0, 0), (0, 1), (4, 4), (8, 8)])
        assert model.is_valid(grid)


class TestSolver:

    def test_solver_fuellt_leerstellen(self, model):
        puzzle = puzzle_with_blanks([(0, 0), (1, 3), (4, 4), (8, 8)])
        result = model.solve_sudoku(puzzle)
        assert result
        assert puzzle == SOLVED

    def test_solver_ist_fuer_vollstaendiges_grid_eine_noop(self, model):
        grid = copy.deepcopy(SOLVED)
        result = model.solve_sudoku(grid)
        assert result == SOLVED

    def test_solver_gibt_false_bei_konflikt(self, model):
        grid = copy.deepcopy(SOLVED)
        grid[0][1] = grid[0][0]
        grid[8][8] = 0
        assert model.solve_sudoku(grid) is False


class TestGenerator:

    def test_fuell_methode_erzeugt_gueltige_loesung(self, model):
        grid = model.fill_sudoku(zeros())
        assert grid is not None
        assert all(value != 0 for row in grid for value in row)
        assert model.is_valid(grid)

    @pytest.mark.parametrize("difficulty, minimum, maximum", [
        (1, 20, 30),
        (2, 35, 40),
        (3, 45, 50),
    ])
    def test_leerstellen_pro_schwierigkeit(self, model, difficulty, minimum, maximum):
        puzzle = model.create_sudoku(difficulty)
        blanks = sum(row.count(0) for row in puzzle)
        assert minimum <= blanks <= maximum
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

    def test_loesung_ist_komplett_und_valid(self, model):
        model.create_sudoku(1)
        assert all(value != 0 for row in model.sudoku for value in row)
        assert model.is_valid(model.sudoku)

    def test_puzzle_passt_zur_loesung(self, model):
        puzzle = model.create_sudoku(2)
        for i in range(9):
            for j in range(9):
                assert puzzle[i][j] in (0, model.sudoku[i][j])

    def test_neues_setzt_leben_und_tipps_zurueck(self, model):
        model.remove_life()
        model.remove_life()
        model.use_tip()
        model.create_sudoku(1)
        assert model.lives == 3
        assert model.tips == 3

    def test_unbekannte_schwierigkeit_erzeugt_keine_leerstellen(self, model):
        puzzle = model.create_sudoku(99)
        assert sum(row.count(0) for row in puzzle) == 0


class TestLebenUndTipps:

    def test_remove_life_zahlt_herunter(self, model):
        assert model.remove_life() == 2
        assert model.remove_life() == 1
        assert model.lives == 1

    def test_lives_setter(self, model):
        model.lives = 7
        assert model.lives == 7

    def test_tips_setter(self, model):
        model.tips = 1
        assert model.tips == 1

    def test_use_tip_zahlt_herunter(self, model):
        assert model.use_tip() == 2
        assert model.tips == 2

    def test_use_tip_bleibt_bei_null(self, model):
        for _ in range(5):
            remaining = model.use_tip()
        assert remaining == 0
        assert model.tips == 0
