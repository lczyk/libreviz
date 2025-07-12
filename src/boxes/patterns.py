import math
import random
import time
from typing import TYPE_CHECKING, Protocol, no_type_check

import pyautogui

from . import colors, utils
from .calibrate import CalibrationData
from .patched_click import click


class Pattern(Protocol):
    name: str

    def step(self) -> None:
        """Perform a single step of the pattern."""
        ...

    def step_all(self) -> None: ...

    @property
    def n_steps(self) -> int:
        """Return the number of steps in the pattern."""
        ...

    @property
    def n_left(self) -> int:
        """Return the number of steps left in the pattern."""
        ...


class _PatternBase:
    @no_type_check
    def step_all(self) -> None:
        """Perform all steps of the pattern."""
        for _ in range(self.n_steps):
            self.step()

    @no_type_check
    def __len__(self) -> int:
        """Return the number of steps in the pattern."""
        return self.n_steps


class InwardSpiral(_PatternBase):
    name = "inward_spiral"

    def __init__(self, calib: CalibrationData, color: colors.Color) -> None:
        self.calib = calib
        self.color = color
        _nodes = "A:1,S:1,S:52,A:52,A:3,Q:3,Q:50,C:50,C:5,O:5,O:48,E:48,E:7,M:7,M:46,G:46,G:9,K:9,K:44,I:44,I:11"
        self.nodes = _nodes.split(",")
        self.i = 0

    def step(self) -> None:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]
        utils.select_range(self.calib, n1, n2)
        self.color.apply()
        self.i += 1

    @property
    def n_steps(self) -> int:
        return len(self.nodes) - 1

    @property
    def n_left(self) -> int:
        return len(self.nodes) - 1 - self.i


if TYPE_CHECKING:
    _inward_spiral: Pattern = InwardSpiral.__new__(InwardSpiral)


class OutwardSpiral(_PatternBase):
    name = "outward_spiral"

    def __init__(self, calib: CalibrationData, color: colors.Color) -> None:
        self.calib = calib
        self.color = color
        _nodes = "J:43,J:10,H:10,H:45,L:45,L:8,F:8,F:47,N:47,N:6,D:6,D:49,P:49,P:4,B:4,B:51,R:51,R:2,A:2"
        self.nodes = _nodes.split(",")
        self.i = 0

    def step(self) -> None:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]
        utils.select_range(self.calib, n1, n2)
        self.color.apply()
        self.i += 1

    @property
    def n_steps(self) -> int:
        return len(self.nodes) - 1

    @property
    def n_left(self) -> int:
        return len(self.nodes) - 1 - self.i


if TYPE_CHECKING:
    _outward_spiral: Pattern = OutwardSpiral.__new__(OutwardSpiral)


# def palette_test_1(calib: CalibrationData) -> None:
#     for j in range(calib.n_color_rows):
#         for i in range(calib.n_color_cols):
#             # print(f"Applying color ({i}, {j})")


class PaletteTest1(_PatternBase):
    name = "palette_test_1"

    def __init__(self, calib: CalibrationData) -> None:
        self.calib = calib
        self.i = 0
        self.j = 0

    def step(self) -> None:
        calib = self.calib
        i, j = self.i, self.j
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

        # Update indices for the next step
        self.i += 1
        if self.i >= calib.n_color_cols:
            self.i = 0
            self.j += 1
            if self.j >= calib.n_color_rows:
                self.j = 0

    @property
    def n_steps(self) -> int:
        return self.calib.n_color_rows * self.calib.n_color_cols

    @property
    def n_left(self) -> int:
        return self.calib.n_color_rows * self.calib.n_color_cols - (self.j * self.calib.n_color_cols + self.i)


if TYPE_CHECKING:
    _palette_test_1: Pattern = PaletteTest1.__new__(PaletteTest1)


def palette_test_2(calib: CalibrationData) -> None:
    """Apply colors in a pattern to the palette."""

    def _xy_to_rgb(x: float, y: float) -> tuple[int, int, int]:
        """Convert (x, y) coordinates to RGB values."""
        r = int(255 * x)
        g = int(255 * y)
        b = int(255 * (1 - x) * (1 - y))
        return r, g, b

    D_ROWS = 4
    D_COLS = 2
    N_COLS = calib.n_cols // D_COLS
    N_ROWS = calib.n_rows // D_ROWS

    coords = [(i, j) for i in range(N_COLS) for j in range(N_ROWS)]
    # random.shuffle(coords)

    for i, j in coords:
        rgb = _xy_to_rgb(i / (N_COLS - 1), j / (N_ROWS - 1))
        utils.select_range(
            calib,
            # (chr(ord("A") + i * D), j * D + 1),
            # (chr(ord("A") + i * D + (D - 1)), j * D + (D - 1) + 1),
            (chr(ord("A") + i * D_COLS), j * D_ROWS + 1),
            (chr(ord("A") + i * D_COLS + (D_COLS - 1)), j * D_ROWS + (D_ROWS - 1) + 1),
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


def pattern_cells(
    calib: CalibrationData,
    color: colors.Color,
    sleep_time: float = 0.1,
) -> None:
    """Apply a color to each cell in the grid."""
    # coords = [(i, j) for i in range(calib.n_cols) for j in range(calib.n_rows)]
    # random.shuffle(coords)

    def _color(i: int, j: int) -> tuple[int, int, int]:
        # color.uv(*ij_2_uv(calib, i, j))
        # color.wq(*ij_2_wq(calib, i, j))
        return color.rgb()

    coords_with_probs_and_color = [(i, j, _color(i, j)) for i in range(calib.n_cols) for j in range(calib.n_rows)]

    def _color_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
        """Calculate the Euclidean distance between two RGB colors."""
        return math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)

    # group by color
    coords_with_probs: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
    distance_tol = 10
    for i, j, color_rgb in coords_with_probs_and_color:
        # Check if the color is already in the dictionary
        found = False
        for existing_color in coords_with_probs:
            if _color_distance(existing_color, color_rgb) < distance_tol:
                coords_with_probs[existing_color].append((i, j))
                found = True
                break
        if not found:
            coords_with_probs[color_rgb] = [(i, j)]

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
        for i, j in coords:
            click(*utils.cell_coords(calib, (i, j)))
            # print(f"Applying color {color_rgb} to cell ({i}, {j})")
            colors.ArbitraryColor(calib, *color_rgb).apply()
            pyautogui.sleep(sleep_time)


def interweave_patterns(patterns: list[Pattern]) -> None:
    """Run all patterns in the list, interleaving their steps. Find out how many steps each pattern has,
    and scale the number of steps taken by each pattern such that they all finish roughtly at the same time."""
    n_steps = [p.n_steps for p in patterns]
    print(f"Number of steps in each pattern: {n_steps}")
    # steps_taken = [0] * len(patterns)

    # the pattern with minimum number of steps will determine the number of blocks of steps taken by each pattern
    min_steps = min(n_steps)

    n_blocks = [math.ceil(n / min_steps) for n in n_steps]
    print(f"Number of blocks for each pattern: {n_blocks}")
    while not all(n == 0 for n in n_blocks):
        # find the pattern with the maximum number of blocks left
        max_index = n_blocks.index(max(n_blocks))

        # step that pattern the required number of times
        for _ in range(
            min(
                min_steps,
                patterns[max_index].n_left,
            )
        ):
            patterns[max_index].step()
        n_blocks[max_index] -= 1

    print("All patterns finished stepping.")
