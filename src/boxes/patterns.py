import math
import random
from typing import TYPE_CHECKING, Callable, Literal, Protocol, no_type_check

from . import colors, utils
from .calibrate import CalibrationData
from .patched_click import click

PatternStep = Callable[[], None]


class Pattern(Protocol):
    def step(self) -> PatternStep:
        """Return the procedure to call to perform a single step of the pattern."""
        ...

    def all_steps(self) -> list[PatternStep]:
        """Return all the steps of the pattern."""
        ...

    def advance(self) -> None:
        """Advance the internal state"""
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

    @property
    def name(self) -> str: ...


class _PatternBase:
    _id: int
    _name_prefix: str

    def __init__(self) -> None:
        self._id = random.randint(1, 9999)

    @no_type_check
    def all_steps(self) -> list[PatternStep]:
        """Perform all steps of the pattern."""
        steps: list[PatternStep] = []
        for _ in range(self.n_steps):
            steps.append(self.step())
            self.advance()
        return steps

    @no_type_check
    def __len__(self) -> int:
        """Return the number of steps in the pattern."""
        return self.n_steps

    @no_type_check
    def step_all(self) -> None:
        """Perform all steps of the pattern."""
        for step in self.all_steps():
            step()

    @property
    def name(self) -> str:
        return self._name_prefix + "_" + str(self._id)


class _1DBase:
    """Mixin for 1D patterns that have a single index."""

    i: int
    Ni: int

    def __init__(self, Ni: int) -> None:
        super().__init__()
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


class _2DBase:
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


################################################################################


class InwardSpiral(_1DBase, _PatternBase):
    _name_prefix = "inward_spiral"

    def __init__(self, calib: CalibrationData, color: colors.Color) -> None:
        self.calib = calib
        self.color = color
        _nodes = "A:1,S:1,S:52,A:52,A:3,Q:3,Q:50,C:50,C:5,O:5,O:48,E:48,E:7,M:7,M:46,G:46,G:9,K:9,K:44,I:44,I:11"
        self.nodes = _nodes.split(",")
        super().__init__(len(self.nodes) - 1)
        self.reset()

    def step(self) -> PatternStep:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]

        def _step() -> None:
            utils.select_range(self.calib, n1, n2)
            self.color.apply()

        return _step


if TYPE_CHECKING:
    _inward_spiral: Pattern = InwardSpiral.__new__(InwardSpiral)


class OutwardSpiral(_1DBase, _PatternBase):
    _name_prefix = "outward_spiral"

    def __init__(self, calib: CalibrationData, color: colors.Color) -> None:
        self.calib = calib
        self.color = color
        _nodes = "J:43,J:10,H:10,H:45,L:45,L:8,F:8,F:47,N:47,N:6,D:6,D:49,P:49,P:4,B:4,B:51,R:51,R:2,A:2"
        self.nodes = _nodes.split(",")
        super().__init__(len(self.nodes) - 1)
        self.reset()

    def step(self) -> PatternStep:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]

        def _step() -> None:
            utils.select_range(self.calib, n1, n2)
            self.color.apply()

        return _step


if TYPE_CHECKING:
    _outward_spiral: Pattern = OutwardSpiral.__new__(OutwardSpiral)


# def palette_test_1(calib: CalibrationData) -> None:
#     for j in range(calib.n_color_rows):
#         for i in range(calib.n_color_cols):
#             # print(f"Applying color ({i}, {j})")


class PaletteTest1(_2DBase, _PatternBase):
    _name_prefix = "palette_test_1"

    def __init__(self, calib: CalibrationData) -> None:
        self.calib = calib
        super().__init__(calib.n_color_cols, calib.n_color_rows)
        self.reset()

    def step(self) -> PatternStep:
        calib = self.calib
        i, j = self.i, self.j

        def _step() -> None:
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

        return _step


if TYPE_CHECKING:
    _palette_test_1: Pattern = PaletteTest1.__new__(PaletteTest1)

PaletteFun = Callable[[float, float], tuple[int, int, int]]


# x = min(max(x, 0), 1)  # Clamp x to [0, 1]
#     y = min(max(y, 0), 1)  # Clamp y to [0, 1]
def default_palette_fun(x: float, y: float) -> tuple[int, int, int]:
    r = int(255 * x)
    g = int(255 * y)
    b = int(255 * (1 - x) * (1 - y))
    return r, g, b


class Palette2(_1DBase, _PatternBase):
    _name_prefix = "palette_2"

    def __init__(
        self,
        calib: CalibrationData,
        *,
        fun: PaletteFun | None = None,
        d_rows: int = 4,
        d_cols: int = 2,
    ) -> None:
        self.calib = calib
        self.d_rows = min(d_rows, self.calib.n_rows)
        self.d_cols = min(d_cols, self.calib.n_cols)
        Ni = calib.n_cols // self.d_cols
        Nj = calib.n_rows // self.d_rows
        self.coords: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for i in range(Ni):
            for j in range(Nj):
                self.coords.append(
                    (
                        (i * self.d_cols, j * self.d_rows),
                        (i * self.d_cols + self.d_cols - 1, j * self.d_rows + self.d_rows - 1),
                    )
                )

        # if any if the downsampling does not divide evenly, add the remaining cells one-by-one
        self.extra_coords: list[tuple[tuple[int, int], tuple[int, int]]] = []
        n_remaining_cols = calib.n_cols % self.d_cols
        n_remaining_rows = calib.n_rows % self.d_rows
        if n_remaining_cols > 0:
            for j in range(Nj):
                self.extra_coords.append(
                    (
                        (calib.n_cols - n_remaining_cols, j * self.d_rows),
                        (calib.n_cols - 1, j * self.d_rows + self.d_rows - 1),
                    )
                )

        if n_remaining_rows > 0:
            for i in range(Ni):
                self.extra_coords.append(
                    (
                        (i * self.d_cols, calib.n_rows - n_remaining_rows),
                        (i * self.d_cols + self.d_cols - 1, calib.n_rows - 1),
                    )
                )

        if n_remaining_cols > 0 and n_remaining_rows > 0:
            # Add the bottom-right corner if both dimensions have remainders
            self.extra_coords.append(
                (
                    (calib.n_cols - n_remaining_cols, calib.n_rows - n_remaining_rows),
                    (calib.n_cols - 1, calib.n_rows - 1),
                )
            )

        self.fun: PaletteFun
        if fun is None:
            self.fun = default_palette_fun
        else:
            self.fun = fun

        super().__init__(len(self.coords) + len(self.extra_coords))
        self.reset()

    def _xy_to_rgb(self, x: float, y: float) -> tuple[int, int, int]:
        """Convert x, y coordinates to RGB color using the palette function."""
        x = min(max(x, 0), 1)  # Clamp x to [0, 1]
        y = min(max(y, 0), 1)  # Clamp y to [
        r, g, b = self.fun(x, y)
        r = min(max(r, 0), 255)  # Clamp r to [0, 255]
        g = min(max(g, 0), 255)  # Clamp g to [0, 255]
        b = min(max(b, 0), 255)  # Clamp b to [0, 255]
        return r, g, b

    def step(self) -> PatternStep:
        if self.i < len(self.coords):
            (i1, j1), (i2, j2) = self.coords[self.i]

            rgb = colors.blend_rgb(
                self._xy_to_rgb(i1 / self.calib.n_cols, j1 / self.calib.n_rows),
                self._xy_to_rgb(i2 / self.calib.n_cols, j2 / self.calib.n_rows),
                0.5,
            )

            def _step() -> None:
                utils.select_range(
                    self.calib,
                    (chr(ord("A") + i1), j1 + 1),
                    (chr(ord("A") + i2), j2 + 1),
                )
                colors.ArbitraryColor(self.calib, *rgb, coerce=True).apply()

        else:
            # Handle the extra coordinates if any
            (i1, j1), (i2, j2) = self.extra_coords[self.i - len(self.coords)]
            rgb = colors.blend_rgb(
                self._xy_to_rgb(i1 / self.calib.n_cols, j1 / self.calib.n_rows),
                self._xy_to_rgb(i2 / self.calib.n_cols, j2 / self.calib.n_rows),
                0.5,
            )

            def _step() -> None:
                utils.select_range(
                    self.calib,
                    (chr(ord("A") + i1), j1 + 1),
                    (chr(ord("A") + i2), j2 + 1),
                )
                colors.ArbitraryColor(self.calib, *rgb, coerce=True).apply()

        return _step


class Lights(_1DBase, _PatternBase):
    _name_prefix = "lights"

    def __init__(
        self,
        calib: CalibrationData,
        which: Literal["row", "column"],
        color: colors.Color,
    ) -> None:
        self.calib = calib
        self.color = color
        self.f: Callable[[CalibrationData, int], None]
        if which == "row":
            self.f = utils.select_row_index
            N = calib.n_rows
        else:
            self.f = utils.select_column_index
            N = calib.n_cols
        super().__init__(N)
        self.reset()

    def step(self) -> PatternStep:
        i = self.i

        def _step() -> None:
            self.f(self.calib, self.indices[i])
            self.color.apply()

        return _step

    def reset(self) -> None:
        super().reset()
        self.indices = random.sample(range(self.Ni), self.Ni)


if TYPE_CHECKING:
    _lights: Pattern = Lights.__new__(Lights)


class RandomCells(_1DBase, _PatternBase):
    _name_prefix = "random_cells"

    def __init__(self, calib: CalibrationData, color: colors.Color) -> None:
        self.calib = calib
        self.color = color
        super().__init__(calib.n_cols * calib.n_rows)
        self.reset()

    def reset(self) -> None:
        super().reset()
        self.coords = [(i, j) for i in range(self.calib.n_cols) for j in range(self.calib.n_rows)]
        random.shuffle(self.coords)

    def step(self) -> PatternStep:
        i, j = self.coords[self.i]

        def _step() -> None:
            click(*utils.cell_coords(self.calib, (i, j)))
            self.color.apply()

        return _step


if TYPE_CHECKING:
    _random_cells: Pattern = RandomCells.__new__(RandomCells)


class GaussianCells(_1DBase, _PatternBase):
    _name_prefix = "cells"

    def __init__(
        self,
        calib: CalibrationData,
        *,
        inner: colors.Color,
        outer: colors.Color,
        radius: float = 1.5,
    ) -> None:
        self.calib = calib
        self.color_inner = inner
        self.color_outer = outer
        self.radius = radius
        super().__init__(calib.n_cols * calib.n_rows)
        self.reset()

    def reset(self) -> None:
        super().reset()

        def _color(i: int, j: int) -> tuple[int, int, int]:
            w, q = utils.ij2wq(self.calib, i, j)
            r = math.sqrt(w**2 + q**2)
            alpha = min(1, r / self.radius)
            return (
                int(self.color_inner.rgb()[0] * (1 - alpha) + self.color_outer.rgb()[0] * alpha),
                int(self.color_inner.rgb()[1] * (1 - alpha) + self.color_outer.rgb()[1] * alpha),
                int(self.color_inner.rgb()[2] * (1 - alpha) + self.color_outer.rgb()[2] * alpha),
            )

        coords_with_color = [(i, j, _color(i, j)) for i in range(self.calib.n_cols) for j in range(self.calib.n_rows)]

        # group by color
        grouped_coords: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
        distance_tol = 10
        for i, j, color_rgb in coords_with_color:
            # Check if the color is already in the dictionary
            found = False
            for existing_color in grouped_coords:
                if colors.color_distance(existing_color, color_rgb) < distance_tol:
                    grouped_coords[existing_color].append((i, j))
                    found = True
                    break
            if not found:
                grouped_coords[color_rgb] = [(i, j)]

        # shuffle the colors in each group
        for color_rgb in grouped_coords:
            random.shuffle(grouped_coords[color_rgb])

        # flatten the grouped coordinates
        self.coords = []
        for color_rgb, coords in grouped_coords.items():
            for i, j in coords:
                self.coords.append((i, j, color_rgb))

    def step(self) -> PatternStep:
        i, j, color_rgb = self.coords[self.i]

        def _step() -> None:
            click(*utils.cell_coords(self.calib, (i, j)))
            # print(f"Applying color {color_rgb} to cell ({i}, {j})")
            colors.ArbitraryColor(self.calib, *color_rgb).apply()

        return _step


if TYPE_CHECKING:
    _gaussian_cells: Pattern = GaussianCells.__new__(GaussianCells)


class Boxes(_1DBase, _PatternBase):
    _name_prefix = "boxes"

    def __init__(
        self,
        calib: CalibrationData,
        color: colors.Color,
    ) -> None:
        self.calib = calib
        self.color = color

        def _all_covered(cells_map: list[list[bool]]) -> bool:
            return all(all(row) for row in cells_map)

        def _random_uncovered_cell(cells_map: list[list[bool]]) -> tuple[int, int]:
            uncovered_cells: list[tuple[int, int]] = []
            for i in range(calib.n_cols):
                for j in range(calib.n_rows):
                    if not cells_map[i][j]:
                        uncovered_cells.extend([(i, j)])
            if not uncovered_cells:
                raise ValueError("No uncovered cells left.")
            return random.choice(uncovered_cells)

        def _mark_cells_as_covered(cells_map: list[list[bool]], i1: int, j1: int, i2: int, j2: int) -> None:
            r1 = range(i1, i2 + 1) if i1 < i2 else range(i2, i1 + 1)
            r2 = range(j1, j2 + 1) if j1 < j2 else range(j2, j1 + 1)
            for i in r1:
                for j in r2:
                    cells_map[i][j] = True

        cells_map: list[list[bool]] = [[False] * calib.n_rows for _ in range(calib.n_cols)]
        self.boxes: list[tuple[tuple[int, int], tuple[int, int]]] = []

        while not _all_covered(cells_map):
            i1, j1 = _random_uncovered_cell(cells_map)
            i2, j2 = _random_uncovered_cell(cells_map)
            self.boxes.append(((i1, j1), (i2, j2)))
            _mark_cells_as_covered(cells_map, i1, j1, i2, j2)

        super().__init__(len(self.boxes))
        self.reset()

    def step(self) -> PatternStep:
        (i1, j1), (i2, j2) = self.boxes[self.i]

        def _step() -> None:
            utils.select_range(
                self.calib,
                (chr(ord("A") + i1), j1 + 1),
                (chr(ord("A") + i2), j2 + 1),
            )
            self.color.apply()

        return _step


if TYPE_CHECKING:
    _boxes: Pattern = Boxes.__new__(Boxes)

################################################################################


def interweave_patterns(patterns: list[Pattern]) -> None:
    """Run all patterns in the list, interleaving their steps. Find out how many steps each pattern has,
    and scale the number of steps taken by each pattern such that they all finish roughly at the same time."""
    steps: dict[str, list[PatternStep]] = {p.name: p.all_steps() for p in patterns}
    while not all(len(s) == 0 for s in steps.values()):
        # pick a probability of stepping a pattern according to the number of steps left
        weights = [len(s) for s in steps.values()]

        # pick a pattern to step
        name: str = random.choices(list(steps.keys()), weights=weights, k=1)[0]
        step = steps[name].pop(0)
        step()
