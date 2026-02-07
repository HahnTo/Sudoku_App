# TODO: - Wenn Pause, dann einen Dialog schalten
#       - Startfenster um Spiel zu starten
#       - Sudoku Generator bauen mit unterschiedlichen Stufen
#       - Button um es direkt zu lösen, für Tests

import tkinter as tk
from tkinter import messagebox


class SudokuView:
    def __init__(self, root):
        self.root = root
        self.controller = None

        self.setup_window()

        self.current_frame = None

        # Alle Attribute für Start Frame



        # Alle Attribute für Game Frame

        # Timer-Attribute
        self.time_elapsed = 0
        self.timer_running = False
        self.timer_id = None

        self.heart_icon = tk.PhotoImage(file="images/Herz.png")
        self.heart_icon = self.heart_icon.subsample(2, 2)
        self.heart1_label = tk.Label()
        self.heart2_label = tk.Label()
        self.heart3_label = tk.Label()

        self.empty_heart_icon = tk.PhotoImage(file="images/leeres_Herz.png")
        self.empty_heart_icon = self.empty_heart_icon.subsample(2, 2)

        # Buttons mit zugehörigen Icons
        self.start_icon = tk.PhotoImage(file="images/Start.png")
        self.start_icon = self.start_icon.subsample(2, 2)
        self.pause_icon = tk.PhotoImage(file="images/Pause.png")
        self.pause_icon = self.pause_icon.subsample(2, 2)

        self.pause_button = tk.Button()

        # Timer Label
        self.timer_label = tk.Label()


        self.help_icon = tk.PhotoImage(file="images/Tipps.png")
        self.help_icon = self.help_icon.subsample(2, 2)

        self.help_button = tk.Button()


        self.entries = []

        self.show_start_frame()
        #self.show_game_frame()

    def set_controller(self, controller):
        """Controller setzen"""
        self.controller = controller

    def setup_window(self):
        """Fenster Aufbauen"""
        self.root.title("Sudoku App")
        self.root.geometry("600x700")
        self.center_window()


    def center_window(self):
        #Fenstergröße aktualisieren
        self.root.update_idletasks()

        # Bildschirm Größe ermitteln
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Fenster Größe ermitteln
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()

        # Position berechnen aus den gefundenen Werten
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        # Position vom Fenster festlegen
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    def show_start_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        tk.Label(self.current_frame, text="Test").pack()
        tk.Button(self.current_frame, text="switch frame",
                  command=self.show_game_frame).pack()

    def show_game_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        menu_frame = tk.Frame(self.current_frame)
        menu_frame.pack(fill="x")

        grid_frame = tk.Frame(self.current_frame)
        grid_frame.place(anchor="c", relx=.5, rely=.5)


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
                                      command=self.toggle_pause)
        self.pause_button.grid(row=0, column=6, sticky="e", padx=10)

        self.help_button = tk.Button(menu_frame, image=self.help_icon)
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
        self.set_grid_values()
        self.start_timer()

    def on_cell_change(self, row, col):
        """Callback wenn Zelle geändert wird"""

        def callback(event):
            # entry = self.entries[row][col]
            entry = event.widget

            if not self.controller.on_cell_changed(row, col, entry.get()):
                entry.config(bg="red")
                self.show_fail()
                entry.delete(0, tk.END)
                entry.insert(0, "")
                entry.config(bg="white")
            else:
                entry.config(bg="white")

            if self.check_all_filled():
                self.toggle_pause()
                self.show_win()

        return callback

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def update_timer(self):
        if self.timer_running:
            self.time_elapsed += 1

            # Formatierung:
            hours = int(self.time_elapsed / 3600)
            minutes = int((self.time_elapsed % 3600) / 60)
            seconds = int(self.time_elapsed % 60)
            time_string = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            self.timer_label.config(text=time_string)

            self.timer_id = self.root.after(1000, self.update_timer)

    def toggle_pause(self):
        if self.timer_running:
            self.timer_running = False
            self.pause_button.config(image=self.start_icon)

            if self.timer_id:
                self.root.after_cancel(self.timer_id)
        else:
            self.timer_running = True
            self.pause_button.config(image=self.pause_icon)
            self.update_timer()

    def validate_entry(self, new_value):
        """Erlaubt nur 1 Zeichen (0-9 oder leer)"""
        # Leer erlauben (zum Löschen)
        if new_value == "":
            return True

        # Nur 1 Ziffer von 1-9 erlauben
        if len(new_value) == 1 and new_value in "123456789":
            return True

        return False


    def set_grid_values(self):
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
        if lives == 2:
            self.heart1_label.config(image=self.empty_heart_icon)
        elif lives == 1:
            self.heart2_label.config(image=self.empty_heart_icon)
        elif lives == 0:
            self.heart3_label.config(image=self.empty_heart_icon)
            self.show_loose()

    def check_all_filled(self):
        """Prüft ob alle Felder ausgefüllt sind"""
        for row in self.entries:
            for entry in row:
                if entry.get() == "":
                    return False
        return True

    def show_fail(self):
        tk.messagebox.showerror("Das war leider falsch...")

    def show_loose(self):
        tk.messagebox.showerror("Du hast leider verloren")

    def show_win(self):
        tk.messagebox.showinfo("Du hast das Sudoku gelöst! Herzlichen Glückwunsch")
