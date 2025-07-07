import os
import sys
import pyautogui

print(sys.argv)

if len(sys.argv) == 1:
    # display a message box to check whether we want to proceed
    response = pyautogui.confirm(
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
        exit()

    # call self with 'run' argument and replace the current process
    os.execv(sys.executable, [sys.executable] + ["boxes.py", "run1"])

elif sys.argv[1] == "run1":
    # 1 on most monitors, 2 on high DPI monitors
    DPI = 2

    # check that 'top_left.png' exists
    if not os.path.exists("./top_left.png"):
        print("Error: top_left.png not found.")
        exit()

    # locate the image on the screen
    location1 = None

    try:
        location1 = pyautogui.locateOnScreen("top_left.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        pass

    if location1 is None:
        print("Error: top_left.png not found on screen.")
        exit()

    try:
        location2 = pyautogui.locateOnScreen("bucket.png", confidence=0.8)
    except pyautogui.ImageNotFoundException:
        location2 = None

    if location2 is None:
        print("Error: bucket.png not found on screen.")
        exit()

    print("top_left.png location:", location1)
    print("bucket.png location:", location2)

    screen_size = pyautogui.size()
    print(f"Screen size: {screen_size}")

    # top left cell
    top_left_cell = (
        location1.left / DPI + 73,
        location1.top / DPI + location1.height / DPI - 30,
    )
    pyautogui.moveTo(*top_left_cell)

    pyautogui.sleep(0.1)

    # top right cell
    top_right_cell = (
        screen_size.width - 105,
        top_left_cell[1],
    )
    pyautogui.moveTo(*top_right_cell)

    pyautogui.sleep(0.1)

    # bottom left cell
    bottom_left_cell = (
        top_left_cell[0],
        screen_size.height - 70,
    )
    pyautogui.moveTo(*bottom_left_cell)

    pyautogui.sleep(0.1)

    # bottom right cell
    bottom_right_cell = (
        top_right_cell[0],
        bottom_left_cell[1],
    )

    pyautogui.moveTo(*bottom_right_cell)

    pyautogui.sleep(0.1)

    # move to the bucket icon
    bucket_location = (
        location2.left / DPI + 120,
        location2.top / DPI + location2.height / DPI - 30,
    )
    pyautogui.moveTo(*bucket_location)
    pyautogui.click()

    no_fill_location = (
        bucket_location[0] - 10,
        bucket_location[1] + 50,
    )

    pyautogui.moveTo(*no_fill_location)

    pyautogui.sleep(0.2)

    top_left_color = (
        bucket_location[0] - 20,
        bucket_location[1] + 120,
    )

    pyautogui.moveTo(*top_left_color)

    pyautogui.sleep(0.2)

    bottom_right_color = (
        top_left_color[0] + 190,
        top_left_color[1] + 155,
    )

    pyautogui.moveTo(*bottom_right_color)

    pyautogui.sleep(0.2)

    pyautogui.moveTo(*top_left_cell)
    pyautogui.click()

    # display a message box to check whether we want to proceed
    response = pyautogui.confirm(
        text="Was that correct?", title="Boxes", buttons=["Yes", "No"]
    )

    if response == "No":
        print("Exiting script.")
        exit()

    x1 = int(top_left_cell[0])
    y1 = int(top_left_cell[1])
    x2 = int(bottom_right_cell[0])
    y2 = int(bottom_right_cell[1])
    bx = int(bucket_location[0])
    by = int(bucket_location[1])
    
    # colors
    cx1 = int(no_fill_location[0])
    cy1 = int(no_fill_location[1])
    cx2 = int(top_left_color[0])
    cy2 = int(top_left_color[1])
    cx3 = int(bottom_right_color[0])
    cy3 = int(bottom_right_color[1])

    # call self with 'run2' argument and replace the current process
    os.execv(
        sys.executable,
        [sys.executable] + ["boxes.py", "run2", str(x1), str(y1), str(x2), str(y2), str(bx), str(by),
        str(cx1), str(cy1), str(cx2), str(cy2), str(cx3), str(cy3)],
    )

elif sys.argv[1] == "run2":

    # get coordinates from command line arguments
    x1 = int(sys.argv[2])
    y1 = int(sys.argv[3])
    x2 = int(sys.argv[4])
    y2 = int(sys.argv[5])
    bx = int(sys.argv[6])
    by = int(sys.argv[7])
    cx1 = int(sys.argv[8])
    cy1 = int(sys.argv[9])
    cx2 = int(sys.argv[10])
    cy2 = int(sys.argv[11])
    cx3 = int(sys.argv[12])
    cy3 = int(sys.argv[13])

    print(f"Top left cell: ({x1}, {y1})")
    print(f"Bottom right cell: ({x2}, {y2})")
    print(f"Bucket location: ({bx}, {by})")
    print(f"No fill color location: ({cx1}, {cy1})")
    print(f"Top left color location: ({cx2}, {cy2})")
    print(f"Bottom right color location: ({cx3}, {cy3})")

    N_COLS = 19
    N_ROWS = 52

    N_COLOR_COLS = 12
    N_COLOR_ROWS = 10

    def move_to_cell_i(col, row):
        """Move to the specified cell in the grid by index."""
        width = x2 - x1
        height = y2 - y1
        cell_width = width / (N_COLS - 1)
        cell_height = height / (N_ROWS - 1)
        x = x1 + cell_width * col
        y = y1 + cell_height * row
        pyautogui.moveTo(x, y)

    def move_to_cell_x(col: str, row: "str | int"):
        """Move to the specified cell in the grid by column letter and row number."""
        col_index = ord(col.upper()) - ord('A')
        if col_index < 0 or col_index >= N_COLS:
            raise ValueError(f"Column {col} is out of range.")
        row_index = int(row) - 1
        if row_index < 0 or row_index >= N_ROWS:
            raise ValueError(f"Row {row} is out of range.")
        move_to_cell_i(col_index, row_index)

    def select_range_fast(col1: str, row1: "str | int", col2: str, row2: "str | int"):
        """Select a range of cells from (col1, row1) to (col2, row2)."""
        move_to_cell_x(col1, row1)
        pyautogui.click()
        move_to_cell_x(col2, row2)
        pyautogui.keyDown('shift')
        pyautogui.click()
        pyautogui.keyUp('shift')

    def open_bucket():
        """Open the bucket tool in LibreOffice."""
        pyautogui.moveTo(bx, by)
        pyautogui.click()
    
    def move_to_color_i(col_i: int, row_i: int):
        """Move to the specified color cell in the color palette."""
        width = cx3 - cx2
        height = cy3 - cy2
        color_cell_width = width / (N_COLOR_COLS - 1)
        color_cell_height = height / (N_COLOR_ROWS - 1)
        x = cx2 + color_cell_width * col_i
        y = cy2 + color_cell_height * row_i
        pyautogui.moveTo(x, y)
    
    def move_to_no_fill():
        """Move to the 'No Fill' color cell in the color palette."""
        pyautogui.moveTo(cx1, cy1)
    
    global LAST_COLOR
    LAST_COLOR = None

    def apply_color_i(col_i: int, row_i: int):
        """Apply the color from the specified color cell in the color palette."""
        global LAST_COLOR
        this_color = (col_i, row_i)
        if this_color == LAST_COLOR:
            # apply the same color again
            pyautogui.moveTo(bx-20, by)
            pyautogui.click()  # click to close the bucket if the same color is applied
        else:
            # change color
            open_bucket()
            move_to_color_i(col_i, row_i)
            pyautogui.click()

        LAST_COLOR = this_color
    
    def apply_no_fill():
        """Apply 'No Fill' color to the selected cells."""
        open_bucket()
        move_to_no_fill()
        pyautogui.click()

    def reset_all_colors():
        """Reset all colors in the grid to 'No Fill'."""
        select_range_fast('A', 1, 'S', 52)
        apply_no_fill()
        pyautogui.sleep(0.1)

    reset_all_colors()

    lime = (N_COLOR_COLS - 1, 1)

    nodes = [
        ('A', 1), ('S', 1),
        ('S', 52), ('A', 52),
        ('A', 3), ('Q', 3),
        ('Q', 50), ('C', 50),
        ('C', 5), ('O', 5),
        ('O', 48), ('E', 48),
        ('E', 7), ('M', 7),
        ('M', 46), ('G', 46),
        ('G', 9), ('K', 9),
        ('K', 44), ('I', 44),
        ('I', 11)
    ]


    from itertools import tee
    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    # move_to_cell_x("B", 2)
    # pyautogui.mouseDown()
    # pyautogui.moveRel(200, 200, duration=1.0)
    # pyautogui.mouseUp()

    pyautogui.PAUSE = 0.05
    # pyautogui.PAUSE = 0.0
    
    # import random

    for n1, n2 in pairwise(nodes):
        select_range_fast(n1[0], n1[1], n2[0], n2[1])
        apply_color_i(*lime)
        # random_color_row = random.randint(0, N_COLOR_ROWS - 1)
        # random_color_col = random.randint(0, N_COLOR_COLS - 1)
        # apply_color_i(random_color_col, random_color_row)
