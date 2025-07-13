import math
import random
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

    def advance(self) -> None:
        """Advance the internal state"""
        ...

    def step_all(self) -> None:
        """Perform all steps of the pattern."""
        ...

    @property
    def n_steps(self) -> int:
        """Return the number of steps in the pattern."""
        ...

    @property
    def current_step(self) -> int:
        """Return the current step index."""
        ...

    def reset(self) -> None:
        """Reset the pattern to its initial state."""
        ...


class _PatternBase:
    @no_type_check
    def step_all(self) -> None:
        """Perform all steps of the pattern."""
        for _ in range(self.n_steps):
            self.step()
            self.advance()

    @no_type_check
    def __len__(self) -> int:
        """Return the number of steps in the pattern."""
        return self.n_steps


class _1DMixin:
    """Mixin for 1D patterns that have a single index."""

    i: int
    Ni: int

    def __init__(self, Ni: int) -> None:
        print(f"Initializing 1D pattern with {Ni} steps.")
        self.Ni = Ni
        self.i = 0

    def reset(self) -> None:
        self.i = 0

    def advance(self) -> None:
        self.i += 1

    @property
    def current_step(self) -> int:
        return self.i

    @property
    def n_steps(self) -> int:
        return self.Ni


class _2DMixin:
    """Mixin for 2D patterns that have two indices."""

    i: int
    j: int
    Ni: int
    Nj: int

    def __init__(self, Ni: int, Nj: int) -> None:
        self.Ni = Ni
        self.Nj = Nj
        self.i = 0
        self.j = 0

    def reset(self) -> None:
        self.i = 0
        self.j = 0

    def advance(self) -> None:
        self.i += 1
        if self.i >= self.Ni:
            self.i = 0
            self.j += 1
            if self.j >= self.Nj:
                self.j = 0

    @property
    def current_step(self) -> int:
        return self.i + self.j * self.Ni

    @property
    def n_steps(self) -> int:
        return self.Ni * self.Nj


class InwardSpiral(_PatternBase, _1DMixin):
    name = "inward_spiral"

    def __init__(self, calib: CalibrationData, color: colors.Color) -> None:
        self.calib = calib
        self.color = color
        _nodes = "A:1,S:1,S:52,A:52,A:3,Q:3,Q:50,C:50,C:5,O:5,O:48,E:48,E:7,M:7,M:46,G:46,G:9,K:9,K:44,I:44,I:11"
        self.nodes = _nodes.split(",")
        super().__init__(len(self.nodes) - 1)
        self.reset()

    def step(self) -> None:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]
        utils.select_range(self.calib, n1, n2)
        self.color.apply()


if TYPE_CHECKING:
    _inward_spiral: Pattern = InwardSpiral.__new__(InwardSpiral)


class OutwardSpiral(_PatternBase, _1DMixin):
    name = "outward_spiral"

    def __init__(self, calib: CalibrationData, color: colors.Color) -> None:
        self.calib = calib
        self.color = color
        _nodes = "J:43,J:10,H:10,H:45,L:45,L:8,F:8,F:47,N:47,N:6,D:6,D:49,P:49,P:4,B:4,B:51,R:51,R:2,A:2"
        self.nodes = _nodes.split(",")
        super().__init__(len(self.nodes) - 1)
        self.reset()

    def step(self) -> None:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]
        utils.select_range(self.calib, n1, n2)
        self.color.apply()


if TYPE_CHECKING:
    _outward_spiral: Pattern = OutwardSpiral.__new__(OutwardSpiral)


# def palette_test_1(calib: CalibrationData) -> None:
#     for j in range(calib.n_color_rows):
#         for i in range(calib.n_color_cols):
#             # print(f"Applying color ({i}, {j})")


class PaletteTest1(_PatternBase, _2DMixin):
    name = "palette_test_1"

    def __init__(self, calib: CalibrationData) -> None:
        self.calib = calib
        super().__init__(calib.n_color_cols, calib.n_color_rows)
        self.reset()

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


if TYPE_CHECKING:
    _palette_test_1: Pattern = PaletteTest1.__new__(PaletteTest1)

# def palette_test_2(calib: CalibrationData) -> None:
#     """Apply colors in a pattern to the palette."""

#     def _xy_to_rgb(x: float, y: float) -> tuple[int, int, int]:
#         """Convert (x, y) coordinates to RGB values."""
#         r = int(255 * x)
#         g = int(255 * y)
#         b = int(255 * (1 - x) * (1 - y))
#         return r, g, b

#     D_ROWS = 4
#     D_COLS = 2
#     N_COLS = calib.n_cols // D_COLS
#     N_ROWS = calib.n_rows // D_ROWS

#     coords = [(i, j) for i in range(N_COLS) for j in range(N_ROWS)]
#     # random.shuffle(coords)

#     for i, j in coords:
#         rgb = _xy_to_rgb(i / (N_COLS - 1), j / (N_ROWS - 1))
#         utils.select_range(
#             calib,
#             # (chr(ord("A") + i * D), j * D + 1),
#             # (chr(ord("A") + i * D + (D - 1)), j * D + (D - 1) + 1),
#             (chr(ord("A") + i * D_COLS), j * D_ROWS + 1),
#             (chr(ord("A") + i * D_COLS + (D_COLS - 1)), j * D_ROWS + (D_ROWS - 1) + 1),
#         )
#         colors.ArbitraryColor(calib, *rgb).apply()


class PaletteTest2(_PatternBase, _1DMixin):
    name = "palette_test_2"

    def __init__(self, calib: CalibrationData) -> None:
        self.calib = calib
        self.d_rows = 4
        self.d_cols = 2
        Ni = calib.n_cols // self.d_cols
        Nj = calib.n_rows // self.d_rows
        self.coords = [(i, j) for i in range(Ni) for j in range(Nj)]

        super().__init__(len(self.coords))
        self.reset()

    def _xy_to_rgb(self, x: float, y: float) -> tuple[int, int, int]:
        """Convert (x, y) coordinates to RGB values."""
        r = int(255 * x)
        g = int(255 * y)
        b = int(255 * (1 - x) * (1 - y))
        return r, g, b

    def step(self) -> None:
        i, j = self.coords[self.i]
        rgb = self._xy_to_rgb(
            i / (self.calib.n_cols // self.d_cols - 1),
            j / (self.calib.n_rows // self.d_rows - 1),
        )
        utils.select_range(
            self.calib,
            (chr(ord("A") + i * self.d_cols), j * self.d_rows + 1),
            (chr(ord("A") + i * self.d_cols + (self.d_cols - 1)), j * self.d_rows + (self.d_rows - 1) + 1),
        )
        colors.ArbitraryColor(self.calib, *rgb).apply()


class ColumnLights(_PatternBase):
    name = "column_lights"

    def __init__(
        self,
        calib: CalibrationData,
        color: colors.Color,
    ) -> None:
        self.calib = calib
        self.color = color
        self.reset()

    def step(self) -> None:
        utils.select_column_index(self.calib, self.indices[self.i])
        self.color.apply()

    def advance(self) -> None:
        self.i += 1

    def reset(self) -> None:
        self.i = 0
        self.indices = random.sample(range(self.calib.n_cols), self.calib.n_cols)

    @property
    def n_steps(self) -> int:
        return self.calib.n_cols

    @property
    def current_step(self) -> int:
        return self.i


if TYPE_CHECKING:
    _column_lights: Pattern = ColumnLights.__new__(ColumnLights)


class RowLights(_PatternBase, _1DMixin):
    name = "row_lights"

    def __init__(
        self,
        calib: CalibrationData,
        color: colors.Color,
    ) -> None:
        self.calib = calib
        self.color = color
        self.i = 0
        indices = [i for i in range(calib.n_rows)]
        random.shuffle(indices)
        self.indices = indices

    def step(self) -> None:
        utils.select_row_index(self.calib, self.indices[self.i])
        self.color.apply()
        self.i += 1

    @property
    def n_steps(self) -> int:
        return self.calib.n_rows


if TYPE_CHECKING:
    _row_lights: Pattern = RowLights.__new__(RowLights)


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
    # min_steps = min(n_steps)

    # n_blocks = [math.ceil(n / min_steps) for n in n_steps]
    # print(f"Number of blocks for each pattern: {n_blocks}")
    while not all(n == 0 for n in n_steps):
        # pick a probability of stepping a pattern according to the number of steps left
        n_total = sum(n_steps)
        probs = [n / n_total for n in n_steps]

        # pick a pattern to step
        index = random.choices(range(len(patterns)), weights=probs, k=1)[0]
        patterns[index].step()
        patterns[index].advance()
        n_steps[index] -= 1
        print(n_steps)

    # print("All patterns finished stepping.")
