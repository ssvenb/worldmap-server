import math
import time
from ..abstract_task import Task
from ..utils import try_start_task
from ..config import Config

CONFIG = Config()

class MulticolorTransitionTask(Task):
    def __init__(self, pixels, args):
        super().__init__(pixels, args)
        self.granularity = CONFIG.task["multicolor_transition"]["granularity"]
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

def run(taskManager, pixels, args):
    return try_start_task(taskManager, MulticolorTransitionTask(pixels, args))

def get_ui_types():
    return MulticolorTransitionTask(None, {}).ui_types