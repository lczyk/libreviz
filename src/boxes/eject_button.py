import os

from pynput import keyboard


def on_press(key):
    if key == keyboard.Key.esc:
        # Graceless exit
        os._exit(0)


def arm():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.wait()

    print("Press ESC to exit the script.")
