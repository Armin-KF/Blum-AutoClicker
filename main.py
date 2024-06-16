import cv2
import numpy as np
import pyautogui
import time
import keyboard
import pygetwindow as gw
import threading

pyautogui.FAILSAFE = True

show_detection = False

def get_active_window():
    try:
        window = gw.getActiveWindow()
        if window is None or window.title == "":
            raise Exception("No active window found.")
        return window
    except Exception as e:
        print(f"Error: {e}")
        return None

def capture_game_window_by_properties(x, y, width, height):
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    screenshot = cv2.resize(screenshot, (width // 2, height // 2))
    return screenshot

def detect_green_bubbles_and_bombs(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    lower_blue = np.array([105, 50, 50])
    upper_blue = np.array([135, 255, 255])
    lower_gray = np.array([0, 0, 50])
    upper_gray = np.array([180, 50, 200])
    lower_bomb = np.array([0, 0, 0])
    upper_bomb = np.array([180, 255, 50])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)
    mask_bomb = cv2.inRange(hsv, lower_bomb, upper_bomb)
    mask = cv2.bitwise_or(mask_green, mask_blue)
    mask = cv2.bitwise_and(mask, cv2.bitwise_not(mask_gray))
    mask = cv2.bitwise_and(mask, cv2.bitwise_not(mask_bomb))
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    green_bubbles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 50 < area < 1000:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cX *= 2
                cY *= 2
                green_bubbles.append((cX, cY))
    contours, _ = cv2.findContours(mask_bomb, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bombs = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 50 < area < 875:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cX *= 2
                cY *= 2
                bombs.append((cX, cY))
    return green_bubbles, bombs

def click_on_bubble(bubble, bombs, window_x, window_y):
    safety_margin = 50
    safe_to_click = True
    for bomb in bombs:
        distance = np.sqrt((bubble[0] - bomb[0])**2 + (bubble[1] - bomb[1])**2)
        if distance < safety_margin:
            safe_to_click = False
            break
    if safe_to_click:
        screen_x = bubble[0] + window_x
        screen_y = bubble[1] + window_y
        pyautogui.moveTo(screen_x, screen_y)
        pyautogui.click()

class StopException(Exception):
    pass

running = False

def toggle_running():
    global running
    running = not running
    print(f"Running: {running}")

def stop_running():
    global running
    running = False
    raise StopException

keyboard.add_hotkey('p', toggle_running)
keyboard.add_hotkey('q', stop_running)
keyboard.add_hotkey('s', lambda: toggle_running() if not running else None)

if __name__ == "__main__":
    start_time = time.time()
    try:
        while True:
            if running:
                if time.time() - start_time > 100:
                    print("100 seconds have passed. Stopping the script.")
                    raise StopException
                try:
                    active_window = get_active_window()
                    if active_window is None:
                        continue
                    window_x, window_y, window_width, window_height = active_window.left, active_window.top, active_window.width, active_window.height
                    screen = capture_game_window_by_properties(window_x, window_y, window_width, window_height)
                    green_bubbles, bombs = detect_green_bubbles_and_bombs(screen)
                    for bubble in green_bubbles:
                        threading.Thread(target=click_on_bubble, args=(bubble, bombs, window_x, window_y)).start()
                    
                except pyautogui.FailSafeException:
                    print("FailSafe triggered. Stopping the script.")
                    raise StopException
                except Exception as e:
                    print(f"Error: {e}")
    except StopException:
        print("Script stopped.")
    finally:
        pass
