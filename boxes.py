import os
import sys
import pyautogui
import json
import base64
from itertools import tee
import random


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
        calibration_data = calibrate()

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


def calibrate() -> CalibrationData:
    # 1 on most monitors, 2 on high DPI monitors
    DPI = 2

    # check that 'top_left.png' exists
    if not os.path.exists("./top_left.png"):
        print("Error: top_left.png not found.")
        exit()

    # locate the image on the screen
    location1 = None

    try:
        location1 = pyautogui.locateOnScreen("top_left.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        pass

    if location1 is None:
        print("Error: top_left.png not found on screen.")
        exit()

    try:
        location_bucket = pyautogui.locateOnScreen("bucket.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        location_bucket = None

    if location_bucket is None:
        print("Error: bucket.png not found on screen.")
        exit()

    print("top_left.png location:", location1)
    print("bucket.png location:", location_bucket)

    screen_size = pyautogui.size()
    print(f"Screen size: {screen_size}")

    # top left cell
    top_left_cell = (
        location1.left / DPI + 73,
        location1.top / DPI + location1.height / DPI - 30,
    )
    pyautogui.moveTo(*top_left_cell)

    pyautogui.sleep(0.1)

    # top right cell
    top_right_cell = (
        screen_size.width - 105,
        top_left_cell[1],
    )
    pyautogui.moveTo(*top_right_cell)

    pyautogui.sleep(0.1)

    # bottom left cell
    bottom_left_cell = (
        top_left_cell[0],
        screen_size.height - 70,
    )
    pyautogui.moveTo(*bottom_left_cell)

    pyautogui.sleep(0.1)

    # bottom right cell
    bottom_right_cell = (
        top_right_cell[0],
        bottom_left_cell[1],
    )

    pyautogui.moveTo(*bottom_right_cell)

    pyautogui.sleep(0.1)

    # move to the bucket icon
    bucket_location_2 = (
        location_bucket.left / DPI + 0.85 * location_bucket.width / DPI,
        location_bucket.top / DPI + location_bucket.height / DPI / 2,
    )
    pyautogui.moveTo(*bucket_location_2)
    pyautogui.click()

    no_fill_location = (
        bucket_location_2[0] - 10,
        bucket_location_2[1] + 50,
    )

    pyautogui.moveTo(*no_fill_location)

    pyautogui.sleep(0.2)

    top_left_color = (
        bucket_location_2[0] - 20,
        bucket_location_2[1] + 120,
    )

    pyautogui.moveTo(*top_left_color)

    pyautogui.sleep(0.2)

    bottom_right_color = (
        top_left_color[0] + 190,
        top_left_color[1] + 155,
    )

    pyautogui.moveTo(*bottom_right_color)

    pyautogui.sleep(0.2)

    pyautogui.moveTo(*top_left_cell)
    pyautogui.click()

    # display a message box to check whether we want to proceed
    response = pyautogui.confirm(
        text="Was that correct?", title="Boxes", buttons=["Yes", "No"]
    )

    if response == "No":
        print("Exiting script.")
        exit()

    calibration_data = CalibrationData(
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
    )

    return calibration_data


N_COLS = 19
N_ROWS = 52

N_COLOR_COLS = 12
N_COLOR_ROWS = 10


def move_to_cell_i(calib: CalibrationData, col, row):
    """Move to the specified cell in the grid by index."""
    width = calib.x2 - calib.x1
    height = calib.y2 - calib.y1
    cell_width = width / (N_COLS - 1)
    cell_height = height / (N_ROWS - 1)
    x = calib.x1 + cell_width * col
    y = calib.y1 + cell_height * row
    pyautogui.moveTo(x, y)


def move_to_cell_x(calib: CalibrationData, a: "tuple[str, str | int]"):
    """Move to the specified cell in the grid by column letter and row number."""
    col, row = a
    col_index = ord(col.upper()) - ord("A")
    if col_index < 0 or col_index >= N_COLS:
        raise ValueError(f"Column {col} is out of range.")
    row_index = int(row) - 1
    if row_index < 0 or row_index >= N_ROWS:
        raise ValueError(f"Row {row} is out of range.")
    move_to_cell_i(calib, col_index, row_index)


ENSURE_PAUSE_TIME = 0.02


def ensure_pause():
    if pyautogui.PAUSE < ENSURE_PAUSE_TIME:
        pyautogui.sleep(ENSURE_PAUSE_TIME)


def select_range_fast(
    calib: CalibrationData,
    a: "tuple[str, str | int]",
    b: "tuple[str, str | int]",
):
    """Select a range of cells from (col1, row1) to (col2, row2)."""
    move_to_cell_x(calib, a)
    pyautogui.click()
    ensure_pause()
    move_to_cell_x(calib, b)
    pyautogui.keyDown("shift")
    ensure_pause()
    pyautogui.click()
    pyautogui.keyUp("shift")
    ensure_pause()


def open_bucket(calib: CalibrationData):
    """Open the bucket tool in LibreOffice."""
    pyautogui.moveTo(calib.bx, calib.by)
    pyautogui.click()
    ensure_pause()


def move_to_color_i(calib: CalibrationData, col_i: int, row_i: int):
    """Move to the specified color cell in the color palette."""
    width = calib.cx3 - calib.cx2
    height = calib.cy3 - calib.cy2
    color_cell_width = width / (N_COLOR_COLS - 1)
    color_cell_height = height / (N_COLOR_ROWS - 1)
    x = calib.cx2 + color_cell_width * col_i
    y = calib.cy2 + color_cell_height * row_i
    pyautogui.moveTo(x, y)


def move_to_no_fill(calib: CalibrationData):
    """Move to the 'No Fill' color cell in the color palette."""
    pyautogui.moveTo(calib.cx1, calib.cy1)


global LAST_COLOR
LAST_COLOR = None


def apply_color_i(calib: CalibrationData, col_i: int, row_i: int):
    """Apply the color from the specified color cell in the color palette."""
    global LAST_COLOR
    this_color = (col_i, row_i)
    if this_color == LAST_COLOR:
        # apply the same color again
        pyautogui.moveTo(calib.bx - 20, calib.by)
    else:
        # change color
        open_bucket(calib)
        move_to_color_i(calib, col_i, row_i)

    pyautogui.click()
    ensure_pause()

    LAST_COLOR = this_color


def apply_no_fill(calib: CalibrationData):
    """Apply 'No Fill' color to the selected cells."""
    global LAST_COLOR
    if LAST_COLOR == (-1, -1):
        # already applied 'No Fill'
        pyautogui.moveTo(calib.bx - 20, calib.by)
    else:
        open_bucket(calib)
        move_to_no_fill(calib)

    pyautogui.click()
    ensure_pause()

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
    nodes = [
        ("A", 1),
        ("S", 1),
        ("S", 52),
        ("A", 52),
        ("A", 3),
        ("Q", 3),
        ("Q", 50),
        ("C", 50),
        ("C", 5),
        ("O", 5),
        ("O", 48),
        ("E", 48),
        ("E", 7),
        ("M", 7),
        ("M", 46),
        ("G", 46),
        ("G", 9),
        ("K", 9),
        ("K", 44),
        ("I", 44),
        ("I", 11),
    ]

    for n1, n2 in pairwise(nodes):
        select_range_fast(calib, n1, n2)
        apply_color_i(calib, *color)


def outward_spiral(calib: CalibrationData, color: "tuple[int, int]"):
    nodes = [
        ("J", 43),
        ("J", 10),
        ("H", 10),
        ("H", 45),
        ("L", 45),
        ("L", 8),
        ("F", 8),
        ("F", 47),
        ("N", 47),
        ("N", 6),
        ("D", 6),
        ("D", 49),
        ("P", 49),
        ("P", 4),
        ("B", 4),
        ("B", 51),
        ("R", 51),
        ("R", 2),
        ("A", 2),
    ]

    for n1, n2 in pairwise(nodes):
        select_range_fast(calib, n1, n2)
        apply_color_i(calib, *color)


def random_color():
    random_color_row = random.randint(0, N_COLOR_ROWS - 1)
    random_color_col = random.randint(0, N_COLOR_COLS - 1)
    return random_color_col, random_color_row


def run(calib: CalibrationData):
    reset_all_colors(calib)

    pyautogui.PAUSE = 0.0

    while True:
        inward_spiral(calib, random_color())
        outward_spiral(calib, random_color())


if __name__ == "__main__":
    main()
