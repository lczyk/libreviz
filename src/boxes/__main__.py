import json
import os
import sys

import pyautogui

from . import eject_button
from .calibrate import CalibrationData, calibrate
from .run import run

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


if __name__ == "__main__":
    main()
