import os
import sys
import pyautogui
import json
import base64
from itertools import tee
import random
from typing import overload, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = str  # type: ignore[assignment]

from pynput import keyboard


def on_press(key):
    if key == keyboard.Key.esc:
        # Graceless exit
        os._exit(0)


listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.wait()

print("Press ESC to exit the script.")

if sys.platform == "darwin":
    import Quartz
    import time
    from pyautogui._pyautogui_osx import _sendMouseEvent

    def _click(x, y):
        _sendMouseEvent(Quartz.kCGEventLeftMouseDown, x, y, Quartz.kCGMouseButtonLeft)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        _sendMouseEvent(Quartz.kCGEventLeftMouseUp, x, y, Quartz.kCGMouseButtonLeft)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)

        time.sleep(pyautogui.PAUSE)


else:

    def _click(x, y):
        pyautogui.click(x, y, button=pyautogui.LEFT)


@dataclass(frozen=True)
class CalibrationData:
    x1: int
    y1: int
    x2: int
    y2: int
    bx: int
    by: int
    cx1: int
    cy1: int
    cx2: int
    cy2: int
    cx3: int
    cy3: int

    cell_width: float
    cell_height: float

    # (x, y) coordinates of the label cell for the first column and row
    first_row: tuple[float, float]
    first_col: tuple[float, float]

    n_cols: int
    n_rows: int
    n_color_cols: int
    n_color_rows: int

    @classmethod
    def from_b64(cls, b64_data: str):
        """Create an instance from base64 encoded JSON string."""
        try:
            data = json.loads(base64.b64decode(b64_data).decode())
            return cls(**{k: v for k, v in data.items()})
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding calibration data: {e}")
            raise ValueError("Invalid calibration data format.")

    def to_b64(self):
        """Convert the instance to a base64 encoded JSON string."""
        return base64.b64encode(json.dumps(self.__dict__).encode()).decode()


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
            exit()

        # call self with 'run' argument and replace the current process
        os.execv(sys.executable, [sys.executable] + ["boxes.py", "calibrate"])

    elif sys.argv[1] == "calibrate":
        calibration_data = calibrate(
            # 1 on most monitors, 2 on high DPI monitors
            pixel_ratio=2,
            # sleep_time=1.0,
        )

        os.execv(
            sys.executable,
            [sys.executable] + ["boxes.py", "run", calibration_data.to_b64()],
        )

    elif sys.argv[1] == "run":
        try:
            CD = CalibrationData.from_b64(sys.argv[2])
        except json.JSONDecodeError:
            print("Error: Invalid calibration data.")
            exit()

        print(CD)

        run(CD)

    else:
        raise ValueError(
            f"Unknown argument: {sys.argv[1]}. Expected 'calibrate' or 'run'."
        )


def calibrate(
    pixel_ratio: int = 1,
    sleep_time: float = 0.1,
) -> CalibrationData:
    # check that 'top_left.png' exists
    if not os.path.exists("./top_left.png"):
        print("Error: top_left.png not found.")
        exit()

    # locate the image on the screen
    location_A1 = None

    try:
        location_A1 = pyautogui.locateOnScreen("top_left.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        pass

    if location_A1 is None:
        print("Error: top_left.png not found on screen.")
        exit()

    try:
        location_bucket = pyautogui.locateOnScreen("bucket.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        location_bucket = None

    if location_bucket is None:
        print("Error: bucket.png not found on screen.")
        exit()

    # print("top_left.png location:", location_A1)
    # print("bucket.png location:", location_bucket)

    screen_size = pyautogui.size()
    # print(f"Screen size: {screen_size}")

    # top left cell
    top_left_cell = (
        location_A1.left / pixel_ratio + 73,
        location_A1.top / pixel_ratio + location_A1.height / pixel_ratio - 30,
    )
    pyautogui.moveTo(*top_left_cell)
    pyautogui.sleep(sleep_time)

    # top right cell
    top_right_cell = (
        screen_size.width - 105,
        top_left_cell[1],
    )
    pyautogui.moveTo(*top_right_cell)
    pyautogui.sleep(sleep_time)

    # bottom left cell
    bottom_left_cell = (
        top_left_cell[0],
        screen_size.height - 70,
    )
    pyautogui.moveTo(*bottom_left_cell)
    pyautogui.sleep(sleep_time)

    # bottom right cell
    bottom_right_cell = (
        top_right_cell[0],
        bottom_left_cell[1],
    )

    pyautogui.moveTo(*bottom_right_cell)
    pyautogui.sleep(sleep_time)

    n_cols = 19
    n_rows = 52
    n_color_cols = 12
    n_color_rows = 10

    cell_width = (top_right_cell[0] - top_left_cell[0]) / (n_cols - 1)
    cell_height = (bottom_left_cell[1] - top_left_cell[1]) / (n_rows - 1)

    first_row = (
        top_left_cell[0] - cell_width / 2,
        top_left_cell[1],
    )
    first_row = (first_row[0] - first_row[0] / 2, first_row[1])

    first_col = (
        top_left_cell[0],
        top_left_cell[1] - cell_height,
    )

    # move to the bucket icon
    bucket_location_2 = (
        location_bucket.left / pixel_ratio + 0.85 * location_bucket.width / pixel_ratio,
        location_bucket.top / pixel_ratio + 0.5 * location_bucket.height / pixel_ratio,
    )
    _click(*bucket_location_2)

    no_fill_location = (
        bucket_location_2[0] - 10,
        bucket_location_2[1] + 50,
    )

    pyautogui.moveTo(*no_fill_location)
    pyautogui.sleep(sleep_time)

    top_left_color = (
        bucket_location_2[0] - 21,
        bucket_location_2[1] + 125,
    )

    pyautogui.moveTo(*top_left_color)
    pyautogui.sleep(sleep_time)

    bottom_right_color = (
        top_left_color[0] + 186,
        top_left_color[1] + 152,
    )

    pyautogui.moveTo(*bottom_right_color)
    pyautogui.sleep(sleep_time)

    _click(*top_left_cell)

    # display a message box to check whether we want to proceed
    response = pyautogui.confirm(
        text="Was that correct?", title="Boxes", buttons=["Yes", "No"]
    )

    if response == "No":
        print("Exiting script.")
        exit()

    return CalibrationData(
        x1=int(top_left_cell[0]),
        y1=int(top_left_cell[1]),
        x2=int(bottom_right_cell[0]),
        y2=int(bottom_right_cell[1]),
        bx=int(bucket_location_2[0]),
        by=int(bucket_location_2[1]),
        cx1=int(no_fill_location[0]),
        cy1=int(no_fill_location[1]),
        cx2=int(top_left_color[0]),
        cy2=int(top_left_color[1]),
        cx3=int(bottom_right_color[0]),
        cy3=int(bottom_right_color[1]),
        first_row=first_row,
        first_col=first_col,
        cell_width=cell_width,
        cell_height=cell_height,
        n_cols=n_cols,
        n_rows=n_rows,
        n_color_cols=n_color_cols,
        n_color_rows=n_color_rows,
    )


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
    _click(*cell_coords(calib, c1))
    pyautogui.keyDown("shift")
    _click(*cell_coords(calib, c2))
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
    _click(*coords)


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
    _click(*coords)

def open_bucket(calib: CalibrationData):
    """Open the bucket tool in LibreOffice."""
    _click(calib.bx, calib.by)


def color_coords(calib: CalibrationData, c: "tuple[int, int]"):
    """Move to the specified color cell in the color palette."""
    width = calib.cx3 - calib.cx2
    height = calib.cy3 - calib.cy2
    color_cell_width = width / (calib.n_color_cols - 1)
    color_cell_height = height / (calib.n_color_rows - 1)
    x = calib.cx2 + color_cell_width * c[0]
    y = calib.cy2 + color_cell_height * c[1]
    return (x, y)


global LAST_COLOR
LAST_COLOR = None

from typing import Protocol


class Color(Protocol):
    def apply(): ...


class StandardColor(Color):
    def __init__(self, calib: CalibrationData, color: "tuple[int, int]") -> None:
        self.calib = calib
        self.color = color

    def apply(self) -> None:
        global LAST_COLOR
        if LAST_COLOR == self.color:
            # apply the same color again
            position = (self.calib.bx - 20, self.calib.by)
        else:
            # change color
            open_bucket(self.calib)
            position = color_coords(self.calib, self.color)

        _click(*position)

        LAST_COLOR = self.color


if TYPE_CHECKING:
    _: Color = StandardColor()


class NoFillColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        self.calib = calib

    def apply(self) -> None:
        global LAST_COLOR
        if LAST_COLOR == "no-fill":
            position = (self.calib.bx - 20, self.calib.by)
        else:
            open_bucket(self.calib)
            position = (self.calib.cx1, self.calib.cy1)

        _click(*position)

        LAST_COLOR = "no-fill"


class RandomColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        self.calib = calib

    def apply(self) -> None:
        color = random_color(self.calib)
        global LAST_COLOR
        if LAST_COLOR == color:
            # apply the same color again
            position = (self.calib.bx - 20, self.calib.by)
        else:
            # change color
            open_bucket(self.calib)
            position = color_coords(self.calib, color)
        _click(*position)
        LAST_COLOR = color

def reset_all_colors(calib: CalibrationData):
    """Reset all colors in the grid to 'No Fill'."""
    select_range(calib, ("A", 1), ("S", 52))
    NoFillColor(calib).apply()


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


############################################################################


def inward_spiral(calib: CalibrationData, color: Color):
    nodes = "A:1,S:1,S:52,A:52,A:3,Q:3,Q:50,C:50,C:5,O:5,O:48,E:48,E:7,M:7,M:46,G:46,G:9,K:9,K:44,I:44,I:11"
    nodes = nodes.split(",")

    for n1, n2 in pairwise(nodes):
        select_range(calib, n1, n2)
        color.apply()


def outward_spiral(calib: CalibrationData, color: Color):
    nodes = "J:43,J:10,H:10,H:45,L:45,L:8,F:8,F:47,N:47,N:6,D:6,D:49,P:49,P:4,B:4,B:51,R:51,R:2,A:2"
    nodes = nodes.split(",")

    for n1, n2 in pairwise(nodes):
        select_range(calib, n1, n2)
        color.apply()


def random_color(calib: CalibrationData) -> "tuple[int, int]":
    random_color_row = random.randint(0, calib.n_color_rows - 1)
    random_color_col = random.randint(0, calib.n_color_cols - 1)
    return random_color_col, random_color_row


################################################################################


def test_pattern(calib: CalibrationData):
    for i in range(calib.n_color_cols):
        for j in range(calib.n_color_rows):
            print(f"Applying color ({i}, {j})")
            # _click(*cell_coords(calib, (i, 4 * j + 4)))
            # apply_color(calib, (i, j))
            # _click(*cell_coords(calib, (i, 4 * j + 4 + 1)))
            # apply_color(calib, (i, j))
            # _click(*cell_coords(calib, (i, 4 * j + 4 + 2)))
            # apply_color(calib, (i, j))
            # _click(*cell_coords(calib, (i, 4 * j + 4 + 3)))
            # apply_color(calib, (i, j))

            select_range(
                calib,
                (chr(ord("A") + i), 4 * j + 4),
                (chr(ord("A") + i), 4 * j + 4 + 3),
            )
            StandardColor(calib, (i, j)).apply()

def column_lights(
    calib: CalibrationData,
    color: Color,
    sleep_time: float = 0.1,
):
    """Apply a color to each cell in a column."""
    column_indices = [i for i in range(calib.n_cols)]
    random.shuffle(column_indices)
    for i in column_indices:
        # select_range(calib, (chr(ord("A") + i), 1), (chr(ord("A") + i), calib.n_rows))
        select_column_index(calib, i)
        color.apply()
        pyautogui.sleep(sleep_time)


def row_lights(
    calib: CalibrationData,
    color: Color,
    sleep_time: float = 0.1,
):
    """Apply a color to each cell in a row."""
    row_indices = [i for i in range(calib.n_rows)]
    random.shuffle(row_indices)
    for i in row_indices:
        # select_range(calib, ("A", i + 1), (chr(ord("A") + calib.n_cols - 1), i + 1))
        select_row_index(calib, i)
        color.apply()
        pyautogui.sleep(sleep_time)


def column_row_lights(
    calib: CalibrationData,
    col_color: Color,
    row_color: Color,
    sleep_time: float = 0.1,
):
    """Apply a color to each cell in a column and then in a row."""
    column_indices = [i for i in range(calib.n_cols)]
    random.shuffle(column_indices)
    row_indices = [i for i in range(calib.n_rows)]
    random.shuffle(row_indices)

    if len(column_indices) < len(row_indices):
        # les columns than rows. for each column, we need to apply a couple of rows
        ratio = len(column_indices) / len(row_indices)
        while True:
            if not column_indices and not row_indices:
                # no more columns or rows to apply
                break
            if len(column_indices) > len(row_indices) * ratio:
                # apply columns
                select_column_index(calib, column_indices.pop())
                col_color.apply()
            else:
                # apply rows
                select_row_index(calib, row_indices.pop())
                row_color.apply()

            time.sleep(sleep_time)
    else:
        raise NotImplementedError

def cell_lights(
    calib: CalibrationData,
    color: Color,
    sleep_time: float = 0.1,
):
    """Apply a color to each cell in the grid."""
    coords = [(i, j) for i in range(calib.n_cols) for j in range(calib.n_rows)]
    random.shuffle(coords)

    for i, j in coords:
        _click(*cell_coords(calib, (i, j)))
        color.apply()
        pyautogui.sleep(sleep_time)

def run(calib: CalibrationData):
    reset_all_colors(calib)

    # pyautogui.PAUSE = 0.0
    pyautogui.PAUSE = 0.03

    # while True:
    #     inward_spiral(calib, random_color(calib))
    #     outward_spiral(calib, random_color(calib))

    cell_lights(calib, RandomColor(calib), sleep_time=0.0)

    # Test pattern
    # test_pattern(calib)

    # column_lights(calib, random_color(calib))
    # reset_all_colors(calib)
    # row_lights(calib, random_color(calib))
    # reset_all_colors(calib)

    # while True:
    #     column_row_lights(calib, random_color(calib), random_color(calib), sleep_time=0)
    #     # reset_all_colors(calib)

    # Clean up a tiny bit
    select_range(calib, "A:1", "D:4")
    NoFillColor(calib).apply()
    _click(*cell_coords(calib, "A:1"))


if __name__ == "__main__":
    main()
