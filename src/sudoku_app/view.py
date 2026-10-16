import random
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from .difficulty import Difficulty

BASE_DIR = Path(__file__).resolve().parent


class SudokuView:
    def __init__(self, root):
        self.root = root

        self.controller = None

        self.setup_window()

        self.current_frame = None


        # Timer-Attribute
        self.time_elapsed = 0
        self.timer_running = False
        self.timer_id = None

        # Labels, Buttons und Bilder laden
        self.heart_icon = tk.PhotoImage(file=str(BASE_DIR / "images" / "Herz.png"))
        self.heart_icon = self.heart_icon.subsample(2, 2)
        self.heart1_label = tk.Label()
        self.heart2_label = tk.Label()
        self.heart3_label = tk.Label()

        self.empty_heart_icon = tk.PhotoImage(file=str(BASE_DIR / "images" / "leeres_Herz.png"))
        self.empty_heart_icon = self.empty_heart_icon.subsample(2, 2)

        self.pause_icon = tk.PhotoImage(file=str(BASE_DIR / "images" / "Pause.png"))
        self.pause_icon = self.pause_icon.subsample(2, 2)

        self.help_icon = tk.PhotoImage(file=str(BASE_DIR / "images" / "Tipps.png"))
        self.help_icon = self.help_icon.subsample(2, 2)

        self.timer_label = tk.Label()

        self.pause_button = tk.Button()

        self.help_button = tk.Button()


        self.entries = []

        # Zustand des pausierten Spiels für "Weiterspielen"
        self.saved_game = None

        # Nach fertigem Setup den Start screen zeigen
        self.show_start_frame()

    def set_controller(self, controller):
        """Controller setzen"""
        self.controller = controller

    def setup_window(self):
        """Fenster Aufbauen"""
        self.root.title("MySudoku")
        self.root.geometry("600x700")
        self.center_window()


    def center_window(self):
        """Das Fenster zentrieren"""
        #Fenstergröße aktualisieren
        self.root.update_idletasks()

        # Bildschirm Größe ermitteln
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Fenster Größe ermitteln
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Position aus den gefundenen Werten berechnen
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        # Position vom Fenster festlegen
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def show_start_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.stop_timer()

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.current_frame = tk.Frame(self.root)
        self.current_frame.grid(column=0, row=0, sticky="nsew")

        self.current_frame.rowconfigure(0, weight=1)
        for row in range(1, 5):
            self.current_frame.rowconfigure(row, weight=0)
        self.current_frame.rowconfigure(5, weight=1)

        self.current_frame.columnconfigure(0, weight=1)
        self.current_frame.columnconfigure(1, weight=0)
        self.current_frame.columnconfigure(2, weight=1)

        sudoku_label = tk.Label(self.current_frame,
                 text="Sudoku",
                 font=("Arial",40))

        sudoku_label.grid(column=1, row=0, pady=20)  # Abstand oben und unten

        button_row = 1
        if self.saved_game:
            tk.Button(self.current_frame, text="Weiterspielen", width=12,
                      command=self.resume_game).grid(column=1, row=button_row, pady=10)
            button_row += 1

        for difficulty in Difficulty:
            tk.Button(self.current_frame, text=difficulty.label, width=12,
                      command=lambda d=difficulty: self.show_game_frame(difficulty=d)
                      ).grid(column=1, row=button_row, pady=10)
            button_row += 1

    def show_game_frame(self, difficulty):
        # Ein neues Spiel verwirft den alten Spielstand
        self.stop_timer()
        self.saved_game = None
        self.time_elapsed = 0

        self.build_game_frame()
        self.set_grid_values(difficulty)
        self.update_help_button()
        self.update_hearts(self.controller.get_lives())
        self.start_timer()

    def resume_game(self):
        """Gespeichertes Spiel fortsetzen"""
        if not self.saved_game:
            return

        saved = self.saved_game

        self.build_game_frame()

        for i in range(9):
            for j in range(9):
                entry = self.entries[i][j]
                entry.delete(0, tk.END)
                entry.insert(0, saved["values"][i][j])

                if saved["given"][i][j]:
                    entry.config(bg="lightgrey", state="readonly")
                else:
                    entry.config(bg="white", state="normal")

        self.time_elapsed = saved["time_elapsed"]
        self.timer_label.config(text=self.format_time(self.time_elapsed))

        self.controller.set_lives(saved["lives"])
        self.controller.set_tips(saved["tips"])
        self.update_hearts(saved["lives"])
        self.update_help_button()

        self.start_timer()

    def build_game_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        # Alte Einträge zeigen auf das zerstörte Frame
        self.entries = []

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        menu_frame = tk.Frame(self.current_frame)
        menu_frame.pack(fill="x")

        grid_frame = tk.Frame(self.current_frame)
        grid_frame.place(anchor="center", relx=.5, rely=.5)


        menu_frame.columnconfigure(0, weight=0)    # Timer
        menu_frame.columnconfigure(1, weight=1)    # Leerer Platz
        menu_frame.columnconfigure(2, weight=0)    # Herzen
        menu_frame.columnconfigure(3, weight=0)    # Herzen
        menu_frame.columnconfigure(4, weight=0)    # Herzen
        menu_frame.columnconfigure(5, weight=1)    # Leerer Platz
        menu_frame.columnconfigure(6, weight=0)    # Pause Button
        menu_frame.columnconfigure(7, weight=0)    # Hilfe Button

        self.timer_label = tk.Label(menu_frame,
                                    text="00:00:00",
                                    font=("Arial", 16),
                                    background="light grey",
                                    foreground="red")
        self.timer_label.grid(row=0, column=0, sticky="w", padx=10)

        self.heart1_label = tk.Label(menu_frame, image=self.heart_icon)
        self.heart1_label.grid(row=0, column=2, sticky="", padx=10)

        self.heart2_label = tk.Label(menu_frame, image=self.heart_icon)
        self.heart2_label.grid(row=0, column=3, sticky="", padx=10)

        self.heart3_label = tk.Label(menu_frame, image=self.heart_icon)
        self.heart3_label.grid(row=0, column=4, sticky="", padx=10)


        self.pause_button = tk.Button(menu_frame,
                                      image=self.pause_icon,
                                      command=self.on_pause_clicked)
        self.pause_button.grid(row=0, column=6, sticky="e", padx=10)

        self.help_button = tk.Button(menu_frame, image=self.help_icon,
                                     command=self.on_help_clicked)
        self.help_button.grid(row=0, column=7, sticky="e", padx=10)



        vcmd = (self.root.register(self.validate_entry), '%P')
        # Grid erstellen
        for row in range(9):
            row_entries = []
            for col in range(9):
                padx_left = 10 if col % 3 == 0 else 2
                pady_top = 10 if row % 3 == 0 else 2

                entry = tk.Entry(grid_frame,
                                 width=2,
                                 font=("Arial", 24, "bold"),
                                 justify="center",
                                 validate="key",
                                 validatecommand=vcmd,
                                 cursor="dot")
                entry.grid(row=row, column=col,
                           padx=(padx_left, 1),
                           pady=(pady_top, 1))

                entry.bind('<KeyRelease>', self.on_cell_change(row, col))

                row_entries.append(entry)


            self.entries.append(row_entries)

    def on_cell_change(self, row, col):
        """Callback wenn Zelle geändert wird"""

        def callback(event):
            entry = event.widget

            if not self.controller.on_cell_changed(row, col, entry.get()):
                entry.config(bg="red")
                self.show_fail()
                entry.delete(0, tk.END)
                entry.insert(0, "")
                entry.config(bg="white")

                if self.controller.get_lives() <= 0:
                    self.game_over()
                return

            entry.config(bg="white")

            if self.check_all_filled():
                self.game_won()

        return callback

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False

            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

    def update_timer(self):
        if self.timer_running:
            self.time_elapsed += 1

            self.timer_label.config(text=self.format_time(self.time_elapsed))

            self.timer_id = self.root.after(1000, self.update_timer)

    def format_time(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def on_pause_clicked(self):
        """Timer anhalten und Pause-Dialog öffnen"""
        self.stop_timer()
        self.show_pause_dialog()

    def show_pause_dialog(self):
        """Mini-Dialog: weiterspielen oder zurück zum Menü"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Pause")
        dialog.resizable(False, False)
        dialog.transient(self.root)

        tk.Label(dialog, text="Das Spiel ist pausiert.",
                 font=("Arial", 14)).pack(padx=30, pady=(20, 10))

        button_frame = tk.Frame(dialog)
        button_frame.pack(padx=30, pady=(0, 20))

        def continue_game():
            dialog.destroy()
            self.start_timer()

        def back_to_menu():
            self.save_game()
            dialog.destroy()
            self.show_start_frame()

        tk.Button(button_frame, text="Weiterspielen", width=14,
                  command=continue_game).pack(side="left", padx=5)
        tk.Button(button_frame, text="Zurück zum Menü", width=16,
                  command=back_to_menu).pack(side="left", padx=5)

        # Schließen über das X zählt als Weiterspielen
        dialog.protocol("WM_DELETE_WINDOW", continue_game)

        self.center_dialog(dialog)
        dialog.wait_visibility()
        dialog.grab_set()
        dialog.focus_set()

    def center_dialog(self, dialog):
        """Dialog in der Mitte des Hauptfensters positionieren"""
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

    def save_game(self):
        """Spielstand sichern, damit er fortgesetzt werden kann"""
        values = [[entry.get() for entry in row] for row in self.entries]
        given = [[str(entry.cget("state")) == "readonly" for entry in row]
                 for row in self.entries]

        self.saved_game = {
            "values": values,
            "given": given,
            "lives": self.controller.get_lives(),
            "tips": self.controller.get_tips(),
            "time_elapsed": self.time_elapsed,
        }

    def on_help_clicked(self):
        """Tipp: ein zufälliges leeres Feld mit der Lösung füllen"""
        empty_cells = [(i, j) for i in range(9) for j in range(9)
                       if self.entries[i][j].get() == ""]

        if not empty_cells or self.controller.get_tips() <= 0:
            return

        i, j = random.choice(empty_cells)
        self.controller.use_tip()

        entry = self.entries[i][j]
        entry.insert(0, str(self.controller.get_cell_value(i, j)))
        entry.config(bg="lightgrey", state="readonly")

        self.update_help_button()

        if self.check_all_filled():
            self.game_won()

    def update_help_button(self):
        """Hilfe-Button deaktivieren, wenn keine Tipps mehr übrig sind"""
        if self.controller.get_tips() > 0:
            self.help_button.config(state="normal")
        else:
            self.help_button.config(state="disabled")

    def validate_entry(self, new_value):
        """Erlaubt nur 1 Zeichen (0-9 oder leer)"""
        # Leer erlauben (zum Löschen)
        if new_value == "":
            return True

        # Nur 1 Ziffer von 1-9 erlauben
        if len(new_value) == 1 and new_value in "123456789":
            return True

        return False


    def set_grid_values(self, difficulty):
        sudoku = self.controller.get_new_sudoku(difficulty)
        if sudoku is None:
            tk.messagebox.showerror("Fehler", "Die Erstellung eines neuen Sudokus ist leider fehlgeschlagen.\nJetzt wird das gespeicherte geladen.")
            sudoku = self.controller.get_unsolved_sudoku()

        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)

                if sudoku[i][j] != 0:
                    self.entries[i][j].insert(0, str(sudoku[i][j]))
                    self.entries[i][j].config(bg="lightgrey",
                                              state="readonly")
                else:
                    self.entries[i][j].insert(0, "")

    def loose_life(self, lives):
        self.update_hearts(lives)

    def update_hearts(self, lives):
        """Herzen je nach verbliebener Lebenanzahl setzen"""
        heart_labels = [self.heart1_label, self.heart2_label, self.heart3_label]
        for index, heart_label in enumerate(heart_labels):
            if index < 3 - lives:
                heart_label.config(image=self.empty_heart_icon)
            else:
                heart_label.config(image=self.heart_icon)

    def check_all_filled(self):
        """Prüft ob alle Felder ausgefüllt sind"""
        for row in self.entries:
            for entry in row:
                if entry.get() == "":
                    return False
        return True

    def show_fail(self):
        tk.messagebox.showerror("Falsch", "Das war leider die falsche Zahl...")

    def show_loose(self):
        tk.messagebox.showerror("Verloren!", "Du hast leider alle Leben verloren")

    def show_win(self):
        tk.messagebox.showinfo("Gewonnen!", "Du hast das Sudoku gelöst! Herzlichen Glückwunsch")

    def game_won(self):
        """Gewonnen: Meldung anzeigen und zurück ins Menü"""
        self.stop_timer()
        self.saved_game = None
        self.show_win()
        self.show_start_frame()

    def game_over(self):
        """Verloren: Meldung anzeigen und zurück ins Menü"""
        self.stop_timer()
        self.saved_game = None
        self.show_loose()
        self.show_start_frame()
