from ..utils import db_connection, get_country_bitmap
from .. import ledmodule


class DataProvider:
    def __init__(self, taskManager, pixels):
        self.taskManager = taskManager
        self.pixels = pixels

    @db_connection
    def get_all(self, cursor):
        cursor.execute("SELECT country FROM leds")
        countries = [country[0] for country in cursor.fetchall()]
        return countries

    def execute(self, country):
        bitmap = get_country_bitmap([country])
        ledmodule.light(bitmap)
