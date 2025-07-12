import random
import time
from collections import deque
from typing import TYPE_CHECKING, Callable, Protocol

import pyautogui

# if __package__ is None or __package__ == "":
#     import utils
#     from calibrate import CalibrationData
#     from patched_click import click
# else:
from . import utils
from .calibrate import CalibrationData
from .patched_click import click


def open_bucket(calib: CalibrationData) -> None:
    """Open the bucket tool in LibreOffice."""
    click(calib.bx, calib.by)


def standard_color_coords(calib: CalibrationData, c: "tuple[int, int]") -> "tuple[float, float]":
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


class Color(Protocol):
    def rgb(self) -> tuple[int, int, int]: ...
    def apply(self) -> None: ...


RECENT_COLORS: deque["tuple[int, int, int]"] = deque(maxlen=12)


def apply_or_recent(
    calib: CalibrationData,
    color_rbg: "tuple[int, int, int]",
    f: Callable[[], None],
) -> None:
    if len(RECENT_COLORS) > 0 and RECENT_COLORS[0] == color_rbg:
        # apply the same color again
        position = (calib.bx - 20, calib.by)
        click(*position)
    else:
        # change color
        open_bucket(calib)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        f()
        # color.apply
        RECENT_COLORS.appendleft(color_rbg)


ColorName = str
ColorIJ = tuple[int, int]
ColorRGB = tuple[int, int, int]  # RGB color as a tuple of (R, G, B) values

STANDARD_COLORS_BY_NAME: dict[ColorName, tuple[ColorIJ, ColorRGB]] = {
    # 1st row
    "black": ((0, 0), (0, 0, 0)),
    "dark_gray_4": ((1, 0), (17, 17, 17)),
    "dark_gray_3": ((2, 0), (28, 28, 28)),
    "dark_gray_2": ((3, 0), (51, 51, 51)),
    "dark_gray_1": ((4, 0), (102, 102, 102)),
    "gray": ((5, 0), (128, 128, 128)),
    "light_gray_1": ((6, 0), (153, 153, 153)),
    "light_gray_2": ((7, 0), (178, 178, 178)),
    "light_gray_3": ((8, 0), (204, 204, 204)),
    "light_gray_4": ((9, 0), (221, 221, 221)),
    "light_gray_5": ((10, 0), (238, 238, 238)),
    "white": ((11, 0), (255, 255, 255)),
    # 2nd row
    "yellow": ((0, 1), (255, 255, 0)),
    "gold": ((1, 1), (255, 191, 0)),
    "orange": ((2, 1), (255, 128, 0)),
    "brick:": ((3, 1), (255, 64, 0)),
    "red": ((4, 1), (255, 0, 0)),
    "magenta": ((5, 1), (191, 0, 65)),
    "purple": ((6, 1), (128, 0, 128)),
    "indigo": ((7, 1), (85, 48, 141)),
    "blue": ((8, 1), (42, 96, 153)),
    "teal": ((9, 1), (21, 132, 102)),
    "green": ((10, 1), (0, 169, 51)),
    "lime": ((11, 1), (129, 212, 26)),
    # 3rd row
}

STANDARD_COLORS_BY_RGB: dict[ColorRGB, tuple[ColorName, ColorIJ]] = {}
for name, (ij, rgb) in STANDARD_COLORS_BY_NAME.items():
    if rgb in STANDARD_COLORS_BY_RGB:
        raise ValueError(
            f"Duplicate RGB value {rgb} for color {name} at indices {ij} and {STANDARD_COLORS_BY_RGB[rgb][0]}"
        )
    STANDARD_COLORS_BY_RGB[rgb] = (name, ij)


max_cj, max_ci = 0, 0
for ij, _ in STANDARD_COLORS_BY_NAME.values():
    ci, cj = ij
    max_cj = max(max_cj, cj)
    max_ci = max(max_ci, ci)


STANDARD_COLORS_MATRIX: list[list[tuple[ColorName, ColorRGB]]] = [
    [("no_fill", (-1, -1, -1))] * (max_ci + 1)  # Initialize with 'No Fill' color
    for _ in range(max_cj + 1)
]

for name, (ij, rgb) in STANDARD_COLORS_BY_NAME.items():
    ci, cj = ij
    if cj < 0 or cj > max_cj or ci < 0 or ci > max_ci:
        raise ValueError(f"Invalid indices ({ci}, {cj}) for color {name}")
    STANDARD_COLORS_MATRIX[cj][ci] = (name, rgb)

print(len(STANDARD_COLORS_MATRIX), "rows")
print(len(STANDARD_COLORS_MATRIX[0]), "columns")
print("0,0", STANDARD_COLORS_MATRIX[0][0])
print("0,1", STANDARD_COLORS_MATRIX[0][1])
print("1,0", STANDARD_COLORS_MATRIX[1][0])
print("1,1", STANDARD_COLORS_MATRIX[1][1])
print("1,11", STANDARD_COLORS_MATRIX[1][11])

#     [
#         ("black", (0, 0, 0)),
#         ("dark_gray_4", (17, 17, 17)),
#         ("dark_gray_3", (28, 28, 28)),
#         ("dark_gray_2", (51, 51, 51)),
#         ("dark_gray_1", (102, 102, 102)),
#         ("gray", (128, 128, 128)),
#         ("light_gray_1", (153, 153, 153)),
#         ("light_gray_2", (178, 178, 178)),
#         ("light_gray_3", (204, 204, 204)),
#         ("light_gray_4", (221, 221, 221)),
#         ("light_gray_5", (238, 238, 238)),
#         ("white", (255, 255, 255)),
#     ],
#     [
#         ("yellow", (255, 255, 0)),
#         ("gold", (255, 191, 0)),
#         ("orange", (255, 128, 0)),
#         ("brick:", (255, 64, 0)),
#         ("red", (255, 0, 0)),
#         ("magenta", (191, 0, 65)),
#         ("purple", (128, 0, 128)),
#         ("indigo", (85, 48, 141)),
#         ("blue", (42, 96, 153)),
#         ("teal", (21, 132, 102)),
#         ("green", (0, 169, 51)),
#         ("lime", (129, 212, 26)),
#     ],
#     # Add more rows as needed
# ]


class StandardColor:
    def __init__(self, calib: CalibrationData, ci: int, cj: int) -> None:
        super().__init__()
        self.calib = calib
        self.ci = ci
        self.cj = cj

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the color."""
        # raise NotImplementedError("We don't have the lookup table for RGB values for the standard colors yet")
        return STANDARD_COLORS_MATRIX[self.cj][self.ci][1]

    def name(self) -> str:
        """Return the name of the color."""
        return STANDARD_COLORS_MATRIX[self.cj][self.ci][0]

    @classmethod
    def from_name(cls, calib: CalibrationData, name: str) -> "StandardColor":
        """Create a StandardColor from its name."""
        return cls(calib, *STANDARD_COLORS_BY_NAME[name][0])

    def apply(self) -> None:
        apply_or_recent(
            self.calib,
            self.rgb(),
            lambda: click(*standard_color_coords(self.calib, (self.ci, self.cj))),
        )


if TYPE_CHECKING:
    _standard_color: Color = StandardColor.__new__(StandardColor)


class NoFillColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        super().__init__()
        self.calib = calib

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the 'No Fill' color."""
        return (-1, -1, -1)  # Special value for 'No Fill'

    def apply(self) -> None:
        open_bucket(self.calib)
        position = (self.calib.cx1, self.calib.cy1)
        click(*position)


if TYPE_CHECKING:
    _no_fill_color: Color = NoFillColor.__new__(NoFillColor)


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
            self.rgb(),
            lambda: click(*standard_color_coords(self.calib, self.color)),
        )

    def indices(self) -> "tuple[int, int]":
        """Return the coordinates of the color in the palette."""
        return self.color


if TYPE_CHECKING:
    _random_once_color: Color = RandomOnceColor.__new__(RandomOnceColor)


class RandomChangingColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        super().__init__()
        self.calib = calib
        self.color = _random_color(calib)

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the color."""
        raise NotImplementedError("We don't have the lookup table for RGB values for the standard colors yet")

    def _apply(self) -> None:
        click(*standard_color_coords(self.calib, _random_color(self.calib)))

    def apply(self) -> None:
        apply_or_recent(self.calib, self.rgb(), self._apply)
        self.color = _random_color(self.calib)  # re-roll

    def indices(self) -> "tuple[int, int]":
        """Return the coordinates of the color in the palette."""
        return self.color


if TYPE_CHECKING:
    _random_changing_color: Color = RandomChangingColor.__new__(RandomChangingColor)


class ArbitraryColor(Color):
    def __init__(self, calib: CalibrationData, r: int, g: int, b: int) -> None:
        super().__init__()
        self.calib = calib
        if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
            raise TypeError("RGB values must be integers")
        self.r = r
        self.g = g
        self.b = b

    def rgb(self) -> "tuple[int, int, int]":
        return (self.r, self.g, self.b)

    def _apply(self) -> None:
        # TODO: check if we're in standard colors
        click(*self.calib.custom_color)
        # time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        pyautogui.press("delete")
        pyautogui.press("delete")
        pyautogui.press("delete")
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        pyautogui.typewrite(f"{self.r}")
        # time.sleep(10.0)
        pyautogui.press("tab")
        # pyautogui.keyDown("ctrl")
        # pyautogui.typewrite("a")
        # pyautogui.keyUp("ctrl")
        # time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        pyautogui.typewrite(f"{self.g}")
        pyautogui.press("tab")
        # pyautogui.keyDown("ctrl")
        # pyautogui.typewrite("a")
        # pyautogui.keyUp("ctrl")
        # time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        pyautogui.typewrite(f"{self.b}")
        pyautogui.press("enter")
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)

    def apply(self) -> None:
        apply_or_recent(self.calib, self.rgb(), self._apply)


if TYPE_CHECKING:
    _arbitrary_color: Color = ArbitraryColor.__new__(ArbitraryColor)


# class RadialColor(Color):
#     def __init__(
#         self,
#         calib: CalibrationData,
#         *,
#         center: "tuple[int, int, int]",
#         edge: "tuple[int, int, int]",
#         radius: float = 1.0,
#     ) -> None:
#         super().__init__()
#         self.calib = calib
#         self.center = center
#         self.edge = edge
#         self.radius = radius

#     def rgb(self) -> tuple[int, int, int]:
#         r = math.sqrt(self.w**2 + self.q**2)
#         if r < self.radius:
#             alpha = r / self.radius
#             color = (
#                 int(self.center[0] * (1 - alpha) + self.edge[0] * alpha),
#                 int(self.center[1] * (1 - alpha) + self.edge[1] * alpha),
#                 int(self.center[2] * (1 - alpha) + self.edge[2] * alpha),
#             )

#         else:
#             # If the radius is greater than self.radius, just apply the edge color
#             color = self.edge

#         return color

#     def _apply(self) -> None:
#         ArbitraryColor(self.calib, *self.rgb())._apply()

#     def apply(self) -> None:
#         """Apply a radial color based on the center and edge coordinates."""
#         apply_or_recent(self.calib, self.rgb(), self._apply)


def reset_all_colors(calib: CalibrationData) -> None:
    """Reset all colors in the grid to 'No Fill'."""
    utils.select_range(calib, ("A", 1), ("S", 52))
    NoFillColor(calib).apply()
