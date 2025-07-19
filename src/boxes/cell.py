import time

import pyautogui

from .calibrate import CalibrationData
from .patched_click import click

CellIJ = tuple[int, int]
CellStr = str
CellUV = tuple[float, float]
CellWQ = tuple[float, float]


def _cell_coords_i(calib: CalibrationData, c: tuple[int, int]) -> tuple[float, float]:
    """Move to the specified cell in the grid by index."""
    return (
        calib.top_left[0] + calib.cell_width * c[0],
        calib.top_left[1] + calib.cell_height * c[1],
    )


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


def ij2str(c: CellIJ) -> str:
    """Convert cell coordinates from (i, j) to 'A:1' format."""
    col = chr(ord("A") + c[0])
    row = str(c[1] + 1)
    return f"{col}:{row}"


def str2ij(c: CellStr) -> CellIJ:
    """Convert cell coordinates from 'A:1' format to (i, j)."""
    col, row = c.split(":")
    col_index = ord(col.upper()) - ord("A")
    row_index = int(row) - 1
    return (col_index, row_index)


def cell_coords(calib: CalibrationData, c: CellStr) -> tuple[float, float]:
    a, b = c.split(":")
    return _cell_coords_x(calib, (a, b))


def select_range(calib: CalibrationData, c1: CellStr, c2: CellStr) -> None:
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


def ij2uv(calib: CalibrationData, ij: CellIJ) -> CellUV:
    u = ij[0] / (calib.n_cols - 1) * 2 - 1
    v = ij[1] / (calib.n_rows - 1) * 2 - 1
    return (u, v)


def ij2wq(calib: CalibrationData, ij: CellIJ) -> CellWQ:
    # w/q coordinates are just like u/v, but the color is in screen coordinates,
    # not image coordinates. This means that the circles are drawn correctly
    cell_area_width = calib.n_cols * calib.cell_width
    cell_area_height = calib.n_rows * calib.cell_height
    aspect_ratio = cell_area_width / cell_area_height
    if aspect_ratio > 1:
        # Wider than tall
        w = (ij[0] / (calib.n_cols - 1) * 2 - 1) * aspect_ratio
        q = ij[1] / (calib.n_rows - 1) * 2 - 1
    else:
        # Taller than wide
        w = ij[0] / (calib.n_cols - 1) * 2 - 1
        q = (ij[1] / (calib.n_rows - 1) * 2 - 1) / aspect_ratio
    return (w, q)


DEFAULT_CELL_WIDTH = 2.26  # cm
DEFAULT_CELL_HEIGHT = 0.45  # cm


def change_cell_dimensions(
    calib: CalibrationData,
    cell_width: float = DEFAULT_CELL_WIDTH,
    cell_height: float = DEFAULT_CELL_HEIGHT,
) -> None:
    """Change the cell dimensions in the calibration data."""
    pyautogui.keyDown("command")
    pyautogui.press("a")
    pyautogui.keyUp("command")
    click(*calib.row_settings_location)
    click(*calib.row_height_location)
    for _ in range(10):
        pyautogui.press("delete")
    pyautogui.write(str(cell_height))
    pyautogui.press("enter")

    click(*calib.column_settings_location)
    click(*calib.column_width_location)
    for _ in range(10):
        pyautogui.press("delete")
    pyautogui.write(str(cell_width))
    pyautogui.press("enter")

    # row_settings_location = (
    #     row_column_location.left / pixel_ratio + 0.25 * row_column_location.width / pixel_ratio,
    #     row_column_location.top / pixel_ratio + 0.5 * row_column_location.height / pixel_ratio,
    # )
    # row_height_location = (
    #     row_settings_location[0],
    #     row_settings_location[1] + 120 / pixel_ratio,
    # )

    # pyautogui.keyDown("command")
    # pyautogui.press("a")
    # pyautogui.keyUp("command")
    # click(*row_settings_location)
    # click(*row_height_location)
    # for _ in range(10):
    #     pyautogui.press("delete")
    # pyautogui.write(str(cell_height))
    # pyautogui.press("enter")

    # column_settings_location = (
    #     row_column_location.left / pixel_ratio + 0.75 * row_column_location.width / pixel_ratio,
    #     row_column_location.top / pixel_ratio + 0.5 * row_column_location.height / pixel_ratio,
    # )
    # column_width_location = (
    #     column_settings_location[0],
    #     column_settings_location[1] + 120 / pixel_ratio,
    # )

    # click(*column_settings_location)
    # click(*column_width_location)
    # for _ in range(10):
    #     pyautogui.press("delete")
    # pyautogui.write(str(cell_width))
    # pyautogui.press("enter")
