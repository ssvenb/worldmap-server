from . import ledmodule
import board
import neopixel
import os
import signal
import sys
import importlib.util
import json
from flask import Flask, request, jsonify
from .db import DataProvider
from .utils import hex_to_rgb, kill_leds, all_leds, reset
from .config import Config
from .abstract_task import TaskManager
from .tasks.blink import BlinkTask

CONFIG = Config()
PIXELS = neopixel.NeoPixel(board.D18, CONFIG.led_count)

app = Flask(__name__)
dataProvider = DataProvider()
taskManager = TaskManager(PIXELS)
ui_types = {}

@app.route("/leds/all", methods=["GET"])
def leds_all():
    all_leds()
    return "ok", 200

@app.route("/leds/kill", methods=["GET"])
def leds_kill():
    kill_leds()
    return "ok", 200

@app.route("/neopixel/<hex_color>", methods=["GET"])
def light_neopixel(hex_color):
    reset(taskManager, PIXELS)
    PIXELS.fill(hex_to_rgb(hex_color))
    return "ok", 200

@app.route("/tasks/terminate", methods=["GET"])
def terminate():
    reset(taskManager, PIXELS)
    return "ok", 200

@app.route("/countries", methods=["GET"])
def get_countries():
    countries = dataProvider.get_countries()
    return jsonify(countries), 200

@app.route("/tasks", methods=["GET"])
def get_ui_types():
    return jsonify(ui_types), 200

@app.route("/groups", methods=["GET"])
def get_groups():
    groups = dataProvider.get_groups()
    return jsonify(groups), 200

@app.route("/groups/<group_name>", methods=["GET"])
def execute_group(group_name):
    reset(taskManager, PIXELS)
    color, bitmap = dataProvider.get_group(group_name)
    PIXELS.fill(color)
    ledmodule.light(bitmap)
    return "ok", 200

@app.route("/groups", methods=["POST"])
def create_group():
    group = json.loads(request.data)
    dataProvider.create_group(group["name"], group["color"], group["countries"])
    return jsonify(group), 200

@app.route("/groups/<group_name>", methods=["DELETE"])
def delete_group(group_name):
    dataProvider.delete_group(group_name)
    return "Ok", 200

@app.route("/colors", methods=["GET"])
def get_colors():
    colors = dataProvider.get_colors()
    return jsonify(colors), 200

@app.route("/colors", methods=["POST"])
def create_color():
    color = json.loads(request.data)
    dataProvider.create_color(color["color"])
    return jsonify(color), 200

@app.route("/colors/<color>", methods=["DELETE"])
def delete_color(color):
    dataProvider.delete_color(color)
    return "Ok", 200

@app.route("/shutdown", methods=["GET"])
def shutdown():
    reset(taskManager, PIXELS)
    os.system("shutdown now -h")
    return "ok", 200

def terminate_handler(signum, frame):
    reset(taskManager, PIXELS)
    sys.exit(0)

def import_and_register_endpoints(dir, sub_module_name=""):
    sys.path.append(dir)
    dir_name = dir.split("/")[-1]
    sub_module_name += f".{dir_name}"
    for file_name in os.listdir(dir):
        if file_name == "__pycache__":
            continue
        if os.path.isdir(f"{dir}/{file_name}"):
            import_and_register_endpoints(f"{dir}/{file_name}", sub_module_name)
        else:
            module_name = f"{sub_module_name}.{file_name[:-3]}"
            module = importlib.import_module(module_name, "worldmap_server")
            endpoint = module_name.replace(".", "/")
            ui_types[module_name] = module.get_ui_types()
            app.add_url_rule(
                endpoint,
                endpoint=endpoint,
                view_func=lambda module=module: module.run(taskManager, PIXELS, request.args)
            )

if __name__ == '__main__':
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    ledmodule.activate()
    reset(taskManager, PIXELS)
    import_and_register_endpoints("worldmap_server/tasks")
    taskManager.start_task(BlinkTask(PIXELS, {"color": CONFIG.ready_color, "time": 0.5}))
    app.run(host="0.0.0.0", port=CONFIG.port)