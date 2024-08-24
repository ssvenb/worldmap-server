import time
import math
from multiprocessing import Process

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
        if sleep_time is None:
            self.sleep_time = 0.01
        else:
            self.sleep_time = float(sleep_time)
    
    def start():
        raise NotImplementedError()

class MulticolorTransitionTask(Task):
    def __init__(self, pixels, sleep_time):
        super().__init__(pixels, sleep_time)
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

class BlinkTask(Task):
    def __init__(self, pixels, color, sleep_time):
        if sleep_time is None:
            sleep_time = 1
        super().__init__(pixels, float(sleep_time))
        self.color = color

    def start(self):
        while True:
            self.pixels.fill(self.color)
            time.sleep(self.sleep_time)
            self.pixels.fill((0, 0, 0))
            time.sleep(self.sleep_time)