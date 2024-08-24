import ledmodule
import sqlite3
import os
import time

home_dir = os.environ.get("HOME")
connection = sqlite3.connect(f"{home_dir}/worldmap-server/db.db")
cursor = connection.cursor()

ledmodule.activate()
# down = True
# i = 0
# while True:
#     cursor.execute(f"SELECT * FROM leds WHERE longitude={i}")
#     bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
#     for country in cursor.fetchall():
#         register = country[0]
#         bit = country[1]
#         bitmap[register] += bit
#     ledmodule.light(bitmap)
#     time.sleep(0.01)
#     if down:
#         i += 1
#     else:
#         i -= 1
#     if i >= 13:
#         down = False
#     if i <= 0:
#         down = True

right = True
i = 0
while True:
    cursor.execute(f"SELECT * FROM leds WHERE latitude={i}")
    bitmap = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    for country in cursor.fetchall():
        register = country[0]
        bit = country[1]
        bitmap[register] += bit
    ledmodule.light(bitmap)
    time.sleep(0.01)
    if right:
        i += 1
    else:
        i -= 1
    if i >= 19:
        right = False
    if i <= 0:
        right = True
    
