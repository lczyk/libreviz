import base64
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import pyautogui

from .patched_click import click


@dataclass(frozen=True)
class CalibrationData:
    top_left: tuple[float, float]  # (x, y) coordinates of the top left cell
    bottom_right: tuple[float, float]  # (x, y) coordinates of
    last_bucket: tuple[float, float]  # (x, y) coordinates of the last bucket icon
    open_bucket: tuple[float, float]  # (x, y) coordinates of the bucket icon

    color_no_fill: tuple[float, float]  # (x, y) coordinates of the no fill button
    color_top_left: tuple[float, float]  # (x, y) coordinates of the top left color cell
    color_bottom_right: tuple[float, float]  # (x, y) coordinates of the bottom right color cell
    # cx1: int
    # cy1: int
    # cx2: int
    # cy2: int
    # cx3: int
    # cy3: int

    custom_color: tuple[float, float]  # (x, y) coordinates of the custom color button

    cell_width: float
    cell_height: float

    color_cell_width: float
    color_cell_height: float

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
    targets_dir: Path,
    pixel_ratio: int = 1,
    sleep_time: float = 0.1,
) -> CalibrationData:
    # check that 'top_left.png' exists

    _targets = {
        "top_left": targets_dir / "top_left.png",
        "bucket": targets_dir / "bucket.png",
    }
    for name, path in _targets.items():
        if not path.exists():
            print(f"Error: {name}.png not found in {targets_dir}.")
            sys.exit()

    targets = {k: str(v) for k, v in _targets.items()}

    # locate the image on the screen

    try:
        location_A1 = pyautogui.locateOnScreen(
            targets["top_left"],
            confidence=0.8,
        )
    except pyautogui.ImageNotFoundException:
        location_A1 = None

    if location_A1 is None:
        print("Error: top_left.png not found on screen.")
        sys.exit()

    try:
        location_bucket = pyautogui.locateOnScreen(
            targets["bucket"],
            confidence=0.8,
        )
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

    color_cell_width = (bottom_right_color[0] - top_left_color[0]) / (n_color_cols - 1)
    color_cell_height = (bottom_right_color[1] - top_left_color[1]) / (n_color_rows - 1)
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
        top_left=top_left_cell,
        bottom_right=bottom_right_cell,
        last_bucket=(
            bucket_location_2[0] - 20,
            bucket_location_2[1],
        ),
        open_bucket=bucket_location_2,
        color_no_fill=no_fill_location,
        color_top_left=top_left_color,
        color_bottom_right=bottom_right_color,
        color_cell_width=color_cell_width,
        color_cell_height=color_cell_height,
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
