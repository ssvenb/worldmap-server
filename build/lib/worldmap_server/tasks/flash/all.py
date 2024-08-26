from .leds import LedFlashTask
from .neopixels import NeopixelFlashTask
from ...utils import try_start_task

class AllFlashTask(NeopixelFlashTask, LedFlashTask):
    def __init__(self, pixels, args):
        NeopixelFlashTask.__init__(self, pixels, args)
        LedFlashTask.__init__(self, pixels, args)

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

def run(taskManager, pixels, args):
    return try_start_task(taskManager, AllFlashTask(pixels, args), pixels)

def get_ui_types():
    return AllFlashTask(None, {}).ui_types