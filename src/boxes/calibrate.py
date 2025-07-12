import base64
import contextlib
import json
import os
import sys
from dataclasses import dataclass

import pyautogui

from .patched_click import click


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

    custom_color: tuple[float, float]  # (x, y) coordinates of the custom color button

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
    def from_b64(cls, b64_data: str) -> "CalibrationData":
        """Create an instance from base64 encoded JSON string."""
        try:
            data = json.loads(base64.b64decode(b64_data).decode())
            return cls(**{k: v for k, v in data.items()})
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error decoding calibration data: {e}")
            raise ValueError("Invalid calibration data format.") from e

    def to_b64(self) -> str:
        """Convert the instance to a base64 encoded JSON string."""
        return base64.b64encode(json.dumps(self.__dict__).encode()).decode()


def calibrate(
    pixel_ratio: int = 1,
    sleep_time: float = 0.1,
) -> CalibrationData:
    # check that 'top_left.png' exists
    if not os.path.exists("./top_left.png"):
        print("Error: top_left.png not found.")
        sys.exit()

    # locate the image on the screen
    location_A1 = None

    with contextlib.suppress(pyautogui.ImageNotFoundException):
        location_A1 = pyautogui.locateOnScreen("top_left.png", confidence=0.8)

    if location_A1 is None:
        print("Error: top_left.png not found on screen.")
        sys.exit()

    try:
        location_bucket = pyautogui.locateOnScreen("bucket.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        location_bucket = None

    if location_bucket is None:
        print("Error: bucket.png not found on screen.")
        sys.exit()

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
    click(*bucket_location_2)

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

    custom_color = (
        bottom_right_color[0] - 180,
        bottom_right_color[1] + 85,
    )

    pyautogui.moveTo(*custom_color)

    # _click(*top_left_cell)

    # display a message box to check whether we want to proceed
    response = pyautogui.confirm(  # type: ignore[attr-defined]
        text="Was that correct?",
        title="Boxes",
        buttons=["Yes", "No"],
    )

    if response == "No":
        print("Exiting script.")
        sys.exit()

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
        custom_color=custom_color,
        first_row=first_row,
        first_col=first_col,
        cell_width=cell_width,
        cell_height=cell_height,
        n_cols=n_cols,
        n_rows=n_rows,
        n_color_cols=n_color_cols,
        n_color_rows=n_color_rows,
    )
