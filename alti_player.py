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

player.set_position(15)

# def run_altiplayer(p, sensor):
#     pos = 0

#     prev = sensor.get_currentValue()
#     # prev2 = prev
#     last_direction = "UP"
#     while sensor.isOnline():

#         if p.position() > 0:
#             pos = p.position()
        
#         print(pos)

#         current = sensor.get_currentValue()
#         print(current)

#         #if current - prev > 0.05 and prev - prev2 > 0.05:
#         if current - prev > 0.1:
#             d = 'UP'
#             if last_direction == 'DOWN':
#                 print('setting new position, going up:')
#                 print('1', pos)
#                 try:
#                     p.set_position(FULL_TIME - pos)
#                 except Exception as e:
#                     print('error')
#                     print(e)
#             p.play()
#         #elif current - prev < -0.05 and prev - prev2 < -0.05:
#         elif current - prev < -0.1:
#             d = 'DOWN'
#             if last_direction == 'UP':
#                 print('setting new position, going down:')
#                 print('2', pos)
#                 try:
#                     p.set_position(FULL_TIME - pos)
#                 except Exception as e:
#                     print('error')
#                     print(e)
                
#             p.play()
#         else:
#             d = 'STILL'
#             p.pause()

#         if d == 'UP':
#             last_direction = 'UP'
#         if d == 'DOWN':
#             last_direction = 'DOWN'

#         # prev2 = prev
#         prev = current
#         YAPI.Sleep(1000)

# try:
#     run_altiplayer(player, altSensor)
# except Exception as e:
#     print(e)
#     YAPI.FreeAPI()
#     # player.stop()
#     player.quit()
#     os.execv(sys.executable, ['python3'] + sys.argv)

pos = 0

prev = sensor.get_currentValue()
# prev2 = prev
last_direction = "UP"
while sensor.isOnline():

    if player.position() > 0:
        pos = player.position()
    
    print(pos)

    current = sensor.get_currentValue()
    print(current)

    #if current - prev > 0.05 and prev - prev2 > 0.05:
    if current - prev > 0.05:
        d = 'UP'
        if last_direction == 'DOWN':
            print('setting new position, going up:')
            print('1', pos)
            try:
                player.set_position(FULL_TIME - pos)
            except Exception as e:
                print('error')
                print(e)
        player.play()
    #elif current - prev < -0.05 and prev - prev2 < -0.05:
    elif current - prev < -0.05:
        d = 'DOWN'
        if last_direction == 'UP':
            print('setting new position, going down:')
            print('2', pos)
            try:
                player.set_position(FULL_TIME - pos)
            except Exception as e:
                print('error')
                print(e)
            
        player.play()
    else:
        d = 'STILL'
        player.pause()

    if d == 'UP':
        last_direction = 'UP'
    if d == 'DOWN':
        last_direction = 'DOWN'

    # prev2 = prev
    prev = current
    YAPI.Sleep(1000)


YAPI.FreeAPI()