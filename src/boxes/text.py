import time

import pyautogui

from .calibrate import CalibrationData
from .utils import select_range


def reset_all_cell_contents(calib: CalibrationData) -> None:
    """Reset all cell contents in the grid to 'No Fill'."""
    select_range(calib, ("A", 1), ("S", 52))
    pyautogui.press("backspace")
    time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
    pyautogui.press("enter")
