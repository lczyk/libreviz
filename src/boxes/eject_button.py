import os

from pynput import keyboard


def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
    if key == keyboard.Key.esc:
        # Graceless exit
        os._exit(0)


def arm() -> None:
    """Arms the eject button functionality by setting up a keyboard listener."""
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.wait()

    print("Press ESC to exit the script.")
