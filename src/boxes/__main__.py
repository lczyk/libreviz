import json
import os
import sys
import time

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
    # pattern_palette_test_1(calib)
    patterns.palette_test_2(calib)

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
