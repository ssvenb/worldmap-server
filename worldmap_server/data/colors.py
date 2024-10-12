from ..utils import check_color, db_connection


class DataProvider:
    def __init__(self, taskManager, pixels):
        self.taskManager = taskManager
        self.pixels = pixels

    @db_connection
    def get_all(self, cursor):
        cursor.execute("SELECT color FROM colors")
        colors = [color[0] for color in cursor.fetchall()]
        return colors

    @db_connection
    def delete(self, cursor, color):
        cursor.execute("DELETE FROM color WHERE name=?", (color,))

    @db_connection
    def create(self, cursor, color):
        check_color(color)
        cursor.execute("INSERT INTO colors ( color ) VALUES ( ? )", (color,))

    def execute(self, color):
        rgb_color = check_color(color)
        self.pixels.fill(rgb_color)
