import time
from multiprocessing import Process, Queue
from .data_provider import DataProvider
from .config import Config
from .utils import hex_to_rgb, check_color, InvalidInputParamsException
from flask import request

DATA_PROVIDER = DataProvider()
CONFIG = Config()


class TaskManager:
    def __init__(self, pixels):
        self.pixels = pixels
        self.task = None
        self.ui_types = {}

    def start_task(self, task_obj, args=None):
        if args is None:
            args = request.args
        if self.task is not None:
            self.kill_task()
        queue = Queue()
        self.task = Process(target=lambda: task_obj.start(args, queue))
        self.task.start()
        error_message = queue.get(timeout=1)
        if error_message is not None:
            raise InvalidInputParamsException(error_message)

    def kill_task(self):
        if self.task is not None:
            self.task.kill()
            self.task.join()
            self.task = None


class Task:
    def __init__(self, pixels):
        if not hasattr(self, "arg_list"):
            self.arg_list = [
                ("time", self._check_float, CONFIG.task["default_time"], "Time has to be of type float")
            ]
        self.pixels = pixels
        self.config_params = {}
        self.args = None

    def _append_arg(self, arg):
        if arg[0] not in [params[0] for params in self.arg_list]:
            self.arg_list.append(arg)

    def _check_float(self, arg):
        return float(arg)
    
    def _check_int(self, arg):
        return int(arg)

    def _extract_arg(self, arg, check, default, error_message):
        if self.args.get(arg) is None:
            self.config_params[arg] = default
        else:
            try:
                self.config_params[arg] = check(self.args.get(arg))
            except:
                raise InvalidInputParamsException(error_message)
            
    def _extract_args(self, args):
        self.args = args
        for arg in self.arg_list:
            self._extract_arg(*arg)
    
    def _start(self):
        raise NotImplementedError()
    
    def start(self, args, queue):
        try:
            self._extract_args(args)
            queue.put(None)
            self._start()
        except InvalidInputParamsException as e:
            queue.put(e.get_exc())
    

class ColorTask(Task):
    def __init__(self, pixels):
        super().__init__(pixels)
        self._append_arg(("color", check_color, hex_to_rgb(CONFIG.task["default_color"]), "Color has to be in hex color scheme"))


class FlashTask(Task):
    def __init__(self, pixels):
        super().__init__(pixels)
        self.direction = "forward"
        self.index = 0
        self.lightmap = []
        self.number_sections = CONFIG.axis_sections
        self.dataProvider = DATA_PROVIDER
        self.axis_keys = list(CONFIG.axis_sections.keys())
        self._append_arg(("width", self._check_int, CONFIG.task["flash"]["default_width"], "Width has to be of type int"))
        self._append_arg(("axis", self._check_axis, CONFIG.task["flash"]["default_axis"], f"Axis has to either be {self.axis_keys[0]} or {self.axis_keys[1]}"))

    def _check_axis(self, axis):
        if axis not in self.axis_keys:
            raise Exception()
        return axis

    def _init_lightmap(self):
        for i in range(self.number_sections[self.config_params["axis"]]):
            self.lightmap.append(self._fetch_elements(i))

    def _fetch_elements(self):
        raise NotImplementedError()
    
    def _count(self):
        if self.direction == "forward":
            self.index += 1
        else:
            self.index -= 1
        if self.index >= self.number_sections[self.config_params["axis"]] - self.config_params["width"]:
            self.direction = "backward"
        if self.index <= self.config_params["width"]:
            self.direction = "forward"

    def _modify_lights(self):
        raise NotImplementedError()

    def _start(self):
        self._init_lightmap()
        while True:
            self._count()
            self._modify_lights(self.lightmap[self.index])
            time.sleep(self.config_params["time"])