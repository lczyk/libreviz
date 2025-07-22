import base64
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pyautogui
from pyscreeze import Box

from . import cell
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

    custom_color: tuple[float, float]  # (x, y) coordinates of the custom color button

    # # (x, y) coordinates of the label cell for the first column and row
    # first_row: tuple[float, float]
    # first_col: tuple[float, float]

    n_cols: int
    n_rows: int
    n_color_cols: int
    n_color_rows: int

    row_settings_location: tuple[float, float]  # (x, y) coordinates of the row settings button
    row_height_location: tuple[float, float]  # (x, y) coordinates of the row height input field
    column_settings_location: tuple[float, float]  # (x, y) coordinates of the column settings button
    column_width_location: tuple[float, float]  # (x, y) coordinates of the column width input field

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

    @property
    def cell_width(self) -> float:
        """Width of a single cell."""
        return abs(self.bottom_right[0] - self.top_left[0]) / (self.n_cols - 1)

    @property
    def cell_height(self) -> float:
        """Height of a single cell."""
        return abs(self.bottom_right[1] - self.top_left[1]) / (self.n_rows - 1)

    @property
    def color_cell_width(self) -> float:
        """Width of a single color cell."""
        return (self.color_bottom_right[0] - self.color_top_left[0]) / (self.n_color_cols - 1)

    @property
    def color_cell_height(self) -> float:
        """Height of a single color cell."""
        return (self.color_bottom_right[1] - self.color_top_left[1]) / (self.n_color_rows - 1)

    @property
    def first_row(self) -> tuple[float, float]:
        """Coordinates of the first row label cell."""
        # go to the center left of top_left_cell
        first_row = (
            self.top_left[0] - self.cell_width / 2,
            self.top_left[1],
        )
        # adjust the x coordinate to be half of the cell width
        # to land on the center of the first row label
        first_row = (first_row[0] - first_row[0] / 2, first_row[1])
        return first_row

    @property
    def first_col(self) -> tuple[float, float]:
        """Coordinates of the first column label cell."""
        return (
            self.top_left[0],
            self.top_left[1] - self.cell_height,
        )


def locate(
    target: str,
    confidence: float = 0.8,
    grayscale: bool = False,
) -> Box | None:
    box = None
    try:  # noqa: SIM105
        box = pyautogui.locateOnScreen(
            target,
            confidence=confidence,
            grayscale=grayscale,
        )
    except pyautogui.ImageNotFoundException:
        pass

    return box


def _row_column_to_locations(
    box: Box,
    pixel_ratio: int = 1,
) -> tuple[tuple[float, float], ...]:
    row_settings_location = (
        box.left / pixel_ratio + 0.25 * box.width / pixel_ratio,
        box.top / pixel_ratio + 0.5 * box.height / pixel_ratio,
    )
    row_height_location = (
        row_settings_location[0],
        row_settings_location[1] + 120 / pixel_ratio,
    )
    column_settings_location = (
        box.left / pixel_ratio + 0.75 * box.width / pixel_ratio,
        box.top / pixel_ratio + 0.5 * box.height / pixel_ratio,
    )
    column_width_location = (
        column_settings_location[0],
        column_settings_location[1] + 120 / pixel_ratio,
    )
    return (
        row_settings_location,
        row_height_location,
        column_settings_location,
        column_width_location,
    )


def _top_left_to_corners(
    box: Box,
    screen_size: pyautogui.Size,
    pixel_ratio: int = 1,
) -> tuple[tuple[float, float], ...]:
    # top left cell
    top_left_cell = (
        box.left / pixel_ratio + 73,
        box.top / pixel_ratio + box.height / pixel_ratio - 30,
    )

    # top right cell
    top_right_cell = (
        screen_size.width - 105,
        top_left_cell[1],
    )

    # bottom left cell
    bottom_left_cell = (
        top_left_cell[0],
        screen_size.height - 70,
    )

    # bottom right cell
    bottom_right_cell = (
        top_right_cell[0],
        bottom_left_cell[1],
    )

    return (
        top_left_cell,
        top_right_cell,
        bottom_left_cell,
        bottom_right_cell,
    )


def calibrate(
    targets_dir: Path,
    pixel_ratio: int = 1,
    sleep_time: float = 0.1,
) -> CalibrationData:
    # check that 'top_left.png' exists

    _targets = {
        "top_left": targets_dir / "top_left.png",
        "bucket": targets_dir / "bucket.png",
        "row_column": targets_dir / "row_column.png",
    }
    for name, path in _targets.items():
        if not path.exists():
            print(f"Error: {name}.png not found in {targets_dir}.")
            sys.exit()

    targets = {k: str(v) for k, v in _targets.items()}

    # locate the image on the screen
    _locations = {
        "top_left": locate(targets["top_left"], confidence=0.8),
        "bucket": locate(targets["bucket"], confidence=0.8),
        "row_column": locate(targets["row_column"], confidence=0.8),
    }

    for name, location in _locations.items():
        if location is None:
            print(f"Error: {name}.png not found on screen.")
            sys.exit()

    locations = cast(dict[str, Box], _locations)

    (
        row_settings_location,
        row_height_location,
        column_settings_location,
        column_width_location,
    ) = _row_column_to_locations(
        locations["row_column"],
        pixel_ratio=pixel_ratio,
    )

    # screen_size = pyautogui.size()
    # print(f"Screen size: {screen_size}")

    (
        top_left_cell,
        top_right_cell,
        bottom_left_cell,
        bottom_right_cell,
    ) = _top_left_to_corners(
        locations["top_left"],
        pyautogui.size(),
        pixel_ratio=pixel_ratio,
    )

    pyautogui.moveTo(*top_left_cell)
    pyautogui.sleep(sleep_time)
    pyautogui.moveTo(*top_right_cell)
    pyautogui.sleep(sleep_time)
    pyautogui.moveTo(*bottom_left_cell)
    pyautogui.sleep(sleep_time)
    pyautogui.moveTo(*bottom_right_cell)
    pyautogui.sleep(sleep_time)

    n_cols = 19
    n_rows = 52
    n_color_cols = 12
    n_color_rows = 10

    # move to the bucket icon
    bucket_location_2 = (
        locations["bucket"].left / pixel_ratio + 0.85 * locations["bucket"].width / pixel_ratio,
        locations["bucket"].top / pixel_ratio + 0.5 * locations["bucket"].height / pixel_ratio,
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

    # color_cell_width = (bottom_right_color[0] - top_left_color[0]) / (n_color_cols - 1)
    # color_cell_height = (bottom_right_color[1] - top_left_color[1]) / (n_color_rows - 1)
    # _click(*top_left_cell)

    # display a message box to check whether we want to proceed
    response = pyautogui.confirm(  # type: ignore[attr-defined, unused-ignore]
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
        custom_color=custom_color,
        n_cols=n_cols,
        n_rows=n_rows,
        n_color_cols=n_color_cols,
        n_color_rows=n_color_rows,
        row_settings_location=row_settings_location,
        row_height_location=row_height_location,
        column_settings_location=column_settings_location,
        column_width_location=column_width_location,
    )


def reset(
    targets_dir: Path,
    pixel_ratio: int = 1,
) -> None:
    """Reset the cell dimensions to the default values."""

    print("Resetting cell dimensions to default values...")
    row_column_location = locate(str(targets_dir / "row_column.png"), confidence=0.8)
    if row_column_location is None:
        print("Error: row_column.png not found on screen.")
        sys.exit()

    (
        row_settings_location,
        row_height_location,
        column_settings_location,
        column_width_location,
    ) = _row_column_to_locations(
        row_column_location,
        pixel_ratio=pixel_ratio,
    )

    pyautogui.keyDown("command")
    pyautogui.press("a")
    pyautogui.keyUp("command")

    # click on the row settings button
    click(*row_settings_location)
    time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
    click(*row_height_location)
    time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
    for _ in range(10):
        pyautogui.press("delete")
    pyautogui.write(str(cell.DEFAULT_CELL_HEIGHT))
    pyautogui.press("enter")

    click(*column_settings_location)
    time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
    click(*column_width_location)
    time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
    for _ in range(10):
        pyautogui.press("delete")
    pyautogui.write(str(cell.DEFAULT_CELL_WIDTH))
    pyautogui.press("enter")

    # find the top left cell
    top_left_cell_location = locate(str(targets_dir / "top_left_2.png"), confidence=0.8, grayscale=True)
    if top_left_cell_location is None:
        print("Error: top_left.png not found on screen.")
        sys.exit()

    top_left_cell = (
        float(top_left_cell_location.left / pixel_ratio + top_left_cell_location.width / pixel_ratio / 2),
        float(top_left_cell_location.top / pixel_ratio + top_left_cell_location.height / pixel_ratio / 2),
    )
    top_left_cell = (
        top_left_cell[0] + 20,
        top_left_cell[1] + 13,
    )

    # click on A1 cell
    click(*top_left_cell)

    # select all cells
    pyautogui.keyDown("command")
    pyautogui.press("a")
    pyautogui.keyUp("command")

    # press delete to clear the cells
    pyautogui.press("delete")
