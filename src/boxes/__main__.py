import json
import os
import sys
import time
from itertools import tee
from typing import TYPE_CHECKING, overload

import pyautogui

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = str  # type: ignore[assignment]

import eject_button

eject_button.arm()

if __package__ is None or __package__ == "":
    from calibrate import CalibrationData, calibrate
    from patched_click import click
    from run import run
else:
    from .calibrate import CalibrationData, calibrate
    from .patched_click import click
    from .run import run

from pathlib import Path

__file_dir__ = Path(__file__).parent
__project_root__ = __file_dir__.parent.parent

BOXES = __project_root__ / "src" / "boxes"


def main():
    if len(sys.argv) == 1:
        response = pyautogui.confirm(
            text=(
                "This script will do things. Is LibreOffice open **and cell A1 selected**? "
                "If you press 'Yes', you will see a calibration procedure and then another "
                "confirmation box."
            ),
            title="Boxes",
            buttons=["Yes", "No"],
        )

        if response == "No":
            print("Exiting script.")
            sys.exit()

        # call self with 'run' argument and replace the current process
        os.execv(sys.executable, [sys.executable, BOXES, "calibrate"])

    elif sys.argv[1] == "calibrate":
        calibration_data = calibrate(
            # 1 on most monitors, 2 on high DPI monitors
            pixel_ratio=2,
            sleep_time=0.0,
        )
        os.execv(
            sys.executable,
            [sys.executable, BOXES, "run", calibration_data.to_b64()],
        )

    elif sys.argv[1] == "run":
        try:
            CD = CalibrationData.from_b64(sys.argv[2])
        except json.JSONDecodeError:
            print("Error: Invalid calibration data.")
            sys.exit()

        print(CD)

        run(CD)

    else:
        raise ValueError(f"Unknown argument: {sys.argv[1]}. Expected 'calibrate' or 'run'.")


def _cell_coords_i(calib: CalibrationData, c: tuple[int, int]):
    """Move to the specified cell in the grid by index."""
    width = calib.x2 - calib.x1
    height = calib.y2 - calib.y1
    cell_width = width / (calib.n_cols - 1)
    cell_height = height / (calib.n_rows - 1)
    x = calib.x1 + cell_width * c[0]
    y = calib.y1 + cell_height * c[1]
    return (x, y)


def _cell_coords_x(calib: CalibrationData, c: "tuple[str, str | int]"):
    """Move to the specified cell in the grid by column letter and row number."""
    col, row = c
    col_index = ord(col.upper()) - ord("A")
    if col_index < -1 or col_index >= calib.n_cols:
        raise ValueError(f"Column {col} is out of range.")
    row_index = int(row) - 1
    if row_index < -1 or row_index >= calib.n_rows:
        raise ValueError(f"Row {row} is out of range.")
    return _cell_coords_i(calib, (col_index, row_index))


def _cell_coords_x2(calib: CalibrationData, a: str):
    """Move to the specified cell in the grid by column letter and row number."""
    a, b = a.split(":")
    return _cell_coords_x(calib, (a, b))


@overload
def cell_coords(calib: CalibrationData, c: tuple[int, int]) -> None:
    """Move to the specified cell in the grid by index."""


@overload
def cell_coords(calib: CalibrationData, c: "tuple[str, str | int]") -> None:
    """Move to the specified cell in the grid by column letter and row number."""


@overload
def cell_coords(calib: CalibrationData, c: str) -> None:
    """Move to the specified cell in the grid by column letter and row number in a string format."""


Coord: TypeAlias = "tuple[int, int] | tuple[str, str | int] | str"


def cell_coords(calib: CalibrationData, c: Coord) -> tuple[int, int]:
    """Move to the specified cell in the grid."""
    if isinstance(c, str):
        return _cell_coords_x2(calib, c)
    elif isinstance(c, tuple):
        if all(isinstance(i, int) for i in c):
            return _cell_coords_i(calib, c)
        else:
            return _cell_coords_x(calib, c)
    else:
        raise TypeError(f"Invalid type for cell: {type(c)}")


def select_range(calib: CalibrationData, c1: Coord, c2: Coord):
    """Select a range of cells from (col1, row1) to (col2, row2)."""
    click(*cell_coords(calib, c1))
    if c2 != c1:
        pyautogui.keyDown("shift")
        click(*cell_coords(calib, c2))
        pyautogui.keyUp("shift")


def select_column_index(calib: CalibrationData, col: "int | str"):
    """Select the entire column."""
    if isinstance(col, int):
        col = chr(ord("A") + col)
    elif isinstance(col, str):
        col = col.upper()
    else:
        raise TypeError(f"Invalid type for column: {type(col)}")

    coords = (
        calib.first_col[0] + (ord(col) - ord("A")) * calib.cell_width,
        calib.first_col[1],
    )
    click(*coords)


def select_row_index(calib: CalibrationData, row: int):
    """Select the entire row."""
    if not isinstance(row, int):
        raise TypeError(f"Invalid type for row: {type(row)}")
    if row < 0 or row > calib.n_rows:
        raise ValueError(f"Row {row} is out of range.")

    coords = (
        calib.first_row[0],
        calib.first_row[1] + row * calib.cell_height,
    )
    click(*coords)


def reset_all_cell_contents(calib: CalibrationData):
    """Reset all cell contents in the grid to 'No Fill'."""
    select_range(calib, ("A", 1), ("S", 52))
    pyautogui.press("backspace")
    time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
    pyautogui.press("enter")


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


if __name__ == "__main__":
    main()
