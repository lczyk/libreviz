import json
import os
import random
import sys
import time
from collections import deque
from typing import Literal

import pyautogui

from . import colors, eject_button, patterns, text
from .calibrate import CalibrationData, calibrate

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
            buttons=["Yes", "No"],
        )

        if response == "No":
            print("Exiting script.")
            sys.exit()

        # call self with 'run' argument and replace the current process
        os.execv(sys.executable, [sys.executable, "-m", "src.boxes", "calibrate"])

    elif sys.argv[1] == "calibrate":
        calibration_data = calibrate(
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


def run(calib: CalibrationData) -> None:
    colors.reset_all_colors(calib)
    text.reset_all_cell_contents(calib)
    time.sleep(0.1)

    # pyautogui.PAUSE = 0.0
    pyautogui.PAUSE = 0.03

    c = list(colors.TEALS) + list(colors.LIMES)
    random.shuffle(c)
    patterns.DenseSpiral(
        calib,
        colors.StandardPaletteColor(calib, c),
    ).step_all()

    dc: list[tuple[Literal["down", "up", "left", "right"], str]] = [
        ("down", "light_brick_1"),
        ("up", "light_lime_1"),
        ("left", "light_indigo_1"),
        ("right", "light_gold_1"),
    ]
    p: list[patterns.Pattern] = [patterns.Icicles(calib, d, colors.StandardColor.from_name(calib, c)) for d, c in dc]

    patterns.interweave_patterns(p)

    sys.exit()

    c1 = deque(colors.TEALS)
    c2 = deque(colors.REDS)

    while True:
        this_c1 = c1.popleft()
        c1.append(this_c1)
        this_c2 = c2.popleft()
        c2.append(this_c2)

        p: list[patterns.Pattern] = [
            # patterns.InwardSpiral(calib, colors.StandardColor.from_name(calib, "light_red_1")),
            # patterns.OutwardSpiral(calib, colors.StandardColor.from_name(calib, "light_blue_1")),
            patterns.Lights(calib, "column", colors.StandardColor.from_name(calib, this_c2)),
            patterns.Lights(calib, "row", colors.StandardColor.from_name(calib, this_c1)),
        ]

        patterns.interweave_patterns(p)

    palette = None

    while True:
        for color_group in colors.GROUPS.values():
            # create a 'bounce' effect by reversing half of the color group
            color_group_2 = list(color_group)
            color_group_2.extend(reversed(color_group_2[1:-1]))

            palette = colors.StandardPaletteColor(
                calib,
                color_group_2,
                offset=palette.current_index if palette else 0,
                cache=False,
            )
            patterns.Boxes(calib, palette).step_all()

    patterns.Palette2(
        calib,
        fun=lambda x, y: (
            int(255 * (1 - x) * (1 - y)),
            int(255 * x),
            int(255 * (1 - y)),
        ),
    ).step_all()

    patterns.RandomCells(
        calib,
        colors.RandomChangingColor(calib),
    ).step_all()

    patterns.GaussianCells(
        calib,
        inner=colors.StandardColor.from_name(calib, "dark_lime_1"),
        outer=colors.StandardColor.from_name(calib, "light_brick_1"),
    ).step_all()

    # c = ["red", "green", "blue", "yellow", "brick", "lime", "teal"]

    # while True:
    #     next_color_1 = c.pop(0)
    #     c.append(next_color_1)
    #     next_color_2 = c.pop(0)
    #     c.append(next_color_2)

    # for step in patterns.InwardSpiral(calib, colors.StandardColor.from_name(calib, "dark_lime_1")).all_steps():
    #     step()
    #     patterns.OutwardSpiral(calib, colors.StandardColor.from_name(calib, next_color_2)).step_all()

    # patterns.PaletteTest1(calib).step_all()
    # patterns.PaletteTest2(calib).step_all()
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
    # pattern_palette_test_1(calib)
    # patterns.palette_test_2(calib)

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


if __name__ == "__main__":
    main()
