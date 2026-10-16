import copy

import pytest

from helpers import (SOLVED, button_by_text, button_texts, dialogs_of,
                     find_empty_cell, grid_values, press_key)
from sudoku_app.difficulty import Difficulty


def wrong_value(correct):
    return str(correct % 9 + 1)


def start_game(app, difficulty=Difficulty.EASY):
    app.view.show_game_frame(difficulty)
    app.root.update()


def pause_to_menu(app):
    app.view.on_pause_clicked()
    app.root.update()
    button_by_text(dialogs_of(app.root)[0], "Zurück zum Menü").invoke()
    app.root.update()


def fill_all_but_last(app):
    empties = [(i, j) for i in range(9) for j in range(9)
               if app.view.entries[i][j].get() == ""]
    for i, j in empties[:-1]:
        app.view.entries[i][j].insert(0, str(app.model.sudoku[i][j]))
    app.root.update()
    return empties[-1]


class TestStartFrame:

    def test_schwierigkeits_buttons(self, app):
        texts = button_texts(app.view.current_frame)
        assert "Leicht" in texts
        assert "Mittel" in texts
        assert "Schwer" in texts

    def test_kein_weiterspielen_ohne_spielstand(self, app):
        assert "Weiterspielen" not in button_texts(app.view.current_frame)

    def test_weiterspielen_mit_spielstand(self, app):
        app.view.saved_game = {"values": [[""] * 9] * 9,
                               "given": [[False] * 9] * 9,
                               "lives": 3, "tips": 3, "time_elapsed": 0}
        app.view.show_start_frame()
        app.root.update()
        assert "Weiterspielen" in button_texts(app.view.current_frame)

    @pytest.mark.parametrize("text", ["Leicht", "Mittel", "Schwer"])
    def test_buttons_starten_ein_spiel(self, app, text):
        app.view.show_start_frame()
        app.root.update()
        button_by_text(app.view.current_frame, text).invoke()
        app.root.update()
        assert app.view.timer_running
        assert len(app.view.entries) == 9

    def test_fenster_titel(self, app):
        assert app.root.title() == "MySudoku"


class TestGameFrame:

    def test_grid_und_timer(self, app):
        start_game(app)
        assert len(app.view.entries) == 9
        assert all(len(row) == 9 for row in app.view.entries)
        assert app.view.timer_running
        assert app.view.time_elapsed == 1

    def test_vorgegebene_zellen_sind_readonly(self, app):
        start_game(app)
        for i in range(9):
            for j in range(9):
                entry = app.view.entries[i][j]
                if str(entry.cget("state")) == "readonly":
                    assert entry.get() == str(app.model.sudoku[i][j])
                else:
                    assert entry.get() == ""

    def test_pause_und_hilfe_button_existieren(self, app):
        start_game(app)
        assert app.view.pause_button.winfo_exists()
        assert app.view.help_button.cget("command") != ""

    def test_neues_spiel_haelt_keine_alten_eintraege(self, app):
        start_game(app)
        start_game(app)
        assert len(app.view.entries) == 9
        assert all(len(row) == 9 for row in app.view.entries)

    def test_neues_spiel_setzt_alles_zurueck(self, app):
        start_game(app)
        app.model.remove_life()
        app.model.use_tip()
        app.view.time_elapsed = 999
        start_game(app)
        assert app.model.lives == 3
        assert app.model.tips == 3
        assert app.view.time_elapsed == 1

    def test_spielstand_wird_bei_neuem_spiel_verworfen(self, app):
        start_game(app)
        pause_to_menu(app)
        assert app.view.saved_game is not None
        button_by_text(app.view.current_frame, "Leicht").invoke()
        app.root.update()
        assert app.view.saved_game is None


class TestTimer:

    def test_stop_und_start(self, app):
        start_game(app)
        app.view.stop_timer()
        assert not app.view.timer_running
        assert app.view.timer_id is None
        app.view.start_timer()
        assert app.view.timer_running

    def test_update_timer_tickt(self, app):
        start_game(app)
        app.view.stop_timer()
        app.view.timer_running = True
        app.view.time_elapsed = 40
        app.view.update_timer()
        assert app.view.time_elapsed == 41
        assert app.view.timer_label.cget("text") == "00:00:41"
        app.view.stop_timer()

    @pytest.mark.parametrize("seconds, expected", [
        (0, "00:00:00"),
        (59, "00:00:59"),
        (60, "00:01:00"),
        (3661, "01:01:01"),
    ])
    def test_format_time(self, app, seconds, expected):
        assert app.view.format_time(seconds) == expected


class TestPauseDialog:

    def test_pause_stoppt_timer_und_oeffnet_dialog(self, app):
        start_game(app)
        app.view.on_pause_clicked()
        app.root.update()
        assert not app.view.timer_running
        assert len(dialogs_of(app.root)) == 1

    def test_dialog_ist_modal(self, app):
        start_game(app)
        app.view.on_pause_clicked()
        app.root.update()
        dialog = dialogs_of(app.root)[0]
        assert str(dialog.grab_current()) == str(dialog)

    def test_dialog_sitzt_in_fenstermitte(self, app):
        start_game(app)
        app.view.on_pause_clicked()
        app.root.update()
        dialog = dialogs_of(app.root)[0]
        root_left = app.root.winfo_x()
        root_right = root_left + app.root.winfo_width()
        assert root_left <= dialog.winfo_x() <= root_right

    def test_weiterspielen_setzt_timer_fort(self, app):
        start_game(app)
        app.view.on_pause_clicked()
        app.root.update()
        button_by_text(dialogs_of(app.root)[0], "Weiterspielen").invoke()
        app.root.update()
        assert not dialogs_of(app.root)
        assert app.view.timer_running
        assert app.view.saved_game is None

    def test_dialog_schliessen_zaelt_als_weiterspielen(self, app):
        start_game(app)
        app.view.on_pause_clicked()
        app.root.update()
        dialog = dialogs_of(app.root)[0]
        command = dialog.protocol("WM_DELETE_WINDOW")
        dialog.tk.call(command)
        app.root.update()
        assert not dialogs_of(app.root)
        assert app.view.timer_running

    def test_zurueck_zum_menu_speichert_spielstand(self, app):
        start_game(app)
        i, j = find_empty_cell(app.view)
        app.view.entries[i][j].insert(0, "5")
        app.model.lives = 2
        app.model.tips = 1
        app.view.time_elapsed = 77

        pause_to_menu(app)

        saved = app.view.saved_game
        assert saved["values"][i][j] == "5"
        assert saved["lives"] == 2
        assert saved["tips"] == 1
        assert saved["time_elapsed"] == 77
        assert not app.view.timer_running
        assert "Weiterspielen" in button_texts(app.view.current_frame)


class TestWeiterspielen:

    def test_stellt_felder_leben_tipps_und_zeit_wieder_her(self, app):
        start_game(app)
        i, j = find_empty_cell(app.view)
        app.view.entries[i][j].insert(0, "7")
        app.view.help_button.invoke()
        app.model.lives = 1
        app.view.time_elapsed = 55

        pause_to_menu(app)
        button_by_text(app.view.current_frame, "Weiterspielen").invoke()
        app.root.update()

        assert app.view.timer_running
        assert app.view.entries[i][j].get() == "7"
        assert app.model.lives == 1
        assert app.model.tips == 2
        assert app.view.time_elapsed >= 55
        assert app.view.timer_label.cget("text") == app.view.format_time(app.view.time_elapsed)
        assert str(app.view.heart1_label.cget("image")) == str(app.view.empty_heart_icon)
        assert str(app.view.help_button.cget("state")) == "normal"

    def test_verbrauchte_tipps_bleiben_verbraucht(self, app):
        start_game(app)
        for _ in range(3):
            app.view.help_button.invoke()
        app.root.update()
        pause_to_menu(app)
        button_by_text(app.view.current_frame, "Weiterspielen").invoke()
        app.root.update()
        assert app.model.tips == 0
        assert str(app.view.help_button.cget("state")) == "disabled"

    def test_vorgegebene_zellen_bleiben_readonly(self, app):
        start_game(app)
        given = next((i, j) for i in range(9) for j in range(9)
                     if str(app.view.entries[i][j].cget("state")) == "readonly")
        value = app.view.entries[given[0]][given[1]].get()

        pause_to_menu(app)
        button_by_text(app.view.current_frame, "Weiterspielen").invoke()
        app.root.update()

        entry = app.view.entries[given[0]][given[1]]
        assert str(entry.cget("state")) == "readonly"
        assert entry.get() == value


class TestZellEingabe:

    def test_falsche_zahl_wird_geleert(self, app):
        start_game(app)
        i, j = find_empty_cell(app.view)
        wrong = wrong_value(app.model.sudoku[i][j])
        app.view.entries[i][j].insert(0, wrong)
        press_key(app.view.entries[i][j], app.root)

        assert app.messages == ["fail"]
        assert app.view.entries[i][j].get() == ""
        assert app.model.lives == 2

    def test_korrekte_zahl_bleibt_stehen(self, app):
        start_game(app)
        i, j = find_empty_cell(app.view)
        correct = str(app.model.sudoku[i][j])
        app.view.entries[i][j].insert(0, correct)
        press_key(app.view.entries[i][j], app.root)

        assert app.messages == []
        assert app.view.entries[i][j].get() == correct
        assert app.model.lives == 3

    def test_leeres_feld_gibt_keine_strafe(self, app):
        start_game(app)
        i, j = find_empty_cell(app.view)
        press_key(app.view.entries[i][j], app.root)

        assert app.messages == []
        assert app.model.lives == 3


class TestHerzen:

    @pytest.mark.parametrize("lives, leere_herzen", [(3, 0), (2, 1), (1, 2), (0, 3)])
    def test_update_hearts(self, app, lives, leere_herzen):
        start_game(app)
        app.view.update_hearts(lives)
        labels = [app.view.heart1_label, app.view.heart2_label, app.view.heart3_label]
        empty = sum(1 for label in labels
                    if str(label.cget("image")) == str(app.view.empty_heart_icon))
        assert empty == leere_herzen

    def test_loose_life_aktualisiert_herzen(self, app):
        start_game(app)
        app.view.loose_life(2)
        assert str(app.view.heart1_label.cget("image")) == str(app.view.empty_heart_icon)
        assert str(app.view.heart2_label.cget("image")) == str(app.view.heart_icon)

    def test_neues_spiel_zeigt_wieder_drei_herzen(self, app):
        start_game(app)
        app.view.loose_life(1)
        start_game(app)
        assert str(app.view.heart1_label.cget("image")) == str(app.view.heart_icon)
        assert str(app.view.heart2_label.cget("image")) == str(app.view.heart_icon)


class TestCheckAllFilled:

    def test_leeres_feld_verhindert_sieg(self, app):
        start_game(app)
        assert not app.view.check_all_filled()

    def test_alle_gefuellt(self, app):
        start_game(app)
        for i in range(9):
            for j in range(9):
                app.view.entries[i][j].insert(0, "1")
        assert app.view.check_all_filled()


class TestSpielEnde:

    def test_gewonnen_fuehrt_zurueck_ins_menu(self, app):
        start_game(app)
        last = fill_all_but_last(app)
        i, j = last
        app.view.entries[i][j].insert(0, str(app.model.sudoku[i][j]))
        press_key(app.view.entries[i][j], app.root)

        assert app.messages == ["win"]
        assert app.view.saved_game is None
        assert not app.view.timer_running
        assert "Weiterspielen" not in button_texts(app.view.current_frame)
        assert "Leicht" in button_texts(app.view.current_frame)

    def test_verloren_fuehrt_zurueck_ins_menu(self, app):
        start_game(app)
        app.model.lives = 1
        i, j = find_empty_cell(app.view)
        wrong = wrong_value(app.model.sudoku[i][j])
        app.view.entries[i][j].insert(0, wrong)
        press_key(app.view.entries[i][j], app.root)

        assert app.messages == ["fail", "loose"]
        assert app.view.saved_game is None
        assert not app.view.timer_running
        assert "Weiterspielen" not in button_texts(app.view.current_frame)


class TestTipp:

    def test_tipp_fuellt_korrekte_zelle(self, app):
        start_game(app)
        before = grid_values(app.view)
        app.view.help_button.invoke()
        app.root.update()

        assert app.model.tips == 2
        changed = [cell for cell, value in grid_values(app.view).items()
                   if value != before[cell]]
        assert len(changed) == 1
        i, j = changed[0]
        entry = app.view.entries[i][j]
        assert entry.get() == str(app.model.sudoku[i][j])
        assert str(entry.cget("state")) == "readonly"

    def test_button_sperrt_sich_bei_null_tipps(self, app):
        start_game(app)
        for _ in range(3):
            app.view.help_button.invoke()
        app.root.update()
        assert app.model.tips == 0
        assert str(app.view.help_button.cget("state")) == "disabled"

    def test_tipp_auf_letztes_feld_gewinnt(self, app):
        start_game(app)
        fill_all_but_last(app)
        app.view.help_button.invoke()
        app.root.update()

        assert app.messages == ["win"]
        assert app.view.saved_game is None
        assert "Weiterspielen" not in button_texts(app.view.current_frame)


class TestFallback:

    def test_fehlerhafte_generierung_laedt_gespeichertes_sudoku(self, app, monkeypatch):
        start_game(app)

        fallback = copy.deepcopy(SOLVED)
        fallback[0][0] = 0
        monkeypatch.setattr(app.controller, "get_new_sudoku", lambda difficulty: None)
        monkeypatch.setattr(app.controller, "get_unsolved_sudoku", lambda: fallback)

        app.view.show_game_frame(Difficulty.EASY)
        app.root.update()

        assert "error" in app.messages
        assert app.view.entries[0][0].get() == ""
        assert str(app.view.entries[0][0].cget("state")) == "normal"
        assert app.view.entries[0][1].get() == str(fallback[0][1])
        assert str(app.view.entries[0][1].cget("state")) == "readonly"
