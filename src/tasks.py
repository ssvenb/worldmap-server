import time
import math
import ledmodule
from multiprocessing import Process
import sqlite3

db_path = "/home/weltkarte/worldmap-server/db.db"

class TaskManager:
    def __init__(self, pixels):
        self.pixels = pixels
        self.task = None

    def start_task(self, task_obj):
        if self.task is not None:
            self.terminate_task()
        self.task = Process(target=task_obj.start)
        self.task.start()

    def terminate_task(self):
        if self.task is not None:
            self.task.terminate()
            self.task.join()
            self.task = None

class Task:
    def __init__(self, pixels, sleep_time):
        self.pixels = pixels
        self.sleep_time = sleep_time
    
    def start():
        raise NotImplementedError()

class MulticolorTransitionTask(Task):
    def __init__(self, pixels):
        super().__init__(pixels, 0.001)
        self.granularity = 100
        self.max_range = int(math.pi / 2 * self.granularity)

    def transition(self, i):
        sin_value = math.sin(i / self.granularity)
        first = 255 - int(255 * sin_value)
        second = int(255 * sin_value)
        return first, second

    def start(self):
        while True:
            r, g, b = [0, 0, 0]
            for i in range(self.max_range):
                r, g = self.transition(i)
                self.pixels.fill((r, g, b))
                time.sleep(self.sleep_time)
            for i in range(self.max_range):
                g, b = self.transition(i) 
                self.pixels.fill((r, g, b))
                time.sleep(self.sleep_time)
            for i in range(self.max_range):
                b, r = self.transition(i)
                self.pixels.fill((r, g, b))
                time.sleep(self.sleep_time)

class FlashTask(Task):
    def __init__(self, pixels, width, axis):
        super().__init__(pixels, 0.01)
        db_connection = sqlite3.connect(db_path)
        self.cursor = db_connection.cursor()
        self.width = 2
        if width is not None:
            self.width = width
        self.axis = "latitude"
        if axis is not None:
            self.axis = axis
        self.direction = "right"
        self.index = 0
        self.lightmap = []
        self.number_sections = {
            "latitude": 19,
            "longitude": 12
        }

    def init_lightmap(self):
        for i in range(self.number_sections[self.axis]):
            self.lightmap.append(self.fetch_elements(i))

    def fetch_elements(self):
        raise NotImplementedError()
    
    def count(self):
        if self.index > self.number_sections[self.axis] - self.width:
            self.direction = "left"
        if self.index <= self.width:
            self.direction = "right"
        if self.direction == "right":
            self.index += 1
        else:
            self.index -= 1

    def modify_lights(self):
        raise NotImplementedError()

    def start(self):
        self.init_lightmap()
        while True:
            self.count()
            self.modify_lights(self.lightmap[self.index])
            time.sleep(self.sleep_time)


class NeopixelFlashTask(FlashTask):
    def __init__(self, pixels, color, width, axis):
        super().__init__(pixels, width, axis)
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
    def __init__(self, pixels, width, axis):
        super().__init__(pixels, width, axis)

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
    def __init__(self, pixels, color, width, axis):
        super().__init__(pixels=pixels, color=color, width=width, axis=axis)

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