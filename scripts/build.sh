#!/bin/bash

# Install wiringPi library
apt-get update && sudo apt-get upgrade
apt-get install git git-core
git clone https://github.com/wiringpi/wiringpi
cd wiringPi
./build

# Clone Repo
cd ..
git clone https://github.com/ssvenb/worldmap-server.git
cd worldmap-server

# Build ledmodule from C source code
apt-get install python3-dev
gcc ledmodule.c -shared -o ledmodule.so -lwiringPi -I/usr/include/python3.11

# Create virtual environment and install modules
python3 -m venv .venv
source .venv/bin/activate
pip install adafruit-circuitpython-neopixel
pip install flask

# Initialize database
python3 scripts/init_db.py

# Create systemd service
echo '[Unit]
Description=Worldmap Server
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/weltkarte/worldmap-server/.venv/bin/python3 /home/weltkarte/worldmap-server/src/server.py
WorkingDirectory=/home/weltkarte/worldmap-server/
User=root
Group=root
Restart=always

[Install]
WantedBy=multi-user.target' > /etc/systemd/system/server.service
systemctl daemon-reload
systemctl enable server.service
systemctl start server.service