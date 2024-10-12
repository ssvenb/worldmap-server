from ...abstract_task import FlashTask, ColorTask
from ...utils import hex_to_rgb, check_color, db_connection
from ...config import Config

CONFIG = Config()


class ExecutableTask(FlashTask, ColorTask):
    def __init__(self, pixels):
        FlashTask.__init__(self, pixels)
        ColorTask.__init__(self, pixels)
        self.colors = None
        self._append_arg(
            (
                "background_color",
                check_color,
                hex_to_rgb(CONFIG.task["flash"]["neopixel"]["default_background_color"]),
                "Background Color has to be in hex color scheme",
            )
        )

    @db_connection
    def get_pixels_flash(self, cursor, axis, index, width):
        pixels = {}
        cursor.execute(f"SELECT * FROM neopixels WHERE {axis}>0 AND {axis}={int(index) - int(width)}")
        pixels["delete"] = cursor.fetchall()
        cursor.execute(f"SELECT * FROM neopixels WHERE {axis}>0 AND {axis}={int(index) + int(width)}")
        pixels["add"] = cursor.fetchall()
        return pixels

    def _fetch_elements(self, index):
        pixels = self.get_pixels_flash(self.config_params["axis"], index, self.config_params["width"])
        return pixels

    def __modify_lights(self, pixels_to_modify, color_1, color_2):
        for pixel in pixels_to_modify:
            if self.direction == "forward":
                self.pixels[pixel[0]] = color_1
            else:
                self.pixels[pixel[0]] = color_2

    def _modify_lights(self, pixels):
        self.__modify_lights(
            pixels["add"],
            self.config_params["color"],
            self.config_params["background_color"],
        )
        self.__modify_lights(
            pixels["delete"],
            self.config_params["background_color"],
            self.config_params["color"],
        )
