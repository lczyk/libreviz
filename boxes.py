import os
import sys
import pyautogui
import json
import base64
from itertools import tee
import random
from typing import overload, TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import TypeAlias
else:
    TypeAlias = str  # type: ignore[assignment]


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


from dataclasses import dataclass


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

    n_cols: int
    n_rows: int
    n_color_cols: int
    n_color_rows: int

    @classmethod
    def from_b64(cls, b64_data: str):
        """Create an instance from base64 encoded JSON string."""
        try:
            data = json.loads(base64.b64decode(b64_data).decode())
            return cls(**{k: int(v) for k, v in data.items()})
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
        n_cols=19,
        n_rows=52,
        n_color_cols=12,
        n_color_rows=10,
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
    if col_index < 0 or col_index >= calib.n_cols:
        raise ValueError(f"Column {col} is out of range.")
    row_index = int(row) - 1
    if row_index < 0 or row_index >= calib.n_rows:
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

def select_range_fast(calib: CalibrationData, c1: Coord, c2: Coord):
    """Select a range of cells from (col1, row1) to (col2, row2)."""
    _click(*cell_coords(calib, c1))
    pyautogui.keyDown("shift")
    _click(*cell_coords(calib, c2))
    pyautogui.keyUp("shift")


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


def apply_color(calib: CalibrationData, c: "tuple[int, int]"):
    """Apply the color from the specified color cell in the color palette."""
    global LAST_COLOR
    if c == LAST_COLOR:
        # apply the same color again
        coords = (calib.bx - 20, calib.by)
        _click(*coords)
    else:
        # change color
        open_bucket(calib)
        _click(*color_coords(calib, c))

    LAST_COLOR = c


def apply_no_fill(calib: CalibrationData):
    """Apply 'No Fill' color to the selected cells."""
    global LAST_COLOR
    if LAST_COLOR == (-1, -1):
        # already applied 'No Fill'
        position = (calib.bx - 20, calib.by)
    else:
        open_bucket(calib)
        position = (calib.cx1, calib.cy1)

    _click(*position)

    LAST_COLOR = (-1, -1)


def reset_all_colors(calib: CalibrationData):
    """Reset all colors in the grid to 'No Fill'."""
    select_range_fast(calib, ("A", 1), ("S", 52))
    apply_no_fill(calib)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


############################################################################


def inward_spiral(calib: CalibrationData, color: "tuple[int, int]"):
    nodes = "A:1,S:1,S:52,A:52,A:3,Q:3,Q:50,C:50,C:5,O:5,O:48,E:48,E:7,M:7,M:46,G:46,G:9,K:9,K:44,I:44,I:11"
    nodes = nodes.split(",")

    for n1, n2 in pairwise(nodes):
        select_range_fast(calib, n1, n2)
        apply_color(calib, color)


def outward_spiral(calib: CalibrationData, color: "tuple[int, int]"):
    nodes = "J:43,J:10,H:10,H:45,L:45,L:8,F:8,F:47,N:47,N:6,D:6,D:49,P:49,P:4,B:4,B:51,R:51,R:2,A:2"
    nodes = nodes.split(",")

    for n1, n2 in pairwise(nodes):
        select_range_fast(calib, n1, n2)
        apply_color(calib, color)


def random_color(calib: CalibrationData) -> "tuple[int, int]":
    random_color_row = random.randint(0, calib.n_color_rows - 1)
    random_color_col = random.randint(0, calib.n_color_cols - 1)
    return random_color_col, random_color_row

################################################################################

def run(calib: CalibrationData):
    reset_all_colors(calib)

    # pyautogui.PAUSE = 0.0
    pyautogui.PAUSE = 0.03

    # while True:
    #     inward_spiral(calib, random_color(calib))
    #     outward_spiral(calib, random_color(calib))

    # Test pattern
    for i in range(calib.n_color_cols):
        for j in range(calib.n_color_rows):
            print(f"Applying color ({i}, {j})")
            _click(*cell_coords(calib, (i, 4 * j + 4)))
            apply_color(calib, (i, j))
            _click(*cell_coords(calib, (i, 4 * j + 4 + 1)))
            apply_color(calib, (i, j))
            _click(*cell_coords(calib, (i, 4 * j + 4 + 2)))
            apply_color(calib, (i, j))
            _click(*cell_coords(calib, (i, 4 * j + 4 + 3)))
            apply_color(calib, (i, j))

    select_range_fast(calib, "A:1", "D:4")
    apply_no_fill(calib)
    _click(*cell_coords(calib, "A:1"))

if __name__ == "__main__":
    main()
