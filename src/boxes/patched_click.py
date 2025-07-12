import sys

import pyautogui

if sys.platform == "darwin":
    import time

    import Quartz
    from pyautogui._pyautogui_osx import _sendMouseEvent

    def click(x: float, y: float) -> None:
        _sendMouseEvent(Quartz.kCGEventLeftMouseDown, x, y, Quartz.kCGMouseButtonLeft)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)
        _sendMouseEvent(Quartz.kCGEventLeftMouseUp, x, y, Quartz.kCGMouseButtonLeft)
        time.sleep(pyautogui.DARWIN_CATCH_UP_TIME)

        time.sleep(pyautogui.PAUSE)

else:

    def click(x: float, y: float) -> None:
        pyautogui.click(x, y, button=pyautogui.LEFT)
