import ledmodule

def hex_to_rgb(hexa):
    return tuple(int(hexa[i:i+2], 16)  for i in (0, 2, 4))

def kill_leds():
    bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ledmodule.light(bitmap)

def reset(taskManager, pixels):
    taskManager.terminate_task()
    kill_leds()
    pixels.fill((0, 0, 0))