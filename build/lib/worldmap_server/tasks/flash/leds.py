from ...abstract_task import FlashTask
from ... import ledmodule
from ...utils import try_start_task

class LedFlashTask(FlashTask):
    def __init__(self, pixels, args):
        super().__init__(pixels, args)

    def fetch_elements(self, index):
        leds = self.dataProvider.get_leds_flash(self.axis, index, self.width)
        return leds
    
    def modify_lights(self, leds):
        bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for led in leds:
            if led[1] > 0:
                bitmap[led[0]] += led[1]
        ledmodule.light(bitmap)

def run(taskManager, pixels, args):
    return try_start_task(taskManager, LedFlashTask(pixels, args), pixels)

def get_ui_types():
    return LedFlashTask(None, {}).ui_types