from ..data_provider import db_connection
from ..utils import hex_to_rgb, check_color, InvalidInputParamsException
from .. import ledmodule
from ..config import Config

CONFIG = Config()

class DataProvider():
    def __init__(self, taskManager, pixels):
        self.taskManager = taskManager
        self.pixels = pixels

    @db_connection
    def get_all(self, cursor):
        cursor.execute("SELECT name FROM groups")
        groups = [name[0] for name in cursor.fetchall()]
        return groups
    
    @db_connection
    def get(self, cursor, name):
        group_dict = {}
        self._group_needs_to_exist(cursor, name)
        cursor.execute("SELECT * FROM groups WHERE name=?", (name,))
        group = cursor.fetchall()
        group_dict["name"] = group[0][0]
        group_dict["color"] = group[0][1]
        group_dict["countries"] = []
        for register in range(CONFIG.register_count):
            number = 65536
            bitmap = group[0][register + 2]
            while number >= 1:
                number = number / 2
                if bitmap - number >= 0:
                    bitmap = bitmap - number
                    cursor.execute("SELECT country FROM leds WHERE register=? AND number=?", (register, number))
                    group_dict["countries"].append(cursor.fetchall()[0][0])
        return group_dict
    
    @db_connection
    def _get_lights(self, cursor, name):
        cursor.execute("SELECT * FROM groups WHERE name=?", (name,))
        group = cursor.fetchall()[0]
        bitmap = [group[2], group[3], group[4], group[5], group[6], group[7], group[8], group[9], group[10]]
        return hex_to_rgb(group[1]), bitmap
    
    def _group_cannot_exist(self, cursor, name):
        cursor.execute("SELECT * FROM GROUPS WHERE name=?", (name,))
        if len(cursor.fetchall()) > 0:
            raise InvalidInputParamsException("Group already exists")
        
    def _group_needs_to_exist(self, cursor, name):
        cursor.execute("SELECT * FROM GROUPS WHERE name=?", (name,))
        if len(cursor.fetchall()) == 0:
            raise InvalidInputParamsException("Group does not exist")
    
    @db_connection
    def create(self, cursor, name, color, countries):
        self._group_cannot_exist(cursor, name)
        check_color(color)
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

    @db_connection
    def delete(self, cursor, name):
        cursor.execute("DELETE FROM groups WHERE name=?", (name,))

    @db_connection
    def execute(self, cursor, name):
        self._group_needs_to_exist(cursor, name)
        color, bitmap = self._get_lights(name)
        self.pixels.fill(color)
        ledmodule.light(bitmap)
