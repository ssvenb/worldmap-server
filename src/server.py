import ledmodule
import board
import neopixel
import tasks
import os
from flask import Flask, request

count = 82
port = 8000
pixels = neopixel.NeoPixel(board.D18, count)
app = Flask(__name__)
taskManager = tasks.TaskManager(pixels)
ledmodule.activate()


def hex_to_rgb(hexa):
    return tuple(int(hexa[i:i+2], 16)  for i in (0, 2, 4))

def kill_leds():
    bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ledmodule.light(bitmap)

def reset():
    taskManager.terminate_task()
    kill_leds()
    pixels.fill((0, 0, 0))

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
    reset()
    rgb_color = hex_to_rgb(hex_color)
    pixels.fill(rgb_color)
    return "ok", 200

@app.route("/special/multicolor_transition", methods=["GET"])
def start_multicolor_transition():
    reset()
    task = tasks.MulticolorTransitionTask(pixels)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/special/flash/<color>", methods=["GET"])
def start_neopixel_flash(color):
    reset()
    axis = request.args.get("axis")
    width = int(request.args.get("width"))
    color = hex_to_rgb(color)
    task = tasks.NeopixelFlashTask(pixels, color, width, axis)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/special/flash/leds", methods=["GET"])
def start_led_flash():
    reset()
    axis = request.args.get("axis")
    width = int(request.args.get("width"))
    task = tasks.LedFlashTask(pixels, width, axis)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/special/flash/all/<color>", methods=["GET"])
def start_all_flash(color):
    reset()
    axis = request.args.get("axis")
    width = int(request.args.get("width"))
    color = hex_to_rgb(color)
    task = tasks.AllFlashTask(pixels, color, width, axis)
    taskManager.start_task(task)
    return "ok", 200

@app.route("/special/terminate", methods=["GET"])
def terminate():
    reset()
    pixels.fill((0, 0, 0))
    ledmodule.light([0, 0, 0, 0, 0, 0, 0, 0, 0])
    return "ok", 200

@app.route("/shutdown", methods=["GET"])
def shutdown():
    reset()
    os.system("shutdown now -h")
    return "ok", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)