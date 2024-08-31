import time
from ..abstract_task import ColorTask

class ExecutableTask(ColorTask):
    def __init__(self, pixels):
        super().__init__(pixels)

    def _start(self):
        while True:
            self.pixels.fill(self.config_params["color"])
            time.sleep(self.config_params["time"])
            self.pixels.fill((0, 0, 0))
            time.sleep(self.config_params["time"])
