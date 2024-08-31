import sqlite3
import functools
from .config import Config
from .utils import InvalidInputParamsException, fill_bitmap

CONFIG = Config()

def _get_cursor():
    db_connection = sqlite3.connect(CONFIG.db_path)
    cursor = db_connection.cursor()
    return db_connection, cursor

def _close_cursor(db_connection):
    db_connection.commit()
    db_connection.close()

def db_connection(func):
    @functools.wraps(func)
    def db_connection_wrapper(self, *args, **kwargs):
        db_connection, cursor = _get_cursor()
        return_values = func(self, cursor, *args, **kwargs)
        _close_cursor(db_connection)
        return return_values
    return db_connection_wrapper

class DataProvider():
    def get_cursor(self):
        db_connection = sqlite3.connect(CONFIG.db_path)
        return db_connection.cursor()
    
    def _check_int(self, int_val, name):
        try:
            int(int_val)
        except:
            raise InvalidInputParamsException(f"{name} has to be of type int")
        
    def _check_axis(self, axis):
        valid_axis = CONFIG.axis_sections.keys()
        if axis not in valid_axis:
            raise InvalidInputParamsException(f"Axis has to be either {valid_axis[0]} or {valid_axis[1]}")
    
    def _check_flash_params(self, axis, index, width):
        self._check_axis(axis)
        self._check_int(index, "Index")
        self._check_int(width, "Width")

    def _get_country_bitmap(self, cursor, countries):
        bitmap = fill_bitmap(0)
        for country in countries:
            try:
                cursor.execute(f"SELECT register, number FROM leds WHERE country='{country}'")
                led = cursor.fetchall()[0]
                bitmap[led[0]] += led[1]
            except:
                raise InvalidInputParamsException(f"Invalid country provided")
        return bitmap
    
    def get_pixels_flash(self, axis, index, width):
        cursor = self.get_cursor()
        self._check_flash_params(axis, index, width)
        pixels = {}
        cursor.execute(f"SELECT * FROM neopixels WHERE {axis}>0 AND {axis}={int(index) - int(width)}")
        pixels["delete"] = cursor.fetchall()
        cursor.execute(f"SELECT * FROM neopixels WHERE {axis}>0 AND {axis}={int(index) + int(width)}")
        pixels["add"] = cursor.fetchall()
        return pixels
    
    def get_leds_flash(self, axis, index, width):
        self._check_flash_params(axis, index, width)
        cursor = self.get_cursor()
        cursor.execute(f"SELECT * FROM leds WHERE {axis}>0 AND {axis}>{int(index) - int(width)} AND {axis}<{int(index) + int(width)}")
        leds = cursor.fetchall()
        return leds