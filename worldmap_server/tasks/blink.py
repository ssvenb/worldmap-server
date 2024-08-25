import time
from ..abstract_task import ColorTask
from ..utils import try_start_task

class BlinkTask(ColorTask):
    def __init__(self, pixels, args):
        super().__init__(pixels, args)

    def start(self):
        while True:
            self.pixels.fill(self.color)
            time.sleep(self.sleep_time)
            self.pixels.fill((0, 0, 0))
            time.sleep(self.sleep_time)

def run(taskManager, pixels, args):
    return try_start_task(taskManager, BlinkTask(pixels, args))

def get_ui_types():
    return BlinkTask(None, {}).ui_types