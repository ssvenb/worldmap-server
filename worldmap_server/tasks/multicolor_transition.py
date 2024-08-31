import math
import time
from ..abstract_task import Task
from ..config import Config

CONFIG = Config()

class ExecutableTask(Task):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.granularity = CONFIG.task["multicolor_transition"]["granularity"]
        self.max_range = int(math.pi / 2 * self.granularity)

    def transition(self, i):
        sin_value = math.sin(i / self.granularity)
        first = 255 - int(255 * sin_value)
        second = int(255 * sin_value)
        return first, second

    def _start(self):
        while True:
            r, g, b = [0, 0, 0]
            for i in range(self.max_range):
                r, g = self.transition(i)
                self.pixels.fill((r, g, b))
                time.sleep(self.config_params["time"])
            for i in range(self.max_range):
                g, b = self.transition(i) 
                self.pixels.fill((r, g, b))
                time.sleep(self.config_params["time"])
            for i in range(self.max_range):
                b, r = self.transition(i)
                self.pixels.fill((r, g, b))
                time.sleep(self.config_params["time"])