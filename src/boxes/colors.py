import math
import random
import time
from collections import deque
from typing import TYPE_CHECKING, Callable, Protocol

import pyautogui

if __package__ is None or __package__ == "":
    import utils
    from calibrate import CalibrationData
    from patched_click import click
else:
    from . import utils
    from .calibrate import CalibrationData
    from .patched_click import click


def open_bucket(calib: CalibrationData):
    """Open the bucket tool in LibreOffice."""
    click(calib.bx, calib.by)


def color_coords(calib: CalibrationData, c: "tuple[int, int]"):
    """Move to the specified color cell in the color palette."""
    width = calib.cx3 - calib.cx2
    height = calib.cy3 - calib.cy2
    color_cell_width = width / (calib.n_color_cols - 1)
    color_cell_height = height / (calib.n_color_rows - 1)
    x = calib.cx2 + color_cell_width * c[0]
    y = calib.cy2 + color_cell_height * c[1]
    return (x, y)


def _random_color(calib: CalibrationData) -> "tuple[int, int]":
    random_color_row = random.randint(0, calib.n_color_rows - 1)
    random_color_col = random.randint(0, calib.n_color_cols - 1)
    return random_color_col, random_color_row


global RECENT_COLORS
RECENT_COLORS = None


def init_last_color(calib: CalibrationData):
    """Initialize the LAST_COLOR variable."""
    global RECENT_COLORS
    RECENT_COLORS = deque(maxlen=calib.n_color_cols)


class Color(Protocol):
    def __init__(self):
        self.u: float = 0.0
        self.v: float = 0.0
        self.w: float = 0.0
        self.q: float = 0.0

    def rgb(self): ...
    def apply(): ...

    def uv(self, u: float, v: float) -> None:
        if u < -1 or u > 1:
            raise ValueError(f"u must be between -1 and 1, got {u}")
        if v < -1 or v > 1:
            raise ValueError(f"v must be between -1 and 1, got {v}")
        self.u = u
        self.v = v

    def wq(self, w: float, q: float) -> None:
        """Set the w/q coordinates for the color."""
        self.w = w
        self.q = q


def apply_or_recent(
    calib: CalibrationData,
    color: "tuple[int, int]",
    f: Callable[[], None],
) -> None:
    global RECENT_COLORS
    if len(RECENT_COLORS) > 0 and RECENT_COLORS[0] == color:
        # apply the same color again
        position = (calib.bx - 20, calib.by)
        click(*position)
    else:
        # change color
        open_bucket(calib)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        f()
        RECENT_COLORS.appendleft(color)


class StandardColor(Color):
    def __init__(self, calib: CalibrationData, color: "tuple[int, int]") -> None:
        super().__init__()
        self.calib = calib
        self.color = color

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the color."""
        raise NotImplementedError("We don't have the lookup table for RGB values for the standard colors yet")

    def apply(self) -> None:
        apply_or_recent(
            self.calib,
            self.color,
            lambda: click(*color_coords(self.calib, self.color)),
        )


if TYPE_CHECKING:
    _: Color = StandardColor()


class NoFillColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        super().__init__()
        self.calib = calib

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the 'No Fill' color."""
        raise ValueError("No Fill color does not have RGB values, it is a special case.")

    def apply(self) -> None:
        open_bucket(self.calib)
        position = (self.calib.cx1, self.calib.cy1)
        click(*position)


class RandomOnceColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        super().__init__()
        self.calib = calib
        self.color = _random_color(calib)

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the color."""
        raise NotImplementedError("We don't have the lookup table for RGB values for the standard colors yet")

    def apply(self) -> None:
        apply_or_recent(
            self.calib,
            self.color,
            lambda: click(*color_coords(self.calib, self.color)),
        )

    def indices(self) -> "tuple[int, int]":
        """Return the coordinates of the color in the palette."""
        return self.color


class RandomChangingColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        super().__init__()
        self.calib = calib
        self.color = _random_color(calib)

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the color."""
        raise NotImplementedError("We don't have the lookup table for RGB values for the standard colors yet")

    def _apply(self) -> None:
        click(*color_coords(self.calib, _random_color(self.calib)))

    def apply(self) -> None:
        apply_or_recent(self.calib, self.color, self._apply)
        self.color = _random_color(self.calib)  # re-roll

    def indices(self) -> "tuple[int, int]":
        """Return the coordinates of the color in the palette."""
        return self.color


class ArbitraryColor(Color):
    def __init__(self, calib: CalibrationData, r: int, g: int, b: int) -> None:
        super().__init__()
        self.calib = calib
        self.r = r
        self.g = g
        self.b = b

    def _apply(self) -> None:
        click(*self.calib.custom_color)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        pyautogui.typewrite(f"{self.r}")
        pyautogui.press("tab")
        pyautogui.typewrite(f"{self.g}")
        pyautogui.press("tab")
        pyautogui.typewrite(f"{self.b}")
        pyautogui.press("enter")
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)

    def apply(self) -> None:
        apply_or_recent(self.calib, (self.r, self.g, self.b), self._apply)


class RadialColor(Color):
    def __init__(
        self,
        calib: CalibrationData,
        *,
        center: "tuple[int, int, int]",
        edge: "tuple[int, int, int]",
        radius: float = 1.0,
    ) -> None:
        super().__init__()
        self.calib = calib
        self.center = center
        self.edge = edge
        self.radius = radius

    def rgb(self) -> "tuple[int, int, int]":
        r = math.sqrt(self.w**2 + self.q**2)
        if r < self.radius:
            alpha = r / self.radius
            color = (
                int(self.center[0] * (1 - alpha) + self.edge[0] * alpha),
                int(self.center[1] * (1 - alpha) + self.edge[1] * alpha),
                int(self.center[2] * (1 - alpha) + self.edge[2] * alpha),
            )

        else:
            # If the radius is greater than self.radius, just apply the edge color
            color = self.edge

        return color

    def _apply(self) -> None:
        ArbitraryColor(self.calib, *self.rgb())._apply()

    def apply(self) -> None:
        """Apply a radial color based on the center and edge coordinates."""
        apply_or_recent(self.calib, self.rgb(), self._apply)


def reset_all_colors(calib: CalibrationData):
    """Reset all colors in the grid to 'No Fill'."""
    utils.select_range(calib, ("A", 1), ("S", 52))
    NoFillColor(calib).apply()
