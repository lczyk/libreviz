import time
from typing import TYPE_CHECKING, overload

import pyautogui

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = str  # type: ignore[assignment]

from .calibrate import CalibrationData
from .patched_click import click

Coord: TypeAlias = "tuple[int, int] | tuple[str, str | int] | str"


def _cell_coords_i(calib: CalibrationData, c: tuple[int, int]) -> tuple[float, float]:
    """Move to the specified cell in the grid by index."""
    width = calib.x2 - calib.x1
    height = calib.y2 - calib.y1
    cell_width = width / (calib.n_cols - 1)
    cell_height = height / (calib.n_rows - 1)
    x = calib.x1 + cell_width * c[0]
    y = calib.y1 + cell_height * c[1]
    return (x, y)


def _cell_coords_x(calib: CalibrationData, c: "tuple[str, str | int]") -> tuple[float, float]:
    """Move to the specified cell in the grid by column letter and row number."""
    col, row = c
    col_index = ord(col.upper()) - ord("A")
    if col_index < -1 or col_index >= calib.n_cols:
        raise ValueError(f"Column {col} is out of range.")
    row_index = int(row) - 1
    if row_index < -1 or row_index >= calib.n_rows:
        raise ValueError(f"Row {row} is out of range.")
    return _cell_coords_i(calib, (col_index, row_index))


def _cell_coords_x2(calib: CalibrationData, a: str) -> tuple[float, float]:
    """Move to the specified cell in the grid by column letter and row number."""
    a, b = a.split(":")
    return _cell_coords_x(calib, (a, b))


@overload
def cell_coords(calib: CalibrationData, c: tuple[int, int]) -> tuple[float, float]:
    """Move to the specified cell in the grid by index."""


@overload
def cell_coords(calib: CalibrationData, c: "tuple[str, str | int]") -> tuple[float, float]:
    """Move to the specified cell in the grid by column letter and row number."""


@overload
def cell_coords(calib: CalibrationData, c: str) -> tuple[float, float]:
    """Move to the specified cell in the grid by column letter and row number in a string format."""


def cell_coords(calib: CalibrationData, c: Coord) -> tuple[float, float]:
    """Move to the specified cell in the grid."""
    if isinstance(c, str):
        return _cell_coords_x2(calib, c)
    elif isinstance(c, tuple):
        if all(isinstance(i, int) for i in c):
            return _cell_coords_i(calib, c)  # type: ignore
        else:
            return _cell_coords_x(calib, c)  # type: ignore
    else:
        raise TypeError(f"Invalid type for cell: {type(c)}")


def select_range(calib: CalibrationData, c1: Coord, c2: Coord) -> None:
    """Select a range of cells from (col1, row1) to (col2, row2)."""
    click(*cell_coords(calib, c1))
    if c2 != c1:
        # sometime, rarely, the shift lands before the click
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        pyautogui.keyDown("shift")
        click(*cell_coords(calib, c2))
        pyautogui.keyUp("shift")


def select_column_index(calib: CalibrationData, col: "int | str") -> None:
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


def select_row_index(calib: CalibrationData, row: int) -> None:
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
