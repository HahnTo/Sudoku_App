import pytest

from sudoku_app.controller import SudokuController
from sudoku_app.model import SudokuModel


class FakeView:
    def __init__(self):
        self.controller = None
        self.loose_life_calls = []

    def set_controller(self, controller):
        self.controller = controller

    def loose_life(self, lives):
        self.loose_life_calls.append(lives)


def wrong_value(correct):
    return str(correct % 9 + 1)


@pytest.fixture
def setup():
    model = SudokuModel()
    view = FakeView()
    controller = SudokuController(model, view)
    return controller, model, view


class TestVerdrahtung:

    def test_controller_registriert_sich_beim_view(self, setup):
        controller, model, view = setup
        assert view.controller is controller

    def test_model_ist_verbunden(self, setup):
        controller, model, view = setup
        assert controller.model is model


class TestZelleingabe:

    def test_korrekte_zahl_laesst_leben_und_meldung_ersparen(self, setup):
        controller, model, view = setup
        value = str(model.sudoku[0][0])
        assert controller.on_cell_changed(0, 0, value) is True
        assert model.lives == 3
        assert view.loose_life_calls == []

    def test_falsche_zahl_kostet_ein_leben(self, setup):
        controller, model, view = setup
        wrong = wrong_value(model.sudoku[0][0])
        assert controller.on_cell_changed(0, 0, wrong) is False
        assert model.lives == 2
        assert view.loose_life_calls == [2]

    def test_leeres_feld_und_null_sind_neutral(self, setup):
        controller, model, view = setup
        assert controller.on_cell_changed(0, 0, "") is True
        assert controller.on_cell_changed(0, 0, "0") is True
        assert model.lives == 3
        assert view.loose_life_calls == []

    def test_drei_falsche_zahlen_verlieren_das_spiel(self, setup):
        controller, model, view = setup
        wrong = wrong_value(model.sudoku[0][0])
        for _ in range(3):
            controller.on_cell_changed(0, 0, wrong)
        assert model.lives == 0
        assert view.loose_life_calls == [2, 1, 0]


class TestZugriffe:

    def test_get_set_lives(self, setup):
        controller, model, view = setup
        controller.set_lives(1)
        assert controller.get_lives() == 1

    def test_get_set_tips(self, setup):
        controller, model, view = setup
        controller.set_tips(2)
        assert controller.get_tips() == 2

    def test_use_tip(self, setup):
        controller, model, view = setup
        assert controller.use_tip() == 2
        assert controller.get_tips() == 2

    def test_get_cell_value(self, setup):
        controller, model, view = setup
        for i in range(9):
            for j in range(9):
                assert controller.get_cell_value(i, j) == model.sudoku[i][j]

    def test_get_unsolved_sudoku(self, setup):
        controller, model, view = setup
        assert controller.get_unsolved_sudoku() is model.unsolved_sudoku

    def test_get_new_sudoku(self, setup):
        controller, model, view = setup
        puzzle = controller.get_new_sudoku(1)
        assert 20 <= sum(row.count(0) for row in puzzle) <= 30
        assert all(value != 0 for row in model.sudoku for value in row)
