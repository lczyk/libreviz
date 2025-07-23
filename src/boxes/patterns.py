import math
import random
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Literal, Protocol, no_type_check

from . import cell, colors
from .calibrate import CalibrationData
from .patched_click import click

PatternStep = Callable[[], None]

from PIL import Image as PILImage


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

    def _init_id(self) -> None:
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

    def _init_1d_base(self, Ni: int) -> None:
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

    def _init_2d_base(self, Ni: int, Nj: int) -> None:
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
        self._init_1d_base(len(self.nodes) - 1)
        self._init_id()
        self.reset()

    def step(self) -> PatternStep:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]

        def _step() -> None:
            cell.select_range(self.calib, n1, n2)
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
        self._init_1d_base(len(self.nodes) - 1)
        self._init_id()
        self.reset()

    def step(self) -> PatternStep:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]

        def _step() -> None:
            cell.select_range(self.calib, n1, n2)
            self.color.apply()

        return _step


if TYPE_CHECKING:
    _outward_spiral: Pattern = OutwardSpiral.__new__(OutwardSpiral)


class DenseSpiral(_1DBase, _PatternBase):
    _name_prefix = "dense_spiral"

    def __init__(
        self,
        calib: CalibrationData,
        color: colors.Color,
    ) -> None:
        self.calib = calib
        self.color = color
        _nodes = "A:1,S:1,S:52,A:52,A:2,R:2,R:51,B:51,B:3,Q:3,Q:50,C:50,C:4,P:4,P:49,D:49,D:5,O:5,O:48,E:48,E:6,N:6,N:47,F:47,F:7,M:7,M:46,G:46,G:8,L:8,L:45,H:45,H:9,K:9,K:44,I:44,I:10,J:10,J:43"
        self.nodes = _nodes.split(",")
        self._init_1d_base(len(self.nodes) - 1)
        self._init_id()
        self.reset()

    def step(self) -> PatternStep:
        n1, n2 = self.nodes[self.i], self.nodes[self.i + 1]

        def _step() -> None:
            cell.select_range(self.calib, n1, n2)
            self.color.apply()

        return _step


if TYPE_CHECKING:
    _dense_spiral: Pattern = DenseSpiral.__new__(DenseSpiral)


class PaletteTest1(_2DBase, _PatternBase):
    _name_prefix = "palette_test_1"

    def __init__(self, calib: CalibrationData) -> None:
        self.calib = calib
        self._init_2d_base(calib.n_color_cols, calib.n_color_rows)
        self._init_id()
        self.reset()

    def step(self) -> PatternStep:
        calib = self.calib
        i, j = self.i, self.j

        def _step() -> None:
            cell.select_range(
                calib,
                # (chr(ord("A") + i), 4 * j + 4),
                # (chr(ord("A") + i), 4 * j + 4 + 1),
                cell.ij2str((i, 4 * j + 3)),
                cell.ij2str((i, 4 * j + 4)),
            )
            colors.StandardColor(calib, i, j).apply()
            cell.select_range(
                calib,
                # (chr(ord("A") + i), 4 * j + 4 + 2),
                # (chr(ord("A") + i), 4 * j + 4 + 3),
                cell.ij2str((i, 4 * j + 5)),
                cell.ij2str((i, 4 * j + 6)),
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
        coerce: bool = True,
    ) -> None:
        self.calib = calib
        self.d_rows = min(d_rows, self.calib.n_rows)
        self.d_cols = min(d_cols, self.calib.n_cols)
        self.coerce = coerce
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

        self._init_1d_base(len(self.coords) + len(self.extra_coords))
        self._init_id()
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
                cell.select_range(
                    self.calib,
                    # (chr(ord("A") + i1), j1 + 1),
                    # (chr(ord("A") + i2), j2 + 1),
                    cell.ij2str((i1, j1)),
                    cell.ij2str((i2, j2)),
                )
                colors.ArbitraryColor(self.calib, *rgb, coerce=self.coerce).apply()

        else:
            # Handle the extra coordinates if any
            (i1, j1), (i2, j2) = self.extra_coords[self.i - len(self.coords)]
            rgb = colors.blend_rgb(
                self._xy_to_rgb(i1 / self.calib.n_cols, j1 / self.calib.n_rows),
                self._xy_to_rgb(i2 / self.calib.n_cols, j2 / self.calib.n_rows),
                0.5,
            )

            def _step() -> None:
                cell.select_range(
                    self.calib,
                    # (chr(ord("A") + i1), j1 + 1),
                    # (chr(ord("A") + i2), j2 + 1),
                    cell.ij2str((i1, j1)),
                    cell.ij2str((i2, j2)),
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
            self.f = cell.select_row_index
            N = calib.n_rows
        else:
            self.f = cell.select_column_index
            N = calib.n_cols
        self._init_1d_base(N)
        self._init_id()
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
        self._init_1d_base(calib.n_cols * calib.n_rows)
        self._init_id()
        self.reset()

    def reset(self) -> None:
        super().reset()
        self.coords = [(i, j) for i in range(self.calib.n_cols) for j in range(self.calib.n_rows)]
        random.shuffle(self.coords)

    def step(self) -> PatternStep:
        i, j = self.coords[self.i]

        def _step() -> None:
            click(
                *cell.cell_coords(
                    self.calib,
                    cell.ij2str((i, j)),
                )
            )
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
        self._init_1d_base(calib.n_cols * calib.n_rows)
        self._init_id()
        self.reset()

    def reset(self) -> None:
        super().reset()

        def _color(i: int, j: int) -> tuple[int, int, int]:
            w, q = cell.ij2wq(self.calib, (i, j))
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
            click(
                *cell.cell_coords(
                    self.calib,
                    cell.ij2str((i, j)),
                )
            )
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

        self._init_1d_base(len(self.boxes))
        self._init_id()
        self.reset()

    def step(self) -> PatternStep:
        (i1, j1), (i2, j2) = self.boxes[self.i]

        def _step() -> None:
            cell.select_range(
                self.calib,
                # (chr(ord("A") + i1), j1 + 1),
                # (chr(ord("A") + i2), j2 + 1),
                cell.ij2str((i1, j1)),
                cell.ij2str((i2, j2)),
            )
            self.color.apply()

        return _step


if TYPE_CHECKING:
    _boxes: Pattern = Boxes.__new__(Boxes)


class Icicles(_1DBase, _PatternBase):
    _name_prefix = "icicles"

    def __init__(
        self,
        calib: CalibrationData,
        direction: Literal["up", "down", "left", "right"],
        color: colors.Color,
        segment_size: int = 8,
    ) -> None:
        self.calib = calib
        self.color = color
        self.f: Callable[[CalibrationData, int], None]
        self.segment_size = segment_size
        self.direction = direction
        self._init_id()
        self.reset()

    def reset(self) -> None:
        super().reset()
        self.segments: list[tuple[int, int, int]] = []  # major_index, minor_start, minor_end
        if self.direction in ("up", "down"):
            N, M = self.calib.n_cols, self.calib.n_rows
        else:
            N, M = self.calib.n_rows, self.calib.n_cols
        lengths = [0] * N
        while not all(cl >= M for cl in lengths):
            # roll a random index
            non_full = [i for i in range(N) if not lengths[i] >= M]
            i = random.choice(non_full)

            # migrate the icicles left or right a bit
            this_length = lengths[i]
            prev_length = -1
            if i > 0 and lengths[i - 1] < M:
                prev_length = lengths[i - 1]
            next_length = -1
            if i < (N - 1) and lengths[i + 1] < M:
                next_length = lengths[i + 1]

            weights = [0, 10, 0]
            if prev_length > this_length:
                weights[0] += 2
                weights[1] -= 2
            if next_length > this_length:
                weights[2] += 2
                weights[1] -= 2

            i += random.choices([-1, 0, +1], weights=weights, k=1)[0]

            # roll a segment length
            segment_length = random.randint(
                max(0, self.segment_size - 1),
                min(M, self.segment_size + 1),
            )

            if lengths[i] + segment_length >= M:
                # last icicle in this column
                segment_length = M - lengths[i]

            if self.direction in ("down", "right"):
                segment = (
                    i,
                    lengths[i],
                    lengths[i] + segment_length - 1,
                )
            else:
                segment = (
                    i,
                    M - 1 - lengths[i],
                    M - 1 - (lengths[i] + segment_length - 1),
                )

            self.segments.append(segment)

            lengths[i] += segment_length

        self._init_1d_base(len(self.segments))

    def step(self) -> PatternStep:
        i = self.i
        if self.direction in ("up", "down"):

            def _step() -> None:
                col, row_start, row_end = self.segments[i]
                cell.select_range(
                    self.calib,
                    # (chr(ord("A") + col), row_start + 1),
                    # (chr(ord("A") + col), row_end + 1),
                    cell.ij2str((col, row_start)),
                    cell.ij2str((col, row_end)),
                )
                self.color.apply()
        else:

            def _step() -> None:
                row, col_start, col_end = self.segments[i]
                cell.select_range(
                    self.calib,
                    # (chr(ord("A") + col_start), row + 1),
                    # (chr(ord("A") + col_end), row + 1),
                    cell.ij2str((col_start, row)),
                    cell.ij2str((col_end, row)),
                )
                self.color.apply()

        return _step


if TYPE_CHECKING:
    _icicles: Pattern = Icicles.__new__(Icicles)


class Snake(_1DBase, _PatternBase):
    """Snake down the screen: A1->A52, then one row down and back up: B52->B1, then C1->C52, etc."""

    _name_prefix = "snake"

    def __init__(
        self,
        calib: CalibrationData,
        color: colors.Color,
        width: int = 2,
        segment_size: int = 4,
        which: Literal["down", "right"] = "down",
    ) -> None:
        self.calib = calib
        self.color = color
        self.segment_size = segment_size
        self.width = width
        self.which = which
        self._init_id()
        self.reset()

    def reset(self) -> None:
        super().reset()

        self.segments: list[tuple[tuple[int, int], tuple[int, int]]] = []

        if self.which == "down":
            right = True
            for j in range(0, self.calib.n_rows, self.width):
                if right:
                    # left to right
                    for i in range(0, self.calib.n_cols, self.segment_size):
                        i1 = i
                        i2 = min(i + self.segment_size - 1, self.calib.n_cols - 1)
                        if i2 < i1:
                            continue
                        self.segments.append(
                            (
                                (i1, min(j, self.calib.n_rows - 1)),
                                (i2, min(j + self.width - 1, self.calib.n_rows - 1)),
                            )
                        )
                else:
                    # right to left
                    for i in range(self.calib.n_cols - 1, -1, -self.segment_size):
                        i1 = max(0, i - self.segment_size + 1)
                        i2 = i
                        if i2 < i1:
                            continue
                        self.segments.append(
                            (
                                (i1, min(j, self.calib.n_rows - 1)),
                                (i2, min(j + self.width - 1, self.calib.n_rows - 1)),
                            )
                        )
                right = not right
        elif self.which == "right":
            down = True
            for i in range(0, self.calib.n_cols, self.width):
                if down:
                    # top to bottom
                    for j in range(0, self.calib.n_rows, self.segment_size):
                        j1 = j
                        j2 = min(j + self.segment_size - 1, self.calib.n_rows - 1)
                        if j2 < j1:
                            continue
                        self.segments.append(
                            (
                                (min(i, self.calib.n_cols - 1), j1),
                                (min(i + self.width - 1, self.calib.n_cols - 1), j2),
                            )
                        )
                else:
                    # bottom to top
                    for j in range(self.calib.n_rows - 1, -1, -self.segment_size):
                        j1 = max(0, j - self.segment_size + 1)
                        j2 = j
                        if j2 < j1:
                            continue
                        self.segments.append(
                            (
                                (min(i, self.calib.n_cols - 1), j1),
                                (min(i + self.width - 1, self.calib.n_cols - 1), j2),
                            )
                        )
                down = not down

        self._init_1d_base(len(self.segments))
        # print(f"Snake segments: {self.segments}")

    def step(self) -> PatternStep:
        i = self.i
        (i1, j1), (i2, j2) = self.segments[i]

        def _step() -> None:
            cell.select_range(
                self.calib,
                # (chr(ord("A") + i1), j1 + 1),
                # (chr(ord("A") + i2), j2 + 1),
                cell.ij2str((i1, j1)),
                cell.ij2str((i2, j2)),
            )
            self.color.apply()

        return _step


class Image(_1DBase, _PatternBase):
    """Pattern which draws a downsampled version of the image on the screen."""

    _name_prefix = "image"

    def __init__(
        self,
        calib: CalibrationData,
        image: Path,
        *,
        mode: Literal["resize", "crop"] = "resize",
        color_distance_tolerance: int = 10,
        alpha_threshold: int = 10,
    ) -> None:
        self.calib = calib
        self.color_distance_tolerance = color_distance_tolerance
        self.alpha_threshold = alpha_threshold

        # load image using numpy
        img1 = PILImage.open(image)
        img2 = img1.convert("RGBA")  # Make sure the image is in RGBA format

        if mode == "crop":
            # crop the image to fit the aspect ratio of the number of cells
            cell_area_width = calib.cell_width * calib.n_cols
            cell_area_height = calib.cell_height * calib.n_rows
            cell_area_aspect_ratio = cell_area_width / cell_area_height
            img_aspect_ratio = img2.width / img2.height
            if img_aspect_ratio > cell_area_aspect_ratio:
                # Image is wider than the cell area, crop width
                new_width = int(cell_area_height * img_aspect_ratio)
                img3 = img2.crop(
                    (
                        (img2.width - new_width) // 2,
                        0,
                        (img2.width + new_width) // 2,
                        img2.height,
                    )
                )
            else:
                # Image is taller than the cell area, crop height
                new_height = int(cell_area_width / img_aspect_ratio)
                img3 = img2.crop(
                    (
                        0,
                        (img2.height - new_height) // 2,
                        img2.width,
                        (img2.height + new_height) // 2,
                    )
                )
        elif mode == "resize":
            # resize the image to fit the number of cells
            img3 = img2.resize(
                (int(calib.n_cols * calib.cell_width), int(calib.n_rows * calib.cell_height)),
                PILImage.Resampling.LANCZOS,
            )
        else:
            raise ValueError(f"Unknown mode: {mode}. Use 'resize' or 'crop'.")

        # downsample the image to fit the number of cells
        img4 = img3.resize(
            (calib.n_cols, calib.n_rows),
            PILImage.Resampling.LANCZOS,
        )

        # convert the image to a list of RGB tuples
        image_data: list[tuple[int, int, int, int]] = list(img4.getdata())
        image_data_2 = [
            (rgba, (i, j))
            for j in range(calib.n_rows)
            for i in range(calib.n_cols)
            for rgba in [image_data[i + j * calib.n_cols]]
        ]

        # filter out fully transparent pixels
        self.image_data = [
            (
                (i, j),
                (r, g, b),
            )
            for (r, g, b, a), (i, j) in image_data_2
            if a > self.alpha_threshold  # Only keep pixels with alpha > threshold
        ]

        self._init_id()
        self._init_1d_base(len(self.image_data))
        self.reset()

    def reset(self) -> None:
        super().reset()

        # group by color
        grouped_coords = colors.group_by_color(
            self.image_data,
            color_accessor=lambda x: x[1],
            distance_tol=self.color_distance_tolerance,
            # shuffle=True,
        )

        grouped_rich_colors: dict[tuple[int, int, int], list[colors.RichColor]] = {}
        for color_rgb, coords in grouped_coords.items():
            color_cells: list[colors.ColoredCell] = []
            for (i, j), _ in coords:
                color_cells.append(
                    colors.ColoredCell(
                        self.calib,
                        colors.ArbitraryColor(self.calib, *color_rgb),
                        cell.ij2str((i, j)),
                    )
                )
            grouped_rich_colors[color_rgb] = colors.simplify_monochrome_colors(color_cells)

        # flatten
        rich_colors: list[colors.RichColor] = []
        for rich_colors_group in grouped_rich_colors.values():
            rich_colors.extend(rich_colors_group)

        self.rich_colors = rich_colors
        self._init_1d_base(len(self.rich_colors))

    def step(self) -> PatternStep:
        rich_color = self.rich_colors[self.i]

        def _step() -> None:
            rich_color.apply()

        return _step


if TYPE_CHECKING:
    _image: Pattern = Image.__new__(Image)


class BoxFill(_1DBase, _PatternBase):
    _name_prefix = "box_fill"

    def __init__(
        self,
        calib: CalibrationData,
        color: colors.Color,
        artistic: bool = True,
        max_expansions: int = -1,  # -1 means no limit
    ) -> None:
        self.calib = calib
        self.color = color
        self.artistic = artistic
        self.max_expansions = max_expansions
        self._init_id()
        self.reset()

    def reset(self) -> None:
        super().reset()
        coords = [(i, j) for i in range(self.calib.n_cols) for j in range(self.calib.n_rows)]

        color_cells: list[colors.ColoredCell] = [
            colors.ColoredCell(
                self.calib,
                self.color,
                cell.ij2str((i, j)),
            )
            for i, j in coords
        ]

        self.rich_colors = colors.simplify_monochrome_colors(
            color_cells,
            early_stop=self.artistic,
            max_expansions=self.max_expansions,
        )
        self._init_1d_base(len(self.rich_colors))

    def step(self) -> PatternStep:
        rich_color = self.rich_colors[self.i]

        def _step() -> None:
            rich_color.apply()

        return _step


class DiagonalFill(_1DBase, _PatternBase):
    """Fill the screen diagonally, starting from the top left corner and moving to the bottom right corner."""

    _name_prefix = "diagonal_fill"

    def __init__(
        self,
        calib: CalibrationData,
        color: colors.Color,
    ) -> None:
        self.calib = calib
        self.color = color
        self._init_id()
        self.reset()

    def reset(self) -> None:
        super().reset()
        rich_colors: list[colors.RichColor] = []

        i, j = 0, 0  # pointers to one cell
        ii, jj = 0, 0  # pointer to another cell
        N_steps = self.calib.n_cols + self.calib.n_rows - 1
        ij_direction = "right"
        iijj_direction = "down"
        # walk i,j right and down, and ii,jj down and right
        for _ in range(N_steps):
            # add the segment from (i, j) to (ii, jj)
            _i, _j = i, j
            cells = []
            while _i >= ii or _j <= jj:
                cells.append(cell.ij2str((_i, _j)))
                _i -= 1
                _j += 1

            rich_colors.append(colors.ColoredCloud(self.calib, self.color, cells))
            # walk
            if ij_direction == "right":
                i, j = i + 1, j
                if i == self.calib.n_cols - 1:
                    ij_direction = "down"
            else:
                i, j = i, j + 1

            if iijj_direction == "down":
                ii, jj = ii, jj + 1
                if jj == self.calib.n_rows - 1:
                    iijj_direction = "right"
            else:
                ii, jj = ii + 1, jj

        # for (i1, j1), (i2, j2) in segments:
        #     ii, jj = i1, j1
        #     cells = []
        #     while ii <= i2 and jj <= j2:
        #         cells.append(cell.ij2str((ii, jj)))
        #         ii -= 1
        #         jj += 1
        #     rich_colors.append(colors.ColoredCloud(self.calib, self.color, cells))

        self.rich_colors = rich_colors
        self._init_1d_base(len(self.rich_colors))

    def step(self) -> PatternStep:
        rich_color = self.rich_colors[self.i]

        def _step() -> None:
            rich_color.apply()

        return _step


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
