import win32gui
import win32con
import win32api
import time
from random import random
from pynput import keyboard as pynput_keyboard
from threading import Thread, Event
import sys

# GLOBALS
window_title = "Growtopia"
hits_to_break = 4
break_key = 'E'
script_name = sys.argv[0]
running = False
stop_event = Event()

if len(sys.argv) > 1:
    hits_to_break = int(sys.argv[1])


def human_random():
    return random() / 4


def get_window_handle(window_title):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and window_title in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None


def get_cursor_pos_window(width, height, rect):
    x, y = win32api.GetCursorPos()
    window_x, window_y, _, _ = rect

    rel_x = x - window_x
    rel_y = y - window_y

    rel_x = max(0, min(rel_x, width - 1))
    rel_y = max(0, min(rel_y, height - 1))

    return rel_x, rel_y


def hold_key(hwnd, key):
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, key, 0)


def release_key(hwnd, key):
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, key, 0)


def move_mouse(hwnd, x, y):
    win32api.SendMessage(hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(x, y))


def click_mouse(hwnd, x, y):
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, 0, win32api.MAKELONG(x, y))
    time.sleep(human_random())
    win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(x, y))


def zoom_setup(hwnd):
    for _ in range(20):
        win32api.SendMessage(hwnd, win32con.WM_MOUSEWHEEL, -300, 0)
    for _ in range(15):
        win32api.SendMessage(hwnd, win32con.WM_MOUSEWHEEL, 300, 0)
    time.sleep(5)


def toggle_script(hwnd):
    global running
    running = not running
    print("Script is now", "running" if running else "stopped")
    if running:
        zoom_setup(hwnd)

def farm(hwnd, center_x, center_y):
    human_random_offset = human_random() * 10
    block_1 = center_x + 150 + human_random_offset
    block_2 = center_x + 300 + human_random_offset
    move_mouse(hwnd, int(block_1), center_y)
    click_mouse(hwnd, int(block_1), center_y)
    time.sleep(human_random())
    move_mouse(hwnd, int(block_2), center_y)
    click_mouse(hwnd, int(block_2), center_y)
    time.sleep(human_random())

    hold_key(hwnd, ord(break_key))
    time.sleep(0.52 * hits_to_break)
    release_key(hwnd, ord(break_key))
    time.sleep(human_random())


def farming_loop():

    hwnd = get_window_handle(window_title)

    if hwnd:
        print(f"Found window: {window_title}, press F8 to toggle the script, CTRL + C to exit.")
        window_rect = win32gui.GetWindowRect(hwnd)
        window_width = window_rect[2] - window_rect[0]
        window_height = window_rect[3] - window_rect[1]
        center_x = window_width // 2
        center_y = window_height // 2

        global scroll_flag
        while not stop_event.is_set():
            if running:
                farm(hwnd, center_x, center_y)
            time.sleep(0.1)


def on_press(key):
    try:
        if key == pynput_keyboard.Key.f8:
            hwnd = get_window_handle(window_title)
            if hwnd:
                toggle_script(hwnd)
    except AttributeError:
        pass


def main():
    farming_thread = Thread(target=farming_loop)
    farming_thread.start()

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nScript terminating...")
        stop_event.set()
        farming_thread.join()
        listener.stop()
        print("Script terminated.")


if __name__ == "__main__":
    main()
