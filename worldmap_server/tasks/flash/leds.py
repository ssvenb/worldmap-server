from ...abstract_task import FlashTask
from ... import ledmodule
from ...utils import db_connection


class ExecutableTask(FlashTask):
    def __init__(self, pixels):
        super().__init__(pixels)

    @db_connection
    def get_leds_flash(self, cursor, axis, index, width):
        cursor.execute(
            f"SELECT * FROM leds WHERE {axis}>0 AND {axis}>{int(index) - int(width)} AND {axis}<{int(index) + int(width)}"
        )
        leds = cursor.fetchall()
        return leds

    def _fetch_elements(self, index):
        leds = self.get_leds_flash(self.config_params["axis"], index, self.config_params["width"])
        return leds

    def _modify_lights(self, leds):
        bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for led in leds:
            if led[1] > 0:
                bitmap[led[0]] += led[1]
        ledmodule.light(bitmap)
