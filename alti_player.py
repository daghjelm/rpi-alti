#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys

# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("..", "..", "Sources"))

from yoctopuce.yocto_api import *
from yoctopuce.yocto_altitude import *
from omxplayer.player import OMXPlayer
from pathlib import Path
from time import sleep

def die(msg):
    sys.exit(msg + ' (check USB cable)')

errmsg = YRefParam()

# Setup the API to use local USB devices
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

# retreive any altitude sensor
sensor = YAltitude.FirstAltitude()
if sensor is None:
    die('No module connected')
m = sensor.get_module()
target = m.get_serialNumber()

altSensor = YAltitude.FindAltitude(target + '.altitude')

#init video in omx
HALF_TIME = 119.25
FULL_TIME = 238.5
VIDEO_PATH = Path("UPP_NER_2.mp4")
player = OMXPlayer(VIDEO_PATH, args=['--no-osd'])

sleep(1)

player.set_position(20)



def run_altiplayer(p, sensor):

    prev = sensor.get_currentValue()
    # prev2 = prev
    last_direction = "UP"
    while sensor.isOnline():
        current = sensor.get_currentValue()

        #if current - prev > 0.05 and prev - prev2 > 0.05:
        if current - prev > 0.03:
            d = 'UP'
            if last_direction == 'DOWN':
                p.set_position(FULL_TIME - p.position())
            p.play()
        #elif current - prev < -0.05 and prev - prev2 < -0.05:
        elif current - prev < -0.03:
            d = 'DOWN'
            if last_direction == 'UP':
                p.set_position(FULL_TIME - p.position())
            p.play()
        else:
            d = 'STILL'
            p.pause()

        if d == 'UP':
            last_direction = 'UP'
        if d == 'DOWN':
            last_direction = 'DOWN'

        # prev2 = prev
        prev = current
        YAPI.Sleep(1000)

try:
    run_altiplayer(player, altSensor)
except:
    YAPI.FreeAPI()
    os.execv(sys.executable, ['python3'] + sys.argv)


YAPI.FreeAPI()