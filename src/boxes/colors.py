import random
import time
from collections import deque
from typing import TYPE_CHECKING, Callable, Iterator, Protocol, TypeVar

import more_itertools
import pyautogui

from . import cell
from .calibrate import CalibrationData
from .patched_click import click

ColorName = str
ColorIJ = tuple[int, int]
ColorRGB = tuple[int, int, int]  # RGB color as a tuple of (R, G, B) values
ColorXY = tuple[float, float]  # Coordinates in the color palette as (x, y)


def open_bucket(calib: CalibrationData) -> None:
    """Open the bucket tool in LibreOffice."""
    click(*calib.open_bucket)


def standard_color_coords(calib: CalibrationData, c: ColorIJ) -> ColorXY:
    """Move to the specified color cell in the color palette."""
    return (
        calib.color_top_left[0] + calib.color_cell_width * c[0],
        calib.color_top_left[1] + calib.color_cell_height * c[1],
    )


class Color(Protocol):
    # Colors know how to apply themselves
    def rgb(self) -> ColorRGB: ...
    def apply(self) -> None: ...
    def _color(self) -> None: ...  # marker method


class RichColor(Protocol):
    # Rich colors are colors which know *where* to apply themselves
    def base(self) -> Color: ...
    def apply(self) -> None: ...
    def _rich_color(self) -> None: ...  # marker method


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
    _finally: Callable[[], None] | None = None,
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
            click(*calib.last_bucket)

        else:
            # TODO: check colors other than the most recent one
            #       thy can be applied from the bucket meny

            # change color
            open_bucket(calib)
            time.sleep(pyautogui.DARWIN_CATCH_UP_TIME * 2)
            f()
            RECENT_COLORS.appendleft(color_rbg)

    if _finally:
        _finally()


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
    "brick": ((3, 1), (255, 64, 0)),
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

YELLOWS: tuple[ColorName, ...] = (
    "light_yellow_4",
    "light_yellow_3",
    "light_yellow_2",
    "light_yellow_1",
    "yellow",
    "dark_yellow_1",
    "dark_yellow_2",
    "dark_yellow_3",
    "dark_yellow_4",
)

GOLDS: tuple[ColorName, ...] = (
    "light_gold_4",
    "light_gold_3",
    "light_gold_2",
    "light_gold_1",
    "gold",
    "dark_gold_1",
    "dark_gold_2",
    "dark_gold_3",
    "dark_gold_4",
)

ORANGES: tuple[ColorName, ...] = (
    "light_orange_4",
    "light_orange_3",
    "light_orange_2",
    "light_orange_1",
    "orange",
    "dark_orange_1",
    "dark_orange_2",
    "dark_orange_3",
    "dark_orange_4",
)

BRICKS: tuple[ColorName, ...] = (
    "light_brick_4",
    "light_brick_3",
    "light_brick_2",
    "light_brick_1",
    "brick",
    "dark_brick_1",
    "dark_brick_2",
    "dark_brick_3",
    "dark_brick_4",
)

REDS: tuple[ColorName, ...] = (
    "light_red_4",
    "light_red_3",
    "light_red_2",
    "light_red_1",
    "red",
    "dark_red_1",
    "dark_red_2",
    "dark_red_3",
    "dark_red_4",
)

MAGENTAS: tuple[ColorName, ...] = (
    "light_magenta_4",
    "light_magenta_3",
    "light_magenta_2",
    "light_magenta_1",
    "magenta",
    "dark_magenta_1",
    "dark_magenta_2",
    "dark_magenta_3",
    "dark_magenta_4",
)

PURPLES: tuple[ColorName, ...] = (
    "light_purple_4",
    "light_purple_3",
    "light_purple_2",
    "light_purple_1",
    "purple",
    "dark_purple_1",
    "dark_purple_2",
    "dark_purple_3",
    "dark_purple_4",
)

INDIGOS: tuple[ColorName, ...] = (
    "light_indigo_4",
    "light_indigo_3",
    "light_indigo_2",
    "light_indigo_1",
    "indigo",
    "dark_indigo_1",
    "dark_indigo_2",
    "dark_indigo_3",
    "dark_indigo_4",
)

BLUES: tuple[ColorName, ...] = (
    "light_blue_4",
    "light_blue_3",
    "light_blue_2",
    "light_blue_1",
    "blue",
    "dark_blue_1",
    "dark_blue_2",
    "dark_blue_3",
    "dark_blue_4",
)

TEALS: tuple[ColorName, ...] = (
    "light_teal_4",
    "light_teal_3",
    "light_teal_2",
    "light_teal_1",
    "teal",
    "dark_teal_1",
    "dark_teal_2",
    "dark_teal_3",
    "dark_teal_4",
)

GREENS: tuple[ColorName, ...] = (
    "light_green_4",
    "light_green_3",
    "light_green_2",
    "light_green_1",
    "green",
    "dark_green_1",
    "dark_green_2",
    "dark_green_3",
    "dark_green_4",
)

LIMES: tuple[ColorName, ...] = (
    "light_lime_4",
    "light_lime_3",
    "light_lime_2",
    "light_lime_1",
    "lime",
    "dark_lime_1",
    "dark_lime_2",
    "dark_lime_3",
    "dark_lime_4",
)

GROUPS: dict[str, tuple[ColorName, ...]] = {
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

    def _apply(self) -> None:
        click(*standard_color_coords(self.calib, (self.ci, self.cj)))

    def apply(self) -> None:
        apply_or_recent(self.calib, self.rgb(), self._apply)

    def _color(self) -> None:
        pass


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
        click(*self.calib.color_no_fill)

    def _color(self) -> None:
        pass


if TYPE_CHECKING:
    _no_fill_color: Color = NoFillColor.__new__(NoFillColor)


def _random_color_ij(
    calib: CalibrationData,
    *,
    avoid_dark: bool = True,
    avoid_white: bool = True,
) -> ColorIJ:
    # all_color_indices = [(ci, cj) for cj in range(calib.n_color_rows) for ci in range(calib.n_color_cols)]
    to_sample = list(STANDARD_COLORS_BY_NAME.keys())

    if avoid_white:
        # Remove the white color (last color in the first row)
        to_sample.remove("white")

    if avoid_dark:

        def _is_dark_color(color_name: ColorName) -> bool:
            """Check if the color is considered dark."""
            if color_name in (
                "black",
                "dark_gray_3",
                "dark_gray_2",
            ):
                return True

            return bool(color_name.startswith("dark_") and color_name.endswith("_4"))

        to_sample = [c for c in to_sample if not _is_dark_color(c)]

    # Randomly select a color from the remaining colors
    sampled_name = random.choice(to_sample)
    sampled_ij = STANDARD_COLORS_BY_NAME[sampled_name][0]
    return sampled_ij


class RandomOnceColor(Color):
    def __init__(
        self,
        calib: CalibrationData,
        *,
        avoid_dark: bool = True,
    ) -> None:
        super().__init__()
        self.calib = calib
        self.color = _random_color_ij(calib, avoid_dark=avoid_dark)

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

    def _color(self) -> None:
        pass


if TYPE_CHECKING:
    _random_once_color: Color = RandomOnceColor.__new__(RandomOnceColor)


class RandomChangingColor(Color):
    def __init__(
        self,
        calib: CalibrationData,
        *,
        avoid_dark: bool = True,
    ) -> None:
        super().__init__()
        self.calib = calib
        self.color_ij = _random_color_ij(calib, avoid_dark=avoid_dark)
        self.avoid_dark = avoid_dark

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the color."""
        return STANDARD_COLORS_MATRIX[self.color_ij[1]][self.color_ij[0]][1]

    def _apply(self) -> None:
        click(*standard_color_coords(self.calib, self.color_ij))

    def apply(self) -> None:
        apply_or_recent(self.calib, self.rgb(), self._apply)
        self.color_ij = _random_color_ij(self.calib, avoid_dark=self.avoid_dark)

    def indices(self) -> "tuple[int, int]":
        """Return the coordinates of the color in the palette."""
        return self.color_ij

    def _color(self) -> None:
        pass


if TYPE_CHECKING:
    _random_changing_color: Color = RandomChangingColor.__new__(RandomChangingColor)


class ArbitraryColor(Color):
    def __init__(
        self,
        calib: CalibrationData,
        r: int,
        g: int,
        b: int,
        *,
        coerce: bool = False,
        cache: bool = True,
    ) -> None:
        super().__init__()
        self.calib = calib
        if not isinstance(r, int) or not isinstance(g, int) or not isinstance(b, int):
            raise TypeError("RGB values must be integers")
        if coerce:
            # Find the closest standard color to the given RGB values
            self.r, self.g, self.b = min(
                STANDARD_COLORS_BY_RGB.keys(),
                key=lambda c: color_distance(c, (r, g, b)),
            )
            self.standard_name = STANDARD_COLORS_BY_RGB[(self.r, self.g, self.b)][0]
        else:
            # Use the provided RGB values directly
            self.r, self.g, self.b = r, g, b
            self.standard_name = ""
        self.cache = cache

    def rgb(self) -> "tuple[int, int, int]":
        return (self.r, self.g, self.b)

    def _apply(self) -> None:
        if self.standard_name != "":
            # If we're using a standard color, apply it directly
            color = StandardColor.from_name(self.calib, self.standard_name)
            color._apply()

        else:
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
            time.sleep(pyautogui.DARWIN_CATCH_UP_TIME * 3)

    def apply(self) -> None:
        apply_or_recent(self.calib, self.rgb(), self._apply, cache=self.cache)

    def _color(self) -> None:
        pass


if TYPE_CHECKING:
    _arbitrary_color: Color = ArbitraryColor.__new__(ArbitraryColor)


class StandardCyclerColor(Color):
    def __init__(
        self,
        calib: CalibrationData,
        palette: tuple[ColorName, ...],
        *,
        offset: int = 0,
        cache: bool = True,
    ) -> None:
        super().__init__()
        self.calib = calib
        self.palette = palette
        if not self.palette:
            raise ValueError("Palette cannot be empty")
        self.current_index = 0 + offset % len(self.palette)
        self.cache = cache

    def rgb(self) -> "tuple[int, int, int]":
        """Return the RGB values of the current color in the palette."""
        color_name = self.palette[self.current_index]
        return STANDARD_COLORS_BY_NAME[color_name][1]

    def _apply(self) -> None:
        """Apply the current color in the palette."""
        color_name = self.palette[self.current_index]
        color = StandardColor.from_name(self.calib, color_name)
        color._apply()

    def _finally(self) -> None:
        self.current_index = (self.current_index + 1) % len(self.palette)

    def apply(self) -> None:
        """Apply the current color in the palette."""
        apply_or_recent(
            self.calib,
            self.rgb(),
            self._apply,
            cache=self.cache,
            _finally=self._finally,
        )

    def _color(self) -> None:
        pass


if TYPE_CHECKING:
    _standard_palette_color: Color = StandardCyclerColor.__new__(StandardCyclerColor)


def reset_all_colors(calib: CalibrationData) -> None:
    """Reset all colors in the grid to 'No Fill'."""
    cell.select_range(
        calib,
        cell.ij2str((0, 0)),
        cell.ij2str((calib.n_cols - 1, calib.n_rows - 1)),
    )
    NoFillColor(calib).apply()


def blend_rgb(c1: ColorRGB, c2: ColorRGB, ratio: float) -> ColorRGB:
    """Blend two RGB colors together based on a ratio."""
    r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
    g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
    b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
    return (r, g, b)


_T = TypeVar("_T")


def group_by_color(
    objects: list[_T],
    color_accessor: Callable[[_T], tuple[int, int, int]],
    distance_tol: int = 10,
    shuffle: bool = False,
) -> dict[tuple[int, int, int], list[_T]]:
    """Group objects by color, using the provided color accessor function."""
    grouped: dict[tuple[int, int, int], list[_T]] = {}
    for obj in objects:
        color_rgb = color_accessor(obj)
        found = False
        for existing_color in grouped:
            if color_distance(existing_color, color_rgb) < distance_tol:
                grouped[existing_color].append(obj)
                found = True
                break
        if not found:
            grouped[color_rgb] = [obj]

    if shuffle:
        for color in grouped:
            random.shuffle(grouped[color])
    return grouped


class ColoredCell:
    def __init__(
        self,
        calib: CalibrationData,
        color: Color,
        cell: cell.CellStr,
    ) -> None:
        self.calib = calib
        self.color = color
        self.cell = cell

    @property
    def cell_coords(self) -> tuple[int, int]:
        """Return the coordinates of the cell as a tuple (ci, cj)."""
        return cell.str2ij(self.cell)

    def base(self) -> Color:
        return self.color

    def apply(self) -> None:
        click(*cell.cell_coords(self.calib, self.cell))
        self.color.apply()

    def _rich_color(self) -> None:
        pass


if TYPE_CHECKING:
    _colored_cell: RichColor = ColoredCell.__new__(ColoredCell)


class ColoredRectangle:
    def __init__(
        self,
        calib: CalibrationData,
        color: Color,
        c1: cell.CellStr,
        c2: cell.CellStr,
    ) -> None:
        self.calib = calib
        self.color = color
        self.c1 = c1
        self.c2 = c2

    def base(self) -> Color:
        return self.color

    def apply(self) -> None:
        cell.select_range(self.calib, self.c1, self.c2)
        self.color.apply()

    def _rich_color(self) -> None:
        pass


if TYPE_CHECKING:
    _colored_rectangle: RichColor = ColoredRectangle.__new__(ColoredRectangle)


def _ij2other(ij: cell.CellIJ, ij_d1: cell.CellIJ, ij_d2: cell.CellIJ) -> list[cell.CellIJ]:
    """
    Given original ij and two directions ij_d1 and ij_d2,
    return the other points which would for a rectangle, as well as the
    antagonist point (the one opposite to the original ij).
    """

    # sanity check. make sure that ij_d1 and ij_d2 have exactly one
    # coordinate in common with ij

    same_x: cell.CellIJ
    if ij[0] == ij_d1[0]:
        same_x = ij_d1
    elif ij[0] == ij_d2[0]:
        same_x = ij_d2
    else:
        raise ValueError(f"ij {ij} does not share x coordinate with ij_d1 {ij_d1} or ij_d2 {ij_d2}")

    same_y: cell.CellIJ
    if ij[1] == ij_d1[1]:
        same_y = ij_d1
    elif ij[1] == ij_d2[1]:
        same_y = ij_d2
    else:
        raise ValueError(f"ij {ij} does not share y coordinate with ij_d1 {ij_d1} or ij_d2 {ij_d2}")

    Dx = same_y[0] - ij[0]
    Dy = same_x[1] - ij[1]

    assert Dx != 0
    assert Dy != 0

    other: list[cell.CellIJ] = []

    dx_range = range(0, Dx + 1, 1) if Dx > 0 else range(0, Dx - 1, -1)
    dy_range = range(0, Dy + 1, 1) if Dy > 0 else range(0, Dy - 1, -1)
    for dx in dx_range:
        for dy in dy_range:
            # NOTE: we don't want the original ij,
            # and we don't want the axes, hence the 'or'
            if dx == 0 or dy == 0:
                continue

            other.append(
                (
                    ij[0] + dx,
                    ij[1] + dy,
                )
            )

    # filter out only the points in the direction perpendicular to d1
    if same_x == ij_d1:  # noqa: SIM108
        # d1 is vertical, so we want horizontal points
        other = [o for o in other if o[1] == ij_d1[1]]
    else:  # same_y == ij_d1:
        other = [o for o in other if o[0] == ij_d1[0]]

    # temp sanity check.
    # we should not be calling this to get no cells back
    assert other

    antagonist = (same_y[0], same_x[1])  # swap the coordinates

    assert other[-1] == antagonist, f"Expected antagonist {antagonist} but got {other[-1]}"

    return other


def simplify_monochrome_colors(
    colors: list[ColoredCell],
    early_stop: bool = False,  # can be used for aesthetic reasons
) -> list[RichColor]:
    """
    Assume we get a list of RichColor objects which we consider to be monochrome.
    """

    # convert to a lookup
    colors_by_ij: dict[ColorIJ, ColoredCell] = {}
    for color in colors:
        ij = color.cell_coords
        if ij in colors_by_ij:
            print(f"Warning: multiple colors at {ij} in {color.cell}")
        else:
            colors_by_ij[ij] = color

    # shuffle
    colors_by_ij = dict(random.sample(colors_by_ij.items(), len(colors_by_ij)))

    def _ij2ij2(ij: cell.CellIJ, direction: str) -> cell.CellIJ:
        if direction == "up":
            ij2 = (ij[0], ij[1] - 1)
        elif direction == "down":
            ij2 = (ij[0], ij[1] + 1)
        elif direction == "left":
            ij2 = (ij[0] - 1, ij[1])
        elif direction == "right":
            ij2 = (ij[0] + 1, ij[1])
        else:
            raise ValueError(f"Unknown direction: {direction}")
        return ij2

    def _shuffle(choices: list[str]) -> Iterator[str]:
        yield from more_itertools.sample(choices, len(choices))

    simplified_colors: list[RichColor] = []
    while colors_by_ij:
        # pick a random color
        ij, color = colors_by_ij.popitem()

        # attempt to expand it to a rectangle
        first_direction: str | None = None
        for direction in _shuffle(["up", "down", "left", "right"]):
            ij_d1 = _ij2ij2(ij, direction)

            if ij_d1 in colors_by_ij:
                first_direction = direction
                break

        if first_direction is None:
            # no direction in which we can expand this color
            simplified_colors.append(color)
            # we already popped this color from the lookup
            continue

        # we found the first direction in which we can expand the color
        ij_d1 = _ij2ij2(ij, first_direction)
        colors_by_ij.pop(ij_d1, None)  # remove the color in the other direction
        # now we can create a rectangle
        rectangle = ColoredRectangle(
            calib=color.calib,
            color=color.base(),
            c1=cell.ij2str(ij),
            c2=cell.ij2str(ij_d1),
        )

        # what about the other direction?
        second_direction: str | None = None
        if first_direction in ["up", "down"]:
            for direction in _shuffle(["left", "right"]):
                _ij_d2 = _ij2ij2(ij, direction)
                _ij_d1_d2 = _ij2ij2(ij_d1, direction)
                if _ij_d2 in colors_by_ij and _ij_d1_d2 in colors_by_ij:
                    second_direction = direction
                    break
        else:  # first_direction in ["left", "right"]:
            for direction in _shuffle(["up", "down"]):
                _ij_d2 = _ij2ij2(ij, direction)
                _ij_d1_d2 = _ij2ij2(ij_d1, direction)
                if _ij_d2 in colors_by_ij and _ij_d1_d2 in colors_by_ij:
                    second_direction = direction
                    break

        if second_direction is None:
            while True:
                ij_d1 = _ij2ij2(ij_d1, first_direction)
                if ij_d1 not in colors_by_ij:
                    break
                colors_by_ij.pop(ij_d1, None)  # remove the color in the other direction
                rectangle.c2 = cell.ij2str(ij_d1)  # expand the rectangle

        else:
            # we can definitely expand in the second direction once
            ij_d2 = _ij2ij2(ij, second_direction)
            ij_d1_d2 = _ij2ij2(ij_d1, second_direction)
            colors_by_ij.pop(ij_d2, None)
            colors_by_ij.pop(ij_d1_d2, None)
            rectangle.c2 = cell.ij2str(ij_d1_d2)

            # try to expand in the first direction as much as possible
            while True:
                _ij_d1 = _ij2ij2(ij_d1, first_direction)
                if _ij_d1 not in colors_by_ij:
                    break
                _ij_d1_d2 = _ij2ij2(ij_d1_d2, first_direction)
                if _ij_d1_d2 not in colors_by_ij:
                    break

                ij_d1, ij_d1_d2 = _ij_d1, _ij_d1_d2
                colors_by_ij.pop(ij_d1, None)
                colors_by_ij.pop(ij_d1_d2, None)
                rectangle.c2 = cell.ij2str(ij_d1_d2)

            # try to expand in the second direction
            # NOTE: now we actually need to keep track of cells other than
            # the extra ij_d1_d2
            while True:
                _ij_d2 = _ij2ij2(ij_d2, second_direction)
                if _ij_d2 not in colors_by_ij:
                    # print("_ij_d2 not in colors")
                    break
                _ij_d1_d2 = _ij2ij2(_ij_d1_d2, second_direction)
                if _ij_d1_d2 not in colors_by_ij:
                    # print("_ij_d1_d2 not in colors")
                    break

                _ij_between: list[cell.CellIJ] = []
                if _ij_d2[0] == _ij_d1_d2[0]:
                    for i in range(_ij_d2[1], _ij_d1_d2[1], 1 if _ij_d1_d2[1] > _ij_d2[1] else -1):
                        _ij_between.extend([(_ij_d2[0], i)])
                else:
                    assert _ij_d2[1] == _ij_d1_d2[1]
                    for i in range(_ij_d2[0], _ij_d1_d2[0], 1 if _ij_d1_d2[0] > _ij_d2[0] else -1):
                        _ij_between.extend([(i, _ij_d2[1])])

                _break = False
                for _ij in _ij_between:
                    if _ij not in colors_by_ij:
                        _break = True
                        break
                if _break:
                    break

                ij_d2, ij_d1_d2 = _ij_d2, _ij_d1_d2
                colors_by_ij.pop(ij_d2, None)
                colors_by_ij.pop(ij_d1_d2, None)
                for _ij in _ij_between:
                    colors_by_ij.pop(_ij, None)
                rectangle.c2 = cell.ij2str(ij_d1_d2)

            if early_stop:
                # if we want to stop early, we can just skip the expansion
                # in the opposite direction
                simplified_colors.append(rectangle)
                continue

            # now try to expand in the direction opposite to the first direction
            first_direction_opposite: str
            if first_direction == "up":
                first_direction_opposite = "down"
            elif first_direction == "down":
                first_direction_opposite = "up"
            elif first_direction == "left":
                first_direction_opposite = "right"
            else:  # first_direction == "right":
                first_direction_opposite = "left"

            # initialize the points used for the expansion
            ij_d3 = ij
            ij_d2_d3 = ij_d2

            while True:
                _ij_d3 = _ij2ij2(ij_d3, first_direction_opposite)
                if _ij_d3 not in colors_by_ij:
                    break
                _ij_d2_d3 = _ij2ij2(ij_d2_d3, first_direction_opposite)
                if _ij_d2_d3 not in colors_by_ij:
                    break

                _ij_between = []
                if _ij_d3[0] == _ij_d2_d3[0]:
                    for i in range(_ij_d3[1], _ij_d2_d3[1], 1 if _ij_d2_d3[1] > _ij_d3[1] else -1):
                        _ij_between.extend([(_ij_d3[0], i)])
                else:
                    assert _ij_d3[1] == _ij_d2_d3[1]
                    for i in range(_ij_d3[0], _ij_d2_d3[0], 1 if _ij_d2_d3[0] > _ij_d3[0] else -1):
                        _ij_between.extend([(i, _ij_d3[1])])

                _break = False
                for _ij in _ij_between:
                    if _ij not in colors_by_ij:
                        _break = True
                        break
                if _break:
                    break

                ij_d3, ij_d2_d3 = _ij_d3, _ij_d2_d3
                colors_by_ij.pop(ij_d3, None)
                colors_by_ij.pop(ij_d2_d3, None)
                for _ij in _ij_between:
                    colors_by_ij.pop(_ij, None)
                rectangle.c1 = cell.ij2str(ij_d3)

            # finally expand in the direction opposite to the second direction
            second_direction_opposite: str
            if second_direction == "up":
                second_direction_opposite = "down"
            elif second_direction == "down":
                second_direction_opposite = "up"
            elif second_direction == "left":
                second_direction_opposite = "right"
            else:  # second_direction == "right":
                second_direction_opposite = "left"

            while True:
                _ij_d3 = _ij2ij2(ij_d3, second_direction_opposite)
                if _ij_d3 not in colors_by_ij:
                    break
                _ij_d1 = _ij2ij2(ij_d1, second_direction_opposite)
                if _ij_d1 not in colors_by_ij:
                    break

                _ij_between = []
                if _ij_d3[0] == _ij_d1[0]:
                    for i in range(_ij_d3[1], _ij_d1[1], 1 if _ij_d1[1] > _ij_d3[1] else -1):
                        _ij_between.extend([(_ij_d3[0], i)])
                else:
                    assert _ij_d3[1] == _ij_d1[1]
                    for i in range(_ij_d3[0], _ij_d1[0], 1 if _ij_d1[0] > _ij_d3[0] else -1):
                        _ij_between.extend([(i, _ij_d3[1])])

                _break = False
                for _ij in _ij_between:
                    if _ij not in colors_by_ij:
                        _break = True
                        break
                if _break:
                    break

                ij_d3, ij_d1 = _ij_d3, _ij_d1
                colors_by_ij.pop(ij_d3, None)
                colors_by_ij.pop(ij_d1, None)
                for _ij in _ij_between:
                    colors_by_ij.pop(_ij, None)
                rectangle.c1 = cell.ij2str(ij_d3)

        # add the rectangle to the list of simplified colors
        simplified_colors.append(rectangle)

    return simplified_colors
