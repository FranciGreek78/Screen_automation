import time
import pygetwindow as gw
import pyautogui
import logging
from screen_automation_copy import KeyBind_Manager
from threading import Event
import math

import math

def circle_border_pixels(radius: int, cx: int = 0, cy: int = 0):
    """
    Restituisce una lista di coordinate (x, y) dei pixel sul bordo di un cerchio.
    """
    points = set()
    for deg in range(360):
        rad = math.radians(deg)
        x = round(cx + radius * math.cos(rad))
        y = round(cy + radius * math.sin(rad))
        points.add((x, y))
    return sorted(points)

def clamp_to_circle(x: int, y: int, cx: int, cy: int, radius: int, border_coords: list[tuple[int, int]]):
    """
    Se il punto (x, y) è fuori dal cerchio di centro (cx, cy) e raggio `radius`,
    sposta il mouse al punto più vicino sul bordo.
    """
    dx = x - cx
    dy = y - cy
    dist = math.sqrt(dx*dx + dy*dy)

    # se è dentro o sul bordo → non fare nulla
    if dist <= radius:
        return

    # trova la coordinata più vicina sul bordo
    closest = min(border_coords, key=lambda p: (p[0] - x)**2 + (p[1] - y)**2)
    pyautogui.moveTo(closest[0], closest[1])

def find_window():
    return any(title.strip() == window_name for title in gw.getAllTitles())

def InGame_Toggle():
    if InGame.is_set():
        InGame.clear()
        return
    InGame.set()

    
def Cancel_Skill():
    pyautogui.moveTo(middle_x, middle_y)  
    
KB = KeyBind_Manager()

window_name = "Brawlstars"
Process = Event()
Process.set()
InGame = Event()
screen_width, screen_height = pyautogui.size()
middle_x = screen_width / 2
middle_y = screen_height / 2
distance_from_center = 400
left_max_distance = middle_x - distance_from_center - 100
right_max_distance = middle_x + distance_from_center + 100
top_max_distance = middle_y - distance_from_center
bottom_max_distance = middle_y + distance_from_center

joystick_range_border = circle_border_pixels(distance_from_center, middle_x, middle_y)

if __name__ == "__main__":

    KB.upload_keybind_function('v', InGame_Toggle)
    KB.upload_keybind_function('middle_m', Cancel_Skill)
    
    
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Waiting for {window_name} to start...")

    while not find_window():
        time.sleep(0.7)

    logging.info(f"{window_name} detected! Monitoring started.")

    try:
        while Process.is_set():
            if find_window():
                active_window = gw.getActiveWindow()
                if active_window and active_window.title.strip() == window_name and InGame.is_set():
                    x, y= pyautogui.position()
                    clamp_to_circle(x, y, middle_x, middle_y, distance_from_center, joystick_range_border)
            else:
                logging.info(f"{window_name} closed. Exiting script.")
                Process.clear()
            time.sleep(0.05)
            

            time.sleep(0.05)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        logging.info("Script stopped.")
