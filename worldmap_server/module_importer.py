import sys
import os
import importlib.util
import json
from flask import request
from .utils import reset, InvalidInputParamsException


class ModuleImporter:
    def __init__(self, app, dir):
        self.app = app
        self.module_name = None
        self.module = None
        self.dir = dir

    def import_modules(self):
        parent_module_name = __name__.split(".")[0]
        self._import_modules(f"{parent_module_name}/{self.dir}")

    def _import_modules(self, dir, sub_module_name=""):
        sys.path.append(dir)
        dir_name = dir.split("/")[-1]
        sub_module_name += f".{dir_name}"
        for file_name in os.listdir(dir):
            if file_name == "__pycache__":
                continue
            if os.path.isdir(f"{dir}/{file_name}"):
                self._import_modules(f"{dir}/{file_name}", sub_module_name)
            else:
                self.module_name = f"{sub_module_name}.{file_name[:-3]}"
                self.module = importlib.import_module(self.module_name, "worldmap_server")
                self._register_endpoints()

    def _register_endpoints(self):
        raise NotImplementedError


class TaskModuleImporter(ModuleImporter):
    def __init__(self, app, taskManager, pixels):
        super().__init__(app, "tasks")
        self.taskManager = taskManager
        self.pixels = pixels
        self.ui_types = {}

    def _register_endpoints(self):
        def try_start_task(taskManager, task, pixels):
            try:
                reset(taskManager, pixels)
                taskManager.start_task(task)
                return "ok", 200
            except InvalidInputParamsException as e:
                return e.get_exc(), 400

        endpoint = self.module_name.replace(".", "/")
        executable_task = self.module.ExecutableTask(self.pixels)
        self.app.add_url_rule(
            endpoint,
            endpoint=endpoint,
            view_func=lambda: try_start_task(self.taskManager, executable_task, self.pixels),
        )
        self.taskManager.ui_types[self.module_name] = [param[0] for param in executable_task.arg_list]


class DataModuleImporter(ModuleImporter):
    def __init__(self, app, taskManager, pixels):
        super().__init__(app, "data")
        self.taskManager = taskManager
        self.pixels = pixels
        self.execute_path = None
        self.method_table = {
            "get_all": ("GET", False),
            "get": ("GET", True),
            "create": ("POST", False),
            "delete": ("DELETE", True),
            "execute": ("GET", True),
        }

    def _register_route(self, data_provider, method_name, endpoint, method):
        def route(*args):
            try:
                options = [*args]
                if method_name == "create":
                    received_data = json.loads(request.data)
                    for option in data_provider.data:
                        options.append(received_data.get(option))
                method = getattr(data_provider, method_name)
                if method_name == "execute":
                    reset(self.taskManager, self.pixels)
                return_value = method(*options)
                if return_value is not None:
                    return return_value, 200
                return "ok", 200
            except InvalidInputParamsException as e:
                return e.get_exc(), 400
            except:
                return "An error occured", 500

        if callable(getattr(data_provider.__class__, method_name, None)):
            http_method = method[0]
            use_subpath = method[1]
            rule = (
                f"{endpoint if method_name != 'execute' else self.execute_path}/<subpath>" if use_subpath else endpoint
            )

            def view_func(subpath=None):
                return route(subpath) if use_subpath else route()

            self.app.add_url_rule(
                rule,
                endpoint=f"{endpoint}_{method_name}",
                view_func=view_func,
                methods=[http_method],
            )

    def _register_endpoints(self):
        endpoint = self.module_name.replace(".", "/")
        self.execute_path = endpoint[len(endpoint.split("/")[1]) + 1 :]
        data_provider = self.module.DataProvider(self.taskManager, self.pixels)
        for method_name, method in self.method_table.items():
            self._register_route(data_provider, method_name, endpoint, method)
