import math
import random
import time
from itertools import pairwise

import pyautogui

from . import colors, text, utils
from .calibrate import CalibrationData
from .patched_click import click


def inward_spiral(calib: CalibrationData, color: colors.Color) -> None:
    _nodes = "A:1,S:1,S:52,A:52,A:3,Q:3,Q:50,C:50,C:5,O:5,O:48,E:48,E:7,M:7,M:46,G:46,G:9,K:9,K:44,I:44,I:11"
    nodes = _nodes.split(",")

    for n1, n2 in pairwise(nodes):
        utils.select_range(calib, n1, n2)
        color.apply()


def outward_spiral(calib: CalibrationData, color: colors.Color) -> None:
    _nodes = "J:43,J:10,H:10,H:45,L:45,L:8,F:8,F:47,N:47,N:6,D:6,D:49,P:49,P:4,B:4,B:51,R:51,R:2,A:2"
    nodes = _nodes.split(",")

    for n1, n2 in pairwise(nodes):
        utils.select_range(calib, n1, n2)
        color.apply()


################################################################################


def pattern_palette_test_1(calib: CalibrationData) -> None:
    for j in range(calib.n_color_rows):
        for i in range(calib.n_color_cols):
            # print(f"Applying color ({i}, {j})")
            utils.select_range(
                calib,
                (chr(ord("A") + i), 4 * j + 4),
                (chr(ord("A") + i), 4 * j + 4 + 1),
            )
            colors.StandardColor(calib, i, j).apply()
            utils.select_range(
                calib,
                (chr(ord("A") + i), 4 * j + 4 + 2),
                (chr(ord("A") + i), 4 * j + 4 + 3),
            )
            colors.ArbitraryColor(
                calib,
                *colors.StandardColor(calib, i, j).rgb(),
                cache=False,
            ).apply()


def pattern_palette_test_2(calib: CalibrationData) -> None:
    """Apply colors in a pattern to the palette."""

    def _xy_to_rgb(x: float, y: float) -> tuple[int, int, int]:
        """Convert (x, y) coordinates to RGB values."""
        r = int(255 * x)
        g = int(255 * y)
        b = int(255 * (1 - x) * (1 - y))
        return r, g, b

    D = 1
    N_COLS = calib.n_cols // D
    N_ROWS = calib.n_rows // D

    coords = [(i, j) for i in range(N_COLS) for j in range(N_ROWS)]
    # random.shuffle(coords)

    for i, j in coords:
        rgb = _xy_to_rgb(i / (N_COLS - 1), j / (N_ROWS - 1))
        utils.select_range(
            calib,
            (chr(ord("A") + i * D), j * D + 1),
            (chr(ord("A") + i * D + (D - 1)), j * D + (D - 1) + 1),
        )
        colors.ArbitraryColor(calib, *rgb).apply()


def pattern_column_lights(
    calib: CalibrationData,
    color: colors.Color,
    sleep_time: float = 0.1,
) -> None:
    """Apply a color to each cell in a column."""
    column_indices = [i for i in range(calib.n_cols)]
    random.shuffle(column_indices)
    for i in column_indices:
        # select_range(calib, (chr(ord("A") + i), 1), (chr(ord("A") + i), calib.n_rows))
        utils.select_column_index(calib, i)
        color.apply()
        pyautogui.sleep(sleep_time)


def pattern_row_lights(
    calib: CalibrationData,
    color: colors.Color,
    sleep_time: float = 0.1,
) -> None:
    """Apply a color to each cell in a row."""
    row_indices = [i for i in range(calib.n_rows)]
    random.shuffle(row_indices)
    for i in row_indices:
        # select_range(calib, ("A", i + 1), (chr(ord("A") + calib.n_cols - 1), i + 1))
        utils.select_row_index(calib, i)
        color.apply()
        pyautogui.sleep(sleep_time)


def pattern_column_row_lights(
    calib: CalibrationData,
    col_color: colors.Color,
    row_color: colors.Color,
    sleep_time: float = 0.1,
) -> None:
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
                utils.select_column_index(calib, column_indices.pop())
                col_color.apply()
            else:
                # apply rows
                utils.select_row_index(calib, row_indices.pop())
                row_color.apply()

            time.sleep(sleep_time)
    else:
        raise NotImplementedError


def ij_2_uv(calib: CalibrationData, i: int, j: int) -> tuple[float, float]:
    u = i / (calib.n_cols - 1) * 2 - 1
    v = j / (calib.n_rows - 1) * 2 - 1
    return (u, v)


def ij_2_wq(calib: CalibrationData, i: int, j: int) -> tuple[float, float]:
    # w/q coordinates are just like u/v, but the color is in screen coordinates,
    # not image coordinates. This means that the circles are drawn correctly
    cell_width = (calib.x2 - calib.x1) / (calib.n_cols - 1)
    cell_height = (calib.y2 - calib.y1) / (calib.n_rows - 1)
    cell_area_width = calib.n_cols * cell_width
    cell_area_height = calib.n_rows * cell_height
    aspect_ratio = cell_area_width / cell_area_height
    if aspect_ratio > 1:
        # Wider than tall
        w = (i / (calib.n_cols - 1) * 2 - 1) * aspect_ratio
        q = j / (calib.n_rows - 1) * 2 - 1
    else:
        # Taller than wide
        w = i / (calib.n_cols - 1) * 2 - 1
        q = (j / (calib.n_rows - 1) * 2 - 1) / aspect_ratio
    return (w, q)


def pattern_cells(
    calib: CalibrationData,
    color: colors.Color,
    sleep_time: float = 0.1,
) -> None:
    """Apply a color to each cell in the grid."""
    # coords = [(i, j) for i in range(calib.n_cols) for j in range(calib.n_rows)]
    # random.shuffle(coords)

    def _probability(i: int, j: int) -> float:
        # potability based on a gaussian distribution centered in the middle of the grid
        w, q = ij_2_wq(calib, i, j)
        return math.exp(-((w**2 + q**2) / (2 * (0.5**2))))

    def _color(i: int, j: int) -> tuple[int, int, int]:
        # color.uv(*ij_2_uv(calib, i, j))
        # color.wq(*ij_2_wq(calib, i, j))
        return color.rgb()

    coords_with_probs_and_color = [
        (i, j, _probability(i, j), _color(i, j)) for i in range(calib.n_cols) for j in range(calib.n_rows)
    ]

    def _color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
        """Calculate the Euclidean distance between two RGB colors."""
        return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)

    # group by color
    coords_with_probs: dict[tuple[int, int, int], list[tuple[int, int, float]]] = {}
    distance_tol = 10
    for i, j, prob, color_rgb in coords_with_probs_and_color:
        # Check if the color is already in the dictionary
        found = False
        for existing_color in coords_with_probs:
            if _color_distance(existing_color, color_rgb) < distance_tol:
                coords_with_probs[existing_color].append((i, j, prob))
                found = True
                break
        if not found:
            coords_with_probs[color_rgb] = [(i, j, prob)]

    # shuffle the colors in each group
    for color_rgb in coords_with_probs:
        random.shuffle(coords_with_probs[color_rgb])

    # max_prob = max(prob for _, _, prob in coords_with_probs)
    # # Normalize probabilities to be between 0 and 1
    # coords_with_probs = deque(
    #     (i, j, prob / max_prob) for i, j, prob in coords_with_probs
    # )

    # Group by color

    # Sort by probability in descending order
    # coords_with_probs = deque(
    #     sorted(coords_with_probs, key=lambda x: x[2], reverse=True)
    # )

    # # Shuffle the coordinates with probabilities
    # random.shuffle(coords_with_probs)

    # coords = []
    # while coords_with_probs:
    #     i, j, prob = coords_with_probs.popleft()
    #     if random.random() < prob:
    #         coords.append((i, j))
    #     else:
    #         # Reinsert the item at the end of the deque with the same probability
    #         coords_with_probs.append((i, j, prob))

    # for i, j in coords:
    #     click(*cell_coords(calib, (i, j)))
    #     color.uv(*ij_2_uv(calib, i, j))
    #     color.wq(*ij_2_wq(calib, i, j))
    #     color.apply()
    #     pyautogui.sleep(sleep_time)

    for color_rgb, coords in coords_with_probs.items():
        just_coords = [(i, j) for i, j, _ in coords]
        for i, j in just_coords:
            click(*utils.cell_coords(calib, (i, j)))
            # print(f"Applying color {color_rgb} to cell ({i}, {j})")
            colors.ArbitraryColor(calib, *color_rgb).apply()
            pyautogui.sleep(sleep_time)


################################################################################


def run(calib: CalibrationData) -> None:
    colors.reset_all_colors(calib)
    text.reset_all_cell_contents(calib)
    time.sleep(0.1)

    # pyautogui.PAUSE = 0.0
    pyautogui.PAUSE = 0.03

    # click(*cell_coords(calib, "G:10"))
    # ArbitraryColor(calib, 255, 0, 0).apply()

    # while True:
    #     inward_spiral(calib, RandomChangingColor(calib))
    #     outward_spiral(calib, RandomOnceColor(calib))

    # pattern_cells(calib, RandomChangingColor(calib), sleep_time=0.0)
    # pattern_cells(
    #     calib,
    #     # colors.RadialColor(
    #     #     calib,
    #     #     center=(255, 0, 0),  # red
    #     #     edge=(128, 128, 128),  # gray
    #     #     radius=1.5,
    #     # ),
    #     # colors.RandomChangingColor(calib),
    #     colors.StandardColor.from_name(calib, "lime"),
    #     sleep_time=0.0,
    # )

    # Test pattern
    pattern_palette_test_1(calib)
    # pattern_palette_test_2(calib)

    # column_lights(calib, random_color(calib))
    # reset_all_colors(calib)
    # row_lights(calib, random_color(calib))
    # reset_all_colors(calib)

    # while True:
    #     column_row_lights(calib, random_color(calib), random_color(calib), sleep_time=0)
    #     # reset_all_colors(calib)

    # Clean up a tiny bit
    # select_range(calib, "A:1", "D:4")
    # NoFillColor(calib).apply()
    # click(*cell_coords(calib, "A:1"))
