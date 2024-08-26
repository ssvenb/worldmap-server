from ...abstract_task import FlashTask, ColorTask
from ...utils import try_start_task, hex_to_rgb, InvalidInputParamsException
from ...config import Config

CONFIG = Config()

class NeopixelFlashTask(FlashTask, ColorTask):
    def __init__(self, pixels, args):
        FlashTask.__init__(self, pixels, args)
        ColorTask.__init__(self, pixels, args)
        self.ui_types.append("background_color")
        if args.get("background_color") is None:
            self.background_color = hex_to_rgb(CONFIG.task["flash"]["neopixel"]["default_background_color"])
        else:
            try:
                self.background_color = hex_to_rgb(args.get("background_color"))
            except:
                raise InvalidInputParamsException("Color has to be in hex color scheme")
        self.colors = [self.color, self.background_color]

    def fetch_elements(self, index):
        pixels = self.dataProvider.get_pixels_flash(self.axis, index, self.width)
        return pixels

    def _modify_lights(self, pixels_to_modify, color_1, color_2):
        for pixel in pixels_to_modify:
            if self.direction == "forward":
                self.pixels[pixel[0]] = color_1
            else:
                self.pixels[pixel[0]] = color_2
    
    def modify_lights(self, pixels):
        self._modify_lights(pixels["add"], self.colors[0], self.colors[1])
        self._modify_lights(pixels["delete"], self.colors[1], self.colors[0])

def run(taskManager, pixels, args):
    return try_start_task(taskManager, NeopixelFlashTask(pixels, args), pixels)

def get_ui_types():
    return NeopixelFlashTask(None, {}).ui_types