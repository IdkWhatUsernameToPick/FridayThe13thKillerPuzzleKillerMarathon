import time
import random
import numpy as np
import mss
import psutil
import win32gui
import win32process
import pydirectinput
import keyboard

def find_window_by_process_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
            pid = proc.info['pid']
            hwnds = []
            def callback(hwnd, _):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                    hwnds.append(hwnd)
                return True
            win32gui.EnumWindows(callback, None)
            if hwnds:
                return hwnds[0]
    return None

target_process = "F13.exe"
hwnd = find_window_by_process_name(target_process)
if hwnd is None:
    print(f"Could not find a visible window for {target_process}.")
    exit(1)
else:
    print(f"Found window handle {hwnd} for {target_process}.")

try:
    win32gui.SetForegroundWindow(hwnd)
except Exception as e:
    print("Unable to bring window to foreground:", e)

red_target_bgr = [26, 26, 146]
black_target_bgr = [0, 0, 0]

with mss.mss() as sct:
    region = {
        "top": 860,
        "left": 0,
        "width": 1920,
        "height": 61
    }
    
    print("Monitoring started. Press F6 to exit.")
    while True:
        if keyboard.is_pressed('F6'):
            print("F6 pressed. Exiting.")
            break

        sct_img = sct.grab(region)
        img = np.array(sct_img)

        row_860 = img[0, :, :3]
        row_920 = img[-1, :, :3]

        red_found = np.any(np.all(row_860 == red_target_bgr, axis=1))
        black_found = np.any(np.all(row_920 == black_target_bgr, axis=1))

        if red_found and black_found:
            print("Conditions met: pressing space key.")
            pydirectinput.press('space')
            delay = random.uniform(2, 3)
            time.sleep(delay)
        else:
            time.sleep(0.001)
