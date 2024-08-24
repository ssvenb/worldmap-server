import ledmodule
import board
import neopixel
import tasks
import flash_tasks
import os
import signal
import sys
import sqlite3
from utils import hex_to_rgb, kill_leds, reset
from flask import Flask, request, jsonify

COUNT = 82
PORT = 80
PIXELS = neopixel.NeoPixel(board.D18, COUNT)

app = Flask(__name__)
taskManager = tasks.TaskManager(PIXELS)
ledmodule.activate()
reset(taskManager, PIXELS)
taskManager.start_task(tasks.BlinkTask(PIXELS, (0, 255, 0), 0.5))
os.environ["DB_PATH"] = "/home/weltkarte/worldmap-server/db.db"

@app.route("/leds/all", methods=["GET"])
def leds_all():
    max = 65535
    bitmap = [max, max, max, max, max, max, max, max, max]
    ledmodule.light(bitmap)
    return "ok", 200

@app.route("/leds/kill", methods=["GET"])
def leds_kill():
    kill_leds()
    return "ok", 200

@app.route("/neopixel/<hex_color>", methods=["GET"])
def light_neopixel(hex_color):
    reset(taskManager, PIXELS)
    rgb_color = hex_to_rgb(hex_color)
    PIXELS.fill(rgb_color)
    return "ok", 200

@app.route("/task/multicolor_transition", methods=["GET"])
def start_multicolor_transition():
    reset(taskManager, PIXELS)
    time = request.args.get("time")
    task = tasks.MulticolorTransitionTask(PIXELS, time)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/task/flash/<color>", methods=["GET"])
def start_neopixel_flash(color):
    reset(taskManager, PIXELS)
    axis = request.args.get("axis")
    width = request.args.get("width")
    time = request.args.get("time")
    color = hex_to_rgb(color)
    task = flash_tasks.NeopixelFlashTask(PIXELS, color, width, axis, time)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/task/flash/leds", methods=["GET"])
def start_led_flash():
    reset(taskManager, PIXELS)
    axis = request.args.get("axis")
    width = request.args.get("width")
    time = request.args.get("time")
    task = flash_tasks.LedFlashTask(PIXELS, width, axis, time)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/task/flash/all/<color>", methods=["GET"])
def start_all_flash(color):
    reset(taskManager, PIXELS)
    axis = request.args.get("axis")
    width = request.args.get("width")
    time = request.args.get("time")
    color = hex_to_rgb(color)
    task = flash_tasks.AllFlashTask(PIXELS, color, width, axis, time)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/task/blink/<color>", methods=["GET"])
def blink(color):
    reset(taskManager, PIXELS)
    sleep_time = request.args.get("time")
    color = hex_to_rgb(color)
    task = tasks.BlinkTask(PIXELS, color, sleep_time)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/task/terminate", methods=["GET"])
def terminate():
    reset(taskManager, PIXELS)
    PIXELS.fill((0, 0, 0))
    ledmodule.light([0, 0, 0, 0, 0, 0, 0, 0, 0])
    return "ok", 200

@app.route("/countries", methods=["GET"])
def get_countries():
    db_connection = sqlite3.connect(os.environ.get("DB_PATH"))
    cursor = db_connection.cursor()
    cursor.execute("SELECT country FROM leds")
    countries = [country[0] for country in cursor.fetchall()]
    return jsonify(countries), 200

@app.route("/groups", methods=["GET"])
def get_groups():
    db_connection = sqlite3.connect(os.environ.get("DB_PATH"))
    cursor = db_connection.cursor()
    cursor.execute("SELECT name FROM groups")
    groups = [name[0] for name in cursor.fetchall()]
    return jsonify(groups), 200


@app.route("/shutdown", methods=["GET"])
def shutdown():
    reset(taskManager, PIXELS)
    os.system("shutdown now -h")
    return "ok", 200

def terminate_handler(signum, frame):
    reset(taskManager, PIXELS)
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    app.run(host="0.0.0.0", port=PORT)