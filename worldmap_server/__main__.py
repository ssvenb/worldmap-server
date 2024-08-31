from . import ledmodule
import board
import neopixel
import os
import signal
import sys
from flask import Flask, jsonify
from .db import DataProvider
from .utils import kill_leds, all_leds, reset
from .config import Config
from .abstract_task import TaskManager
from .tasks.blink import ExecutableTask as BlinkTask
from .module_importer import TaskModuleImporter, DataModuleImporter

CONFIG = Config()
PIXELS = neopixel.NeoPixel(board.D18, CONFIG.led_count)
ENDPOINT_IMPORTERS = [TaskModuleImporter, DataModuleImporter]

app = Flask(__name__)
dataProvider = DataProvider()
taskManager = TaskManager(PIXELS)

@app.route("/leds/all", methods=["GET"])
def leds_all():
    all_leds()
    return "ok", 200

@app.route("/leds/kill", methods=["GET"])
def leds_kill():
    kill_leds()
    return "ok", 200

@app.route("/reset", methods=["GET"])
def terminate():
    reset(taskManager, PIXELS)
    return "ok", 200

@app.route("/shutdown", methods=["GET"])
def shutdown():
    reset(taskManager, PIXELS)
    os.system("shutdown now -h")
    return "ok", 200

def terminate_handler(signum, frame):
    reset(taskManager, PIXELS)
    sys.exit(0)

def import_endpoint_modules():
    for importer_class in ENDPOINT_IMPORTERS:
        importer_class(app, taskManager, PIXELS).import_modules()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    ledmodule.activate()
    reset(taskManager, PIXELS)
    import_endpoint_modules()
    taskManager.start_task(BlinkTask(PIXELS), {"color": CONFIG.ready_color, "time": 0.5})
    app.run(host="0.0.0.0", port=CONFIG.port)