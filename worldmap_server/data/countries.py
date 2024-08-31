from ..data_provider import db_connection
from .. import ledmodule

class DataProvider():
    def __init__(self, taskManager, pixels):
        self.taskManager = taskManager
        self.pixels = pixels

    @db_connection
    def get_all(self, cursor):
        cursor.execute("SELECT country FROM leds")
        countries = [country[0] for country in cursor.fetchall()]
        return countries
    
    @db_connection
    def execute(self, cursor, country):
        bitmap = self._get_country_bitmap(cursor, [country])
        ledmodule.light(bitmap)