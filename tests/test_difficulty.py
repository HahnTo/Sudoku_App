from sudoku_app.difficulty import Difficulty


def test_labels_passen_zum_menu():
    assert [difficulty.label for difficulty in Difficulty] == ["Leicht", "Mittel", "Schwer"]


def test_bereiche_sind_aufsteigend_und_gueltig():
    ranges = [(difficulty.min_blanks, difficulty.max_blanks) for difficulty in Difficulty]
    assert ranges == sorted(ranges)
    assert all(minimum <= maximum for minimum, maximum in ranges)


def test_mitglieder_sind_nach_schwierigkeit_geordnet():
    assert list(Difficulty) == [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
