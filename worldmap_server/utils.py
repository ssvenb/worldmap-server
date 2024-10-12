from . import ledmodule
from .config import Config
import sqlite3
import functools

CONFIG = Config()


class InvalidInputParamsException(Exception):
    def __init__(self, status):
        self.status = status

    def get_exc(self):
        return self.status


def db_connection(func):
    @functools.wraps(func)
    def db_connection_wrapper(self, *args, **kwargs):
        db_connection = sqlite3.connect(CONFIG.db_path)
        cursor = db_connection.cursor()
        return_values = func(self, cursor, *args, **kwargs)
        db_connection.commit()
        db_connection.close()
        return return_values

    return db_connection_wrapper


@db_connection
def get_country_bitmap(countries, cursor):
    bitmap = fill_bitmap(0)
    for country in countries:
        try:
            cursor.execute(f"SELECT register, number FROM leds WHERE country='{country}'")
            led = cursor.fetchall()[0]
            bitmap[led[0]] += led[1]
        except:
            raise InvalidInputParamsException(f"Invalid country provided")
    return bitmap


def hex_to_rgb(hexa):
    return tuple(int(hexa[i : i + 2], 16) for i in (0, 2, 4))


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
