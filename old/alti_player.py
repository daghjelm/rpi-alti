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
import sys

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
FULL_TIME = 238.5
HALF_TIME = FULL_TIME / 2
VIDEO_PATH = Path("UPP_NER_2.mp4")
player = OMXPlayer(VIDEO_PATH, args=['--no-osd'])

#get playback rate from arguments
rate = float(sys.argv[1])
print('rate', rate)

sleep(1)

player.set_rate(rate)
player.set_position(30)

print(player.rate())

def run_altiplayer(p, sensor):
    pos = 0
    first = sensor.get_currentValue()
    prev = sensor.get_currentValue()
    # prev2 = prev
    last_direction = "UP"
    while sensor.isOnline():

        if p.position() > 0:
            pos = p.position()
        
        print('position in video', pos)

        current = sensor.get_currentValue()
        
        if current < first:
            first = current

        print('sensor value', current)

        #if current - prev > 0.05 and prev - prev2 > 0.05:
        if current - prev > 0.07:
            playable = True
            d = 'UP'
            if last_direction == 'DOWN':
                print('setting new position, going up:')
                print('1', pos)
                try:
                    p.set_position(FULL_TIME - pos)
                except Exception as e:
                    print('error')
                    print(e)
            elif last_direction != 'DOWN' and pos > HALF_TIME - 20:
                playable = False
            
            if playable:
                p.play()
        #elif current - prev < -0.05 and prev - prev2 < -0.05:
        elif current - prev < -0.07 and pos < FULL_TIME - 20:
            d = 'DOWN'
            if last_direction == 'UP':
                print('setting new position, going down:')
                print('2', pos)
                try:
                    p.set_position(FULL_TIME - pos)
                except Exception as e:
                    print('error')
                    print(e)
                
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
except Exception as e:
    print(e)
    YAPI.FreeAPI()
    # player.stop()
    player.quit()
    os.execv(sys.executable, ['python3'] + sys.argv)

YAPI.FreeAPI()