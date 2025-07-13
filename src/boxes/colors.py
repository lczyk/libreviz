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

ColorName = str
ColorIJ = tuple[int, int]
ColorRGB = tuple[int, int, int]  # RGB color as a tuple of (R, G, B) values
ColorXY = tuple[float, float]  # Coordinates in the color palette as (x, y)


def open_bucket(calib: CalibrationData) -> None:
    """Open the bucket tool in LibreOffice."""
    click(calib.bx, calib.by)


def standard_color_coords(calib: CalibrationData, c: ColorIJ) -> ColorXY:
    """Move to the specified color cell in the color palette."""
    width = calib.cx3 - calib.cx2
    height = calib.cy3 - calib.cy2
    color_cell_width = width / (calib.n_color_cols - 1)
    color_cell_height = height / (calib.n_color_rows - 1)
    x = calib.cx2 + color_cell_width * c[0]
    y = calib.cy2 + color_cell_height * c[1]
    return (x, y)


class Color(Protocol):
    def rgb(self) -> ColorRGB: ...
    def apply(self) -> None: ...


RECENT_COLORS: deque[ColorRGB] = deque(maxlen=12)


def color_distance(c1: ColorRGB, c2: ColorRGB) -> float:
    """Manhattan distance between two RGB colors."""
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2])


def apply_or_recent(
    calib: CalibrationData,
    color_rbg: "tuple[int, int, int]",
    f: Callable[[], None],
    *,
    tolerance: int = 0,  # tolerance for color matching
    cache: bool = True,
) -> None:
    if not cache:
        # if cache is disabled act as if the color is not in the recent colors
        open_bucket(calib)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME * 2)
        f()

        if len(RECENT_COLORS) > 0 and color_distance(RECENT_COLORS[0], color_rbg) > tolerance:
            RECENT_COLORS.appendleft(color_rbg)

    else:
        if len(RECENT_COLORS) > 0 and color_distance(RECENT_COLORS[0], color_rbg) <= tolerance:
            # we're matching the most recent color
            # apply the same color again
            position = (calib.bx - 20, calib.by)
            click(*position)

        else:
            # TODO: check colors other than the most recent one
            #       thy can be applied from the bucket meny

            # change color
            open_bucket(calib)
            time.sleep(pyautogui.DARWIN_CATCH_UP_TIME * 2)
            f()
            RECENT_COLORS.appendleft(color_rbg)


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
    "light_yellow_4": ((0, 2), (255, 255, 215)),
    "light_gold_4": ((1, 2), (255, 245, 206)),
    "light_orange_4": ((2, 2), (255, 219, 182)),
    "light_brick_4": ((3, 2), (255, 216, 206)),
    "light_red_4": ((4, 2), (255, 215, 215)),
    "light_magenta_4": ((5, 2), (247, 209, 213)),
    "light_purple_4": ((6, 2), (224, 194, 205)),
    "light_indigo_4": ((7, 2), (222, 220, 230)),
    "light_blue_4": ((8, 2), (222, 230, 239)),
    "light_teal_4": ((9, 2), (222, 231, 229)),
    "light_green_4": ((10, 2), (221, 232, 203)),
    "light_lime_4": ((11, 2), (246, 249, 212)),
    # 4th row
    "light_yellow_3": ((0, 3), (255, 255, 166)),
    "light_gold_3": ((1, 3), (255, 233, 148)),
    "light_orange_3": ((2, 3), (255, 182, 108)),
    "light_brick_3": ((3, 3), (255, 170, 149)),
    "light_red_3": ((4, 3), (255, 166, 166)),
    "light_magenta_3": ((5, 3), (236, 155, 164)),
    "light_purple_3": ((6, 3), (191, 129, 158)),
    "light_indigo_3": ((7, 3), (183, 179, 202)),
    "light_blue_3": ((8, 3), (180, 199, 220)),
    "light_teal_3": ((9, 3), (179, 202, 199)),
    "light_green_3": ((10, 3), (175, 208, 149)),
    "light_lime_3": ((11, 3), (232, 242, 161)),
    # 5th row
    "light_yellow_2": ((0, 4), (255, 255, 109)),
    "light_gold_2": ((1, 4), (255, 222, 89)),
    "light_orange_2": ((2, 4), (255, 151, 47)),
    "light_brick_2": ((3, 4), (255, 123, 89)),
    "light_red_2": ((4, 4), (255, 109, 109)),
    "light_magenta_2": ((5, 4), (225, 97, 115)),
    "light_purple_2": ((6, 4), (161, 70, 126)),
    "light_indigo_2": ((7, 4), (142, 134, 174)),
    "light_blue_2": ((8, 4), (114, 159, 207)),
    "light_teal_2": ((9, 4), (129, 172, 166)),
    "light_green_2": ((10, 4), (119, 188, 101)),
    "light_lime_2": ((11, 4), (212, 234, 107)),
    # 6th row
    "light_yellow_1": ((0, 5), (255, 255, 56)),
    "light_gold_1": ((1, 5), (255, 212, 40)),
    "light_orange_1": ((2, 5), (255, 134, 13)),
    "light_brick_1": ((3, 5), (255, 84, 41)),
    "light_red_1": ((4, 5), (255, 56, 56)),
    "light_magenta_1": ((5, 5), (214, 46, 78)),
    "light_purple_1": ((6, 5), (141, 29, 117)),
    "light_indigo_1": ((7, 5), (107, 94, 155)),
    "light_blue_1": ((8, 5), (89, 131, 176)),
    "light_teal_1": ((9, 5), (80, 147, 138)),
    "light_green_1": ((10, 5), (63, 175, 70)),
    "light_lime_1": ((11, 5), (187, 227, 61)),
    # 7th row
    "dark_yellow_1": ((0, 6), (230, 233, 5)),
    "dark_gold_1": ((1, 6), (232, 162, 2)),
    "dark_orange_1": ((2, 6), (234, 117, 0)),
    "dark_brick_1": ((3, 6), (237, 76, 5)),
    "dark_red_1": ((4, 6), (241, 13, 12)),
    "dark_magenta_1": ((5, 6), (167, 7, 75)),
    "dark_purple_1": ((6, 6), (120, 3, 115)),
    "dark_indigo_1": ((7, 6), (91, 39, 125)),
    "dark_blue_1": ((8, 6), (52, 101, 164)),
    "dark_teal_1": ((9, 6), (22, 130, 83)),
    "dark_green_1": ((10, 6), (6, 154, 46)),
    "dark_lime_1": ((11, 6), (84, 185, 30)),
    # 8th row
    "dark_yellow_2": ((0, 7), (172, 178, 12)),
    "dark_gold_2": ((1, 7), (180, 120, 4)),
    "dark_orange_2": ((2, 7), (184, 92, 0)),
    "dark_brick_2": ((3, 7), (190, 72, 10)),
    "dark_red_2": ((4, 7), (201, 33, 30)),
    "dark_magenta_2": ((5, 7), (134, 17, 65)),
    "dark_purple_2": ((6, 7), (101, 9, 83)),
    "dark_indigo_2": ((7, 7), (85, 33, 91)),
    "dark_blue_2": ((8, 7), (53, 82, 105)),
    "dark_teal_2": ((9, 7), (30, 106, 57)),
    "dark_green_2": ((10, 7), (18, 118, 34)),
    "dark_lime_2": ((11, 7), (70, 138, 26)),
    # 9th row
    "dark_yellow_3": ((0, 8), (112, 110, 12)),
    "dark_gold_3": ((1, 8), (120, 75, 4)),
    "dark_orange_3": ((2, 8), (123, 61, 0)),
    "dark_brick_3": ((3, 8), (129, 55, 9)),
    "dark_red_3": ((4, 8), (141, 40, 30)),
    "dark_magenta_3": ((5, 8), (97, 23, 41)),
    "dark_purple_3": ((6, 8), (78, 16, 45)),
    "dark_indigo_3": ((7, 8), (72, 29, 50)),
    "dark_blue_3": ((8, 8), (56, 61, 60)),
    "dark_teal_3": ((9, 8), (40, 71, 31)),
    "dark_green_3": ((10, 8), (34, 75, 18)),
    "dark_lime_3": ((11, 8), (57, 85, 17)),
    # 10th row
    "dark_yellow_4": ((0, 9), (68, 50, 5)),
    "dark_gold_4": ((1, 9), (71, 39, 2)),
    "dark_orange_4": ((2, 9), (73, 35, 0)),
    "dark_brick_4": ((3, 9), (75, 34, 4)),
    "dark_red_4": ((4, 9), (80, 32, 12)),
    "dark_magenta_4": ((5, 9), (65, 25, 13)),
    "dark_purple_4": ((6, 9), (59, 22, 14)),
    "dark_indigo_4": ((7, 9), (58, 26, 15)),
    "dark_blue_4": ((8, 9), (54, 36, 19)),
    "dark_teal_4": ((9, 9), (48, 39, 9)),
    "dark_green_4": ((10, 9), (46, 39, 6)),
    "dark_lime_4": ((11, 9), (52, 42, 6)),
}


def _init_standard_colors_by_rgb(
    _in: dict[ColorName, tuple[ColorIJ, ColorRGB]],
) -> dict[ColorRGB, tuple[ColorName, ColorIJ]]:
    out: dict[ColorRGB, tuple[ColorName, ColorIJ]] = {}
    for name, (ij, rgb) in _in.items():
        if rgb in out:
            raise ValueError(f"Duplicate RGB value {rgb} for color {name} at indices {ij} and {out[rgb][0]}")
        out[rgb] = (name, ij)
    return out


STANDARD_COLORS_BY_RGB = _init_standard_colors_by_rgb(STANDARD_COLORS_BY_NAME)


def _init_standard_colors_matrix(
    _in: dict[ColorName, tuple[ColorIJ, ColorRGB]],
) -> list[list[tuple[ColorName, ColorRGB]]]:
    """Initialize the standard colors matrix."""
    max_cj, max_ci = 0, 0
    for ij, _ in _in.values():
        ci, cj = ij
        max_cj = max(max_cj, cj)
        max_ci = max(max_ci, ci)

    out: list[list[tuple[ColorName, ColorRGB]]] = [
        [("no_fill", (-1, -1, -1))] * (max_ci + 1)  # Initialize with 'No Fill' color
        for _ in range(max_cj + 1)
    ]

    for name, (ij, rgb) in _in.items():
        ci, cj = ij
        if cj < 0 or cj > max_cj or ci < 0 or ci > max_ci:
            raise ValueError(f"Invalid indices ({ci}, {cj}) for color {name}")
        out[cj][ci] = (name, rgb)

    return out


STANDARD_COLORS_MATRIX = _init_standard_colors_matrix(STANDARD_COLORS_BY_NAME)

# greens = deque(
#         [
#             "light_green_4",
#             "light_green_3",
#             "light_green_2",
#             "light_green_1",
#             "green",
#             "dark_green_1",
#             "dark_green_2",
#             "dark_green_3",
#             "dark_green_4",
#         ]
#     )

#     golds = deque(
#         [
#             "light_gold_4",
#             "light_gold_3",
#             "light_gold_2",
#             "light_gold_1",
#             "gold",
#             "dark_gold_1",
#             "dark_gold_2",
#             "dark_gold_3",
#             "dark_gold_4",
#         ]
#     )

YELLOWS: list[ColorName] = [
    "light_yellow_4",
    "light_yellow_3",
    "light_yellow_2",
    "light_yellow_1",
    "yellow",
    "dark_yellow_1",
    "dark_yellow_2",
    "dark_yellow_3",
    "dark_yellow_4",
]

GOLDS: list[ColorName] = [
    "light_gold_4",
    "light_gold_3",
    "light_gold_2",
    "light_gold_1",
    "gold",
    "dark_gold_1",
    "dark_gold_2",
    "dark_gold_3",
    "dark_gold_4",
]

ORANGES: list[ColorName] = [
    "light_orange_4",
    "light_orange_3",
    "light_orange_2",
    "light_orange_1",
    "orange",
    "dark_orange_1",
    "dark_orange_2",
    "dark_orange_3",
    "dark_orange_4",
]

BRICKS: list[ColorName] = [
    "light_brick_4",
    "light_brick_3",
    "light_brick_2",
    "light_brick_1",
    "brick",
    "dark_brick_1",
    "dark_brick_2",
    "dark_brick_3",
    "dark_brick_4",
]

REDS: list[ColorName] = [
    "light_red_4",
    "light_red_3",
    "light_red_2",
    "light_red_1",
    "red",
    "dark_red_1",
    "dark_red_2",
    "dark_red_3",
    "dark_red_4",
]

MAGENTAS: list[ColorName] = [
    "light_magenta_4",
    "light_magenta_3",
    "light_magenta_2",
    "light_magenta_1",
    "magenta",
    "dark_magenta_1",
    "dark_magenta_2",
    "dark_magenta_3",
    "dark_magenta_4",
]

PURPLES: list[ColorName] = [
    "light_purple_4",
    "light_purple_3",
    "light_purple_2",
    "light_purple_1",
    "purple",
    "dark_purple_1",
    "dark_purple_2",
    "dark_purple_3",
    "dark_purple_4",
]

INDIGOS: list[ColorName] = [
    "light_indigo_4",
    "light_indigo_3",
    "light_indigo_2",
    "light_indigo_1",
    "indigo",
    "dark_indigo_1",
    "dark_indigo_2",
    "dark_indigo_3",
    "dark_indigo_4",
]

BLUES: list[ColorName] = [
    "light_blue_4",
    "light_blue_3",
    "light_blue_2",
    "light_blue_1",
    "blue",
    "dark_blue_1",
    "dark_blue_2",
    "dark_blue_3",
    "dark_blue_4",
]

TEALS: list[ColorName] = [
    "light_teal_4",
    "light_teal_3",
    "light_teal_2",
    "light_teal_1",
    "teal",
    "dark_teal_1",
    "dark_teal_2",
    "dark_teal_3",
    "dark_teal_4",
]

GREENS: list[ColorName] = [
    "light_green_4",
    "light_green_3",
    "light_green_2",
    "light_green_1",
    "green",
    "dark_green_1",
    "dark_green_2",
    "dark_green_3",
    "dark_green_4",
]

LIMES: list[ColorName] = [
    "light_lime_4",
    "light_lime_3",
    "light_lime_2",
    "light_lime_1",
    "lime",
    "dark_lime_1",
    "dark_lime_2",
    "dark_lime_3",
    "dark_lime_4",
]

GROUPS: dict[str, list[ColorName]] = {
    "yellow": YELLOWS,
    "gold": GOLDS,
    "orange": ORANGES,
    "brick": BRICKS,
    "red": REDS,
    "magenta": MAGENTAS,
    "purple": PURPLES,
    "indigo": INDIGOS,
    "blue": BLUES,
    "teal": TEALS,
    "green": GREENS,
    "lime": LIMES,
}


################################################################################
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


def _random_color_ij(calib: CalibrationData) -> ColorIJ:
    random_color_row = random.randint(0, calib.n_color_rows - 1)
    random_color_col = random.randint(0, calib.n_color_cols - 1)
    return random_color_col, random_color_row


class RandomOnceColor(Color):
    def __init__(self, calib: CalibrationData) -> None:
        super().__init__()
        self.calib = calib
        self.color = _random_color_ij(calib)

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
        self.color = _random_color_ij(calib)

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the color."""
        raise NotImplementedError("We don't have the lookup table for RGB values for the standard colors yet")

    def _apply(self) -> None:
        click(*standard_color_coords(self.calib, _random_color_ij(self.calib)))

    def apply(self) -> None:
        apply_or_recent(self.calib, self.rgb(), self._apply)
        self.color = _random_color_ij(self.calib)  # re-roll

    def indices(self) -> "tuple[int, int]":
        """Return the coordinates of the color in the palette."""
        return self.color


if TYPE_CHECKING:
    _random_changing_color: Color = RandomChangingColor.__new__(RandomChangingColor)


class ArbitraryColor(Color):
    def __init__(
        self,
        calib: CalibrationData,
        r: int,
        g: int,
        b: int,
        cache: bool = True,
    ) -> None:
        super().__init__()
        self.calib = calib
        if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
            raise TypeError("RGB values must be integers")
        self.r = r
        self.g = g
        self.b = b
        self.cache = cache

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
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME * 2)

    def apply(self) -> None:
        apply_or_recent(self.calib, self.rgb(), self._apply, cache=self.cache)


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
