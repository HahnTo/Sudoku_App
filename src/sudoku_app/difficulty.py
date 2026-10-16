from enum import Enum


class Difficulty(Enum):
    """Schwierigkeitsgrad mit Anzahl der Leerstellen und Menü-Label."""

    EASY = (20, 30, "Leicht")
    MEDIUM = (35, 40, "Mittel")
    HARD = (45, 50, "Schwer")

    def __init__(self, min_blanks, max_blanks, label):
        self.min_blanks = min_blanks
        self.max_blanks = max_blanks
        self.label = label
