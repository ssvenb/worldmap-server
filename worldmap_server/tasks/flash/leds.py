from ...abstract_task import FlashTask
from ... import ledmodule

class ExecutableTask(FlashTask):
    def __init__(self, pixels):
        super().__init__(pixels)

    def _fetch_elements(self, index):
        leds = self.dataProvider.get_leds_flash(self.config_params["axis"], index, self.config_params["width"])
        return leds
    
    def _modify_lights(self, leds):
        bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for led in leds:
            if led[1] > 0:
                bitmap[led[0]] += led[1]
        ledmodule.light(bitmap)
