from . import leds
from . import neopixels


class ExecutableTask(neopixels.ExecutableTask, leds.ExecutableTask):
    def __init__(self, pixels):
        neopixels.ExecutableTask.__init__(self, pixels)
        leds.ExecutableTask.__init__(self, pixels)

    def _fetch_elements(self, i):
        pixels = neopixels.ExecutableTask._fetch_elements(self, i)
        leds_bitmap = leds.ExecutableTask._fetch_elements(self, i)
        return {"add": pixels["add"], "delete": pixels["delete"], "leds": leds_bitmap}

    def _modify_lights(self, lights):
        neopixels.ExecutableTask._modify_lights(self, lights)
        leds.ExecutableTask._modify_lights(self, lights["leds"])
