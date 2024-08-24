import ledmodule
import sqlite3
import time
import os
from tasks import Task


class FlashTask(Task):
    def __init__(self, pixels, width, axis, sleep_time):
        super().__init__(pixels, sleep_time)
        db_connection = sqlite3.connect(os.environ.get("DB_PATH"))
        self.cursor = db_connection.cursor()
        if width is None:
            self.width = 2
        else:
            self.width = int(width)
        self.axis = "latitude"
        if axis is not None:
            self.axis = axis
        self.direction = "right"
        self.index = 0
        self.lightmap = []
        self.number_sections = {
            "latitude": 19,
            "longitude": 13
        }

    def init_lightmap(self):
        for i in range(self.number_sections[self.axis]):
            self.lightmap.append(self.fetch_elements(i))

    def fetch_elements(self):
        raise NotImplementedError()
    
    def count(self):
        if self.direction == "right":
            self.index += 1
        else:
            self.index -= 1
        if self.index >= self.number_sections[self.axis] - self.width:
            self.direction = "left"
        if self.index <= self.width:
            self.direction = "right"

    def modify_lights(self):
        raise NotImplementedError()

    def start(self):
        self.init_lightmap()
        while True:
            self.count()
            self.modify_lights(self.lightmap[self.index])
            time.sleep(self.sleep_time)


class NeopixelFlashTask(FlashTask):
    def __init__(self, pixels, color, width, axis, sleep_time):
        super().__init__(pixels, width, axis, sleep_time)
        self.colors = [color, (0, 0, 0)]

    def fetch_elements(self, index):
        pixels = {}
        self.cursor.execute(f"SELECT * FROM neopixels WHERE {self.axis}>0 AND {self.axis}={index - self.width}")
        pixels["delete"] = self.cursor.fetchall()
        self.cursor.execute(f"SELECT * FROM neopixels WHERE {self.axis}>0 AND {self.axis}={index + self.width}")
        pixels["add"] = self.cursor.fetchall()
        return pixels

    def _modify_lights(self, pixels_to_modify, color_1, color_2):
        for pixel in pixels_to_modify:
            if self.direction == "right":
                self.pixels[pixel[0]] = color_1
            else:
                self.pixels[pixel[0]] = color_2
    
    def modify_lights(self, pixels):
        self._modify_lights(pixels["add"], self.colors[0], self.colors[1])
        self._modify_lights(pixels["delete"], self.colors[1], self.colors[0])

class LedFlashTask(FlashTask):
    def __init__(self, pixels, width, axis, sleep_time):
        super().__init__(pixels, width, axis, sleep_time)

    def fetch_elements(self, index):
        self.cursor.execute(f"SELECT * FROM leds WHERE {self.axis}>0 AND {self.axis}>{index - self.width} AND {self.axis}<{index + self.width}")
        leds = self.cursor.fetchall()
        return leds
    
    def modify_lights(self, leds):
        bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for led in leds:
            if led[1] > 0:
                bitmap[led[0]] += led[1]
        ledmodule.light(bitmap)

class AllFlashTask(NeopixelFlashTask, LedFlashTask):
    def __init__(self, pixels, color, width, axis, sleep_time):
        super().__init__(pixels, color, width, axis, sleep_time)

    def fetch_elements(self, i):
        pixels = NeopixelFlashTask.fetch_elements(self, i)
        leds = LedFlashTask.fetch_elements(self, i)
        return {
            "add": pixels["add"],
            "delete": pixels["delete"],
            "leds": leds
        }

    def modify_lights(self, lights):
        NeopixelFlashTask.modify_lights(self, lights)
        LedFlashTask.modify_lights(self, lights["leds"])