import json
import math
import os
import random
import sys
import time
from dataclasses import replace
from typing import Callable, Literal

import more_itertools
import pyautogui

from . import cell, colors, eject_button, patterns, text, utils
from .calibrate import CalibrationData, calibrate, reset

eject_button.arm()

from pathlib import Path

__file_dir__ = Path(__file__).parent
__project_root__ = __file_dir__.parent.parent

BOXES = __project_root__


def main() -> None:
    if len(sys.argv) == 1:
        response = pyautogui.confirm(  # type: ignore[attr-defined]
            text=(
                "This script will do things. Is LibreOffice open **and cell A1 selected**? "
                "If you press 'Yes', you will see a calibration procedure and then another "
                "confirmation box."
            ),
            title="Boxes",
            buttons=["Yes", "No", "Reset (!)"],
        )

        if response == "No":
            print("Exiting script.")
            sys.exit()
        elif response == "Reset (!)":
            os.execv(sys.executable, [sys.executable, "-m", "src.boxes", "reset"])

        elif response == "Yes":
            # call self with 'run' argument and replace the current process
            os.execv(sys.executable, [sys.executable, "-m", "src.boxes", "calibrate"])
        else:
            print(f"Unknown response: {response}. Expected 'Yes', 'No', or 'Reset'.")
            sys.exit()

    elif sys.argv[1] == "reset":
        reset(
            targets_dir=__project_root__ / "targets",
            pixel_ratio=2,  # 1 on most monitors, 2 on high DPI monitors
        )

        os.execv(sys.executable, [sys.executable, "-m", "src.boxes"])

    elif sys.argv[1] == "calibrate":
        calibration_data = calibrate(
            targets_dir=__project_root__ / "targets",
            # 1 on most monitors, 2 on high DPI monitors
            pixel_ratio=2,
            sleep_time=0.0,
        )
        os.execv(
            sys.executable,
            [
                sys.executable,
                "-m",
                "src.boxes",
                "run",
                calibration_data.to_b64(),
            ],
        )

    elif sys.argv[1] == "run":
        try:
            CD = CalibrationData.from_b64(sys.argv[2])
        except json.JSONDecodeError:
            print("Error: Invalid calibration data.")
            sys.exit()

        print(CD)

        run(CD)

    else:
        raise ValueError(f"Unknown argument: {sys.argv[1]}. Expected 'calibrate' or 'run'.")


def fires_up_night_down(calib: CalibrationData) -> None:
    p: list[patterns.Pattern]

    # FIRES UP
    golds: tuple[colors.ColorName, ...] = (
        "dark_gold_1",
        "dark_gold_1",
        "gold",
        "gold",
        "light_gold_1",
        "light_gold_2",
    )

    oranges: tuple[colors.ColorName, ...] = (
        "dark_orange_1",
        "dark_orange_1",
        "orange",
        "orange",
        "orange",
        "light_orange_1",
    )

    bricks: tuple[colors.ColorName, ...] = (
        "dark_brick_1",
        "dark_brick_1",
        "brick",
        "brick",
        "brick",
        "light_brick_1",
        "light_brick_1",
    )

    p = [
        patterns.Icicles(calib, "up", colors.StandardCyclerColor(calib, golds), segment_size=8),
        patterns.Icicles(calib, "up", colors.StandardCyclerColor(calib, oranges), segment_size=8),
        patterns.Icicles(calib, "up", colors.StandardCyclerColor(calib, bricks), segment_size=8),
    ]

    patterns.interweave_patterns(p)

    # NIGHT DOWN

    _sky: list[colors.ColorName] = [
        "blue",
        "dark_blue_1",
        "dark_blue_2",
        "dark_blue_3",
        "dark_indigo_3",
    ]

    sky = tuple(_sky)

    patterns.Snake(
        calib,
        colors.StandardCyclerColor(
            calib,
            utils.bounce(sky),
            offset=random.randint(0, len(sky) - 1),
        ),
    ).step_all()


def change_to_square_grid(calib: CalibrationData) -> CalibrationData:
    cell.change_cell_dimensions(
        calib,
        cell_width=cell.DEFAULT_CELL_HEIGHT,
        cell_height=cell.DEFAULT_CELL_HEIGHT,
    )

    # manually adjust the calibration data to fit the new cell dimensions
    calib2 = replace(
        calib,
        n_cols=101,  # CW
        n_rows=52,
        top_left=(
            calib.top_left[0] - calib.cell_width / 2 + 8,
            calib.top_left[1],
        ),
        bottom_right=(
            calib.bottom_right[0] + calib.cell_width / 2,
            calib.bottom_right[1],
        ),
    )
    return calib2


def grays_fill(calib: CalibrationData) -> None:
    grays: tuple[colors.ColorName, ...] = (
        "dark_gray_1",
        "gray",
        "light_gray_1",
        "light_gray_2",
    )

    # patterns.BoxFill(
    #     calib,
    #     colors.StandardCyclerColor(calib, grays),
    #     artistic=True,
    # ).step_all()
    patterns.Snake(
        calib,
        colors.StandardCyclerColor(calib, grays),
        width=calib.n_rows // 10,
        segment_size=calib.n_cols,
    ).step_all()


def draw_logo_final(
    calib: CalibrationData,
    square_grid: bool = True,
) -> None:
    """Draw the final logo on the grid."""

    if square_grid:
        calib = change_to_square_grid(calib)

    grays_fill(calib=calib)

    palette = [
        # "dark_brick_2",
        "dark_brick_1",
        "brick",
        "light_brick_1",
        "light_brick_1",
        "light_brick_2",
        "dark_orange_1",
        "orange",
    ]

    # patterns.BoxFill(
    #     calib,
    #     # colors.StandardColor.from_name(calib, "white"),
    #     # colors.StandardColor.from_name(calib, "gray"),
    #     colors.StandardCyclerColor(
    #         calib,
    #         utils.bounce(oranges),
    #     ),
    #     artistic=True,
    # ).step_all()
    p: list[patterns.Pattern] = []
    which: Literal["row", "column"] = "row"
    for color in palette:
        p.append(
            patterns.Lights(
                calib,
                which=which,
                color=colors.StandardColor.from_name(calib, color),
            )
        )
        which = "column" if which == "row" else "row"

    patterns.interweave_patterns(p)

    patterns.Image(
        calib,
        image=__project_root__ / "img" / "hivemind_inverted_white.png",
        mode="resize",
        color_distance_tolerance=40,
        alpha_threshold=30,
    ).step_all()


def gliders_final(calib: CalibrationData) -> None:
    calib = change_to_square_grid(calib)

    # draw a glider gun
    # fmt: off
    cell_coords = [
        ### square on the left
        (1, 5), (1, 6), (2, 5), (2, 6),
        ### big blob facing left
        (11, 5), (11, 6), (11, 7),
        (12, 4), (12, 8),
        (13, 3), (13, 9),
        (14, 3), (14, 9),
        (15, 6),
        (16, 4), (16, 8),
        (17, 5), (17, 6), (17, 7),
        (18, 6),
        ### square ship thingy
        (21, 3), (21, 4), (21, 5),
        (22, 3), (22, 4), (22, 5),
        (23, 2), (23, 6),
        (25, 1), (25, 2), (25, 6), (25, 7),
        ### square on the right
        (35, 3), (35, 4),
        (36, 3), (36, 4),
    ]
    # fmt: on

    i, j = 1, 1  # origin
    init_state: list[tuple[int, int]] = [(i + x, j + y) for x, y in cell_coords]

    patterns.GameOfLife(
        calib,
        dead=colors.StandardColor.from_name(calib, "dark_gray_1"),
        alive=colors.StandardColor.from_name(calib, "lime"),
        N=300_000,
        frame_sleep=1.0,  # Sleep time between frames
        init_state=init_state,
    ).step_all()


def random_fun(calib: CalibrationData) -> None:
    _ux = lambda x, y: int(255 * x)
    _uy = lambda x, y: int(255 * y)
    _dx = lambda x, y: int(255 * (1 - x))
    _dy = lambda x, y: int(255 * (1 - y))
    _uxuy = lambda x, y: int(255 * x * y)
    _dxdy = lambda x, y: int(255 * (1 - x) * (1 - y))
    _uxdy = lambda x, y: int(255 * x * (1 - y))
    _dxuy = lambda x, y: int(255 * (1 - x) * y)
    _sinx = lambda x, y: int(math.sin(x * math.pi) * 127 + 128)
    _siny = lambda x, y: int(math.sin(y * math.pi) * 127 + 128)
    _sinxy = lambda x, y: int(math.sin((x + y) * math.pi) * 127 + 128)
    _cosx = lambda x, y: int(math.cos(x * math.pi) * 127 + 128)
    _cosy = lambda x, y: int(math.cos(y * math.pi) * 127 + 128)
    _cosxy = lambda x, y: int(math.cos((x + y) * math.pi) * 127 + 128)
    funs = [_ux, _uy, _dx, _dy, _uxuy, _dxdy, _uxdy, _dxuy, _sinx, _siny, _sinxy, _cosx, _cosy, _cosxy]

    def _random_fun() -> Callable[[float, float], tuple[int, int, int]]:
        fr = random.choice(funs)
        fb = random.choice(funs)
        fg = random.choice(funs)
        return lambda x, y: (fr(x, y), fb(x, y), fg(x, y))

    while True:
        # randomise the palette fun. each component is a random function of x and y
        fun = _random_fun()
        patterns.Palette2(
            calib,
            fun=fun,
            d_rows=random.randint(3, 5),
            d_cols=random.randint(1, 3),
        ).step_all()


def snakes(calib: CalibrationData) -> None:
    palette = random.choice(list(colors.GROUPS.values()))
    while True:
        patterns.Snake(
            calib,
            colors.StandardCyclerColor(
                calib, utils.bounce(colors.filter_colors(palette, avoid_dark=True, avoid_light=True))
            ),
            width=random.randint(1, 3),
            segment_size=random.randint(3, 5),
            which=random.choice(["up", "down", "left", "right"]),
        ).step_all()

        new_palette = None
        if new_palette is None or palette != new_palette:
            new_palette = random.choice(list(colors.GROUPS.values()))
        palette = new_palette

        time.sleep(2.0)


def crosses(calib: CalibrationData) -> None:
    warm_palettes = [
        colors.GOLDS,
        colors.ORANGES,
        colors.BRICKS,
        colors.REDS,
    ]
    cold_palettes = [
        colors.INDIGOS,
        colors.BLUES,
        colors.TEALS,
        colors.GREENS,
    ]

    palette_a, palette_b = warm_palettes, cold_palettes

    while True:
        palette_lights = random.choice(palette_a)
        p: list[patterns.Pattern] = []

        which: Literal["row", "column"] = "row"
        colors_used = set()
        for color in more_itertools.sample(
            colors.filter_colors(
                palette_lights,
                avoid_dark=False,
                avoid_light=False,
            )
            + colors.filter_colors(
                palette_lights,
                avoid_dark=True,
                avoid_light=True,
            ),
            len(palette_lights),
        ):
            colors_used.add(color)
            p.append(
                patterns.Lights(
                    calib,
                    which=which,
                    color=colors.StandardColor.from_name(calib, color),
                )
            )
            which = "column" if which == "row" else "row"

        patterns.interweave_patterns(p)

        blank_color = colors.StandardColor.from_name(calib, random.choice(list(colors_used)))
        p = [patterns.Lights(calib, which=which, color=blank_color) for which in ["row", "column"]]  # type: ignore[arg-type]
        patterns.interweave_patterns(p)

        # palette_gaussians = random.choice(palette_b)
        # p = []
        # for _ in range(3):
        #     random_gaussian_color_1 = random.choice(palette_gaussians)
        #     random_gaussian_color_2 = None
        #     while random_gaussian_color_2 is None or random_gaussian_color_2 == random_gaussian_color_1:
        #         # Ensure the second color is different from the first
        #         random_gaussian_color_2 = random.choice(palette_gaussians)

        #     p.append(
        #         patterns.GaussianCells(
        #             calib,
        #             # inner=colors.RandomOnceColor(calib),
        #             # outer=colors.RandomOnceColor(calib),
        #             inner=colors.StandardColor.from_name(calib, random_gaussian_color_1),
        #             outer=colors.StandardColor.from_name(calib, random_gaussian_color_2),
        #             radius=2.0,
        #         )
        #     )

        # patterns.interweave_patterns(p)

        if random.random() < 0.25:
            palette_a, palette_b = palette_b, palette_a


def run(calib: CalibrationData) -> None:
    colors.reset_all_colors(calib)
    text.reset_all_cell_contents(calib)
    time.sleep(0.1)

    cell_area_width = calib.n_cols * calib.cell_width
    cell_area_height = calib.n_rows * calib.cell_height
    aspect_ratio = cell_area_width / cell_area_height
    print(f"Aspect ratio: {aspect_ratio:.2f}")

    # p: list[patterns.Pattern]

    # pyautogui.PAUSE = 0.0
    # pyautogui.PAUSE = 0.03
    pyautogui.PAUSE = 0.04
    # pyautogui.PAUSE = 0.2

    palette = colors.GROUPS[random.choice(list(colors.GROUPS.keys()))]
    while True:
        patterns.Clouds(
            calib,
            colors.StandardSamplerColor(
                calib,
                colors.filter_colors(palette, avoid_dark=True, avoid_light=True),
            ),
            n_diffusers=3,
            n_diffuser_steps=10,
            step_radius=1.8,
        ).step_all()

        new_palette = None
        if new_palette is None or palette != new_palette:
            new_palette = random.choice(list(colors.GROUPS.values()))
        palette = new_palette

    _BLOCK_ = True  # Useful for debugging, set to True to run all patterns

    if _BLOCK_:
        cc = utils.bounce(colors.filter_colors(colors.GOLDS, avoid_dark=True, avoid_light=True))
        ci = 0
        cj = len(cc) // 2
        for _ in range(len(cc)):
            this_c1 = cc[ci]
            ci = (ci + 1) % len(cc)
            this_c2 = cc[cj]
            cj = (cj + 1) % len(cc)

            patterns.InwardSpiral(calib, colors.StandardColor.from_name(calib, this_c1)).step_all()
            patterns.OutwardSpiral(calib, colors.StandardColor.from_name(calib, this_c2)).step_all()

    if _BLOCK_:
        patterns.Palette2(
            calib,
            fun=lambda x, y: (
                int(255 * x),
                int(255 * y),
                int(255 * (1 - x) * (1 - y)),
            ),
            d_rows=4,
            d_cols=2,
        ).step_all()

        patterns.Palette2(
            calib,
            fun=lambda x, y: (
                int(255 * (1 - x) * (1 - y)),
                int(255 * x),
                int(255 * (1 - y)),
            ),
        ).step_all()

        patterns.Palette2(
            calib,
            fun=lambda x, y: (
                int(math.sin(x * math.pi) * 127 + 128),
                int(math.sin(y * math.pi) * 127 + 128),
                int(math.sin((x + y) * math.pi) * 127 + 128),
            ),
            d_rows=4,
            d_cols=2,
        ).step_all()

    if _BLOCK_:
        patterns.DiagonalFill(
            calib,
            colors.StandardCyclerColor(
                calib,
                colors.filter_colors(colors.BLUES, avoid_dark=True, avoid_light=True),
            ),
        ).step_all()

    if _BLOCK_:
        patterns.Snake(
            calib,
            colors.StandardCyclerColor(
                calib, utils.bounce(colors.filter_colors(colors.PURPLES, avoid_dark=True, avoid_light=True))
            ),
            width=3,
            segment_size=3,
            which="down",
        ).step_all()

        patterns.Snake(
            calib,
            colors.StandardCyclerColor(calib, utils.bounce(colors.MAGENTAS)),
            width=1,
            segment_size=5,
            which="right",
        ).step_all()

    if _BLOCK_:
        # temp copy of night
        _sky: list[colors.ColorName] = [
            "blue",
            "dark_blue_1",
            "dark_blue_2",
            "dark_blue_3",
            "dark_indigo_3",
        ]

        sky = tuple(_sky)

        patterns.Snake(
            calib,
            colors.StandardCyclerColor(
                calib,
                utils.bounce(sky),
                offset=random.randint(0, len(sky) - 1),
            ),
        ).step_all()

        fires_up_night_down(calib)

    if _BLOCK_:
        draw_logo_final(
            calib,
            # square_grid=False,  # for debug speed
        )

    sys.exit()

    ############################################################################

    if _BLOCK_:
        palette = None

        while True:
            for color_group in colors.GROUPS.values():
                palette = colors.StandardCyclerColor(
                    calib,
                    utils.bounce(color_group),
                    offset=palette.current_index if palette else 0,
                    cache=False,
                )
                patterns.Boxes(calib, palette).step_all()

    patterns.RandomCells(
        calib,
        colors.RandomChangingColor(calib),
    ).step_all()

    patterns.GaussianCells(
        calib,
        inner=colors.StandardColor.from_name(calib, "dark_lime_1"),
        outer=colors.StandardColor.from_name(calib, "light_brick_1"),
    ).step_all()

    dc: list[tuple[Literal["down", "up", "left", "right"], str]] = [
        ("down", "light_brick_1"),
        ("up", "light_lime_1"),
        ("left", "light_indigo_1"),
        ("right", "light_gold_1"),
    ]
    p = [patterns.Icicles(calib, d, colors.StandardColor.from_name(calib, c)) for d, c in dc]
    patterns.interweave_patterns(p)


if __name__ == "__main__":
    main()
