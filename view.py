# TODO: - Wenn Pause, dann einen Dialog schalten
#       - Logik hinter eingegebenen Zahlen im Sudoku implementieren
#           -> Hier mit KI fragen, wie das verbunden wird, braucht
#              man dazu Controller?

import tkinter as tk


class SudokuView:
    def __init__(self, root):
        self.root = root

        #Menu Attribute
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack()

        # Timer-Attribute
        self.time_elapsed = 0
        self.timer_running = False
        self.timer_id = None

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


        # Grid Attribute
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()

        self.entries = []

        self.setup_window()

        self.start_timer()



    def setup_window(self):
        """Fenster Aufbauen"""
        self.root.title("Sudoku App")
        self.root.geometry("600x700")
        #self.center_window()
        self.create_widgets()


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
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)

        # Position vom Fenster festlegen
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")


    def create_widgets(self):

        self.timer_label = tk.Label(self.menu_frame,
                                    text="00:00:00",
                                    font=("Arial", 16),
                                    background="light grey",
                                    foreground="red")
        self.timer_label.grid(row=0, column=0, padx=100)

        self.pause_button = tk.Button(self.menu_frame,
                                      image=self.pause_icon,
                                      command=self.toggle_pause)
        self.pause_button.grid(row=0, column=1, padx=10)

        self.help_button = tk.Button(self.menu_frame, image=self.help_icon)
        self.help_button.grid(row=0, column=2)



        vcmd = (self.root.register(self.validate_entry), '%P')

        # Grid erstellen
        for row in range(9):
            row_entries = []
            for col in range(9):
                padx_left = 10 if col % 3 == 0 else 2
                pady_top = 10 if row % 3 == 0 else 2

                entry = tk.Entry(self.grid_frame,
                                 width=2,
                                 font=("Arial", 24, "bold"),
                                 justify="center",
                                 validate="key",
                                 validatecommand=vcmd)
                entry.grid(row=row, column=col,
                           padx=(padx_left, 1),
                           pady=(pady_top, 1))
                row_entries.append(entry)

            self.entries.append(row_entries)

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


    def set_grid_values(self, sudoku):
        for i in range(9):
            for j in range(9):
                self.entries[i][j].delete(0, tk.END)

                if sudoku[i][j] != 0:
                    self.entries[i][j].insert(0, str(sudoku[i][j]))