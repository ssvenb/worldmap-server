import time
from multiprocessing import Process
from .db import DataProvider, InvalidInputParamsException
from .config import Config
from .utils import hex_to_rgb

DATA_PROVIDER = DataProvider()
CONFIG = Config()


class TaskManager:
    def __init__(self, pixels):
        self.pixels = pixels
        self.task = None

    def start_task(self, task_obj):
        if self.task is not None:
            self.terminate_task()
        self.task = Process(target=task_obj.start)
        self.task.start()

    def terminate_task(self):
        if self.task is not None:
            self.task.terminate()
            self.task.join()
            self.task = None


class Task:
    def __init__(self, pixels, args):
        self.pixels = pixels
        self.ui_types = ["time"]
        if args.get("time") is None:
            self.sleep_time = CONFIG.task["default_time"]
        else:
            try:
                self.sleep_time = float(args.get("time"))
            except:
                raise InvalidInputParamsException("Time has to be of type float")
    
    def start():
        raise NotImplementedError()
    

class ColorTask(Task):
    def __init__(self, pixels, args):
        super().__init__(pixels, args)
        self.ui_types.append("color")
        if args.get("color") is None:
            self.color = hex_to_rgb(CONFIG.task["default_color"])
        else:
            try:
                self.color = hex_to_rgb(args.get("color"))
            except:
                raise InvalidInputParamsException("Color has to be in hex color scheme")


class FlashTask(Task):
    def __init__(self, pixels, args):
        super().__init__(pixels, args)
        self.ui_types.append("width")
        self.ui_types.append("axis")
        if args.get("width") is None:
            self.width = CONFIG.task["flash"]["default_width"]
        else:
            self.width = args.get("width")
        self.axis = CONFIG.task["flash"]["default_axis"]
        if args.get("axis") is not None:
            self.axis = args.get("axis")
        self.direction = "forward"
        self.index = 0
        self.lightmap = []
        self.number_sections = CONFIG.axis_sections
        self.dataProvider = DATA_PROVIDER

    def init_lightmap(self):
        for i in range(self.number_sections[self.axis]):
            self.lightmap.append(self.fetch_elements(i))

    def fetch_elements(self):
        raise NotImplementedError()
    
    def count(self):
        if self.direction == "forward":
            self.index += 1
        else:
            self.index -= 1
        if self.index >= self.number_sections[self.axis] - self.width:
            self.direction = "backward"
        if self.index <= self.width:
            self.direction = "forward"

    def modify_lights(self):
        raise NotImplementedError()

    def start(self):
        self.init_lightmap()
        self.width = int(self.width)
        while True:
            self.count()
            self.modify_lights(self.lightmap[self.index])
            time.sleep(self.sleep_time)