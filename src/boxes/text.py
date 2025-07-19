import time

import pyautogui

from . import cell
from .calibrate import CalibrationData


def reset_all_cell_contents(calib: CalibrationData) -> None:
    """Reset all cell contents in the grid to 'No Fill'."""
    cell.select_range(
        calib,
        cell.ij2str((0, 0)),
        cell.ij2str((calib.n_cols - 1, calib.n_rows - 1)),
    )
    pyautogui.press("backspace")
    time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
    pyautogui.press("enter")
