import importlib.util
from pathlib import Path

MAIN_PATH = Path(__file__).resolve().parent.parent / "main.py"


def load_main_module():
    spec = importlib.util.spec_from_file_location("sudoku_main", MAIN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_main_ist_aufrufbar():
    module = load_main_module()
    assert callable(module.main)
