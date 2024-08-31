from . import ledmodule
from flask import jsonify
from .config import Config

CONFIG = Config()

class InvalidInputParamsException(Exception):
    def __init__(self, status):
        self.status = status

    def get_exc(self):
        return self.status

def hex_to_rgb(hexa):
    return tuple(int(hexa[i:i+2], 16)  for i in (0, 2, 4))

def fill_bitmap(number):
    bitmap = []
    for _ in range(CONFIG.register_count):
        bitmap.append(number)
    return bitmap

def kill_leds():
    bitmap = fill_bitmap(0)
    ledmodule.light(bitmap)

def all_leds():
    bitmap = fill_bitmap(65535)
    ledmodule.light(bitmap)

def reset(taskManager, pixels):
    taskManager.kill_task()
    kill_leds()
    pixels.fill((0, 0, 0))

def check_color(color):
    try:
        return hex_to_rgb(color)
    except:
        raise InvalidInputParamsException(f"Color has to be in hex color scheme")