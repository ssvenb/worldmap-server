import sqlite3
from .config import Config
from .utils import hex_to_rgb, fill_bitmap, InvalidInputParamsException

CONFIG = Config()

class DataProvider():
    def get_cursor(self):
        db_connection = sqlite3.connect(CONFIG.db_path)
        return db_connection.cursor()

    def get_countries(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT country FROM leds")
        countries = [country[0] for country in cursor.fetchall()]
        return countries
    
    def get_groups(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT name FROM groups")
        groups = [name[0] for name in cursor.fetchall()]
        return groups
    
    def _check_color(self, color):
        try:
            return hex_to_rgb(color)
        except:
            raise InvalidInputParamsException(f"Color has to be in hex color scheme")
        
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
    
    def create_group(self, name, color, countries):
        db_connection = sqlite3.connect(CONFIG.db_path)
        cursor = db_connection.cursor()
        self._check_color(color)
        bitmap = self._get_country_bitmap(cursor, countries)
        cursor.execute(
            '''INSERT INTO groups (
                name, 
                color, 
                ledbits_0, 
                ledbits_1,
                ledbits_2,
                ledbits_3,
                ledbits_4,
                ledbits_5,
                ledbits_6,
                ledbits_7,
                ledbits_8
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (name, color, *bitmap)
        )
        db_connection.commit()
        db_connection.close()

    def get_group(self, name):
        cursor = self.get_cursor()
        cursor.execute("SELECT * FROM groups WHERE name=?", (name,))
        group = cursor.fetchall()[0]
        bitmap = [group[2], group[3], group[4], group[5], group[6], group[7], group[8], group[9], group[10]]
        return hex_to_rgb(group[1]), bitmap
    
    def delete_group(self, name):
        db_connection = sqlite3.connect(CONFIG.db_path)
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM groups WHERE name=?", (name,))
        db_connection.commit()
        db_connection.close()

    def get_colors(self):
        cursor = self.get_cursor()
        cursor.execute("SELECT color FROM colors")
        colors = [color[0] for color in cursor.fetchall()]
        return colors

    def create_color(self, color):
        db_connection = sqlite3.connect(CONFIG.db_path)
        cursor = db_connection.cursor()
        self._check_color(color)
        cursor.execute("INSERT INTO colors ( color ) VALUES ( ? )", (color,))
        db_connection.commit()
        db_connection.close()

    def delete_color(self, color):
        db_connection = sqlite3.connect(CONFIG.db_path)
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM colors WHERE color=?", (color,))
        db_connection.commit()
        db_connection.close()
    
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