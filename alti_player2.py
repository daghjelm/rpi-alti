#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys
import math

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

#Length of the video in seconds 

#init video in omx
VIDEO_PATH = Path("UPP_NER_2.mp4")
player = OMXPlayer(VIDEO_PATH, args=['--no-osd'])

FULL_TIME = 238
HALF_TIME = FULL_TIME / 2

#how long we should wait between checking the sensor value
interval = 1

#how many seconds of video we should leave
margin = 10

#get playback rate from arguments
rate = float(sys.argv[1])

starting_pos = int(sys.argv[2])
play_time = int(sys.argv[3])

print('rate', rate)
print('starting_pos', starting_pos)
print('play_time', play_time)

sleep(1)

player.set_rate(rate)
player.set_position(starting_pos)
sleep(1)
player.pause()
print('duration', player.duration())

def play_video(p, sensor, pos, d, r):
    if d == 'UP':
        t = HALF_TIME
    else:
        t = FULL_TIME
    #we shouldnt play longer the video - the margin
    if(pos < t - margin - interval / 1000):
        p.play()
        sleep(play_time)
        p.pause()
    elif t - margin - pos > 0:
        p.play()
        sleep(int(t - margin - pos))
        p.pause()

def run_altiplayer(p, sensor, r, interval):
    pos = p.position()
    #get first value()
    prev = sensor.get_currentValue()
    print('prev', prev)

    sleep(interval)

    while sensor.isOnline():
        pos = p.position()
        current = sensor.get_currentValue()
        #sensor is moving up
        if current - prev > 0.15:
            if pos > HALF_TIME:
                print('pos b4 going up', pos)
                pos = FULL_TIME - pos
                print('pos going up', pos)
                p.set_position((pos + 2))
            try:
                print('trying to go up')
                play_video(p, sensor, pos, 'UP', r)
                print('after')
            except Exception as e:
                print('error')
                print(e)
        #sensor if moving down
        elif current - prev < -0.15:
            if pos < HALF_TIME:
                print('pos b4 going down', pos)
                pos = FULL_TIME - pos
                print('pos going down', pos)
                p.set_position(pos + 0.5)
            try:
                print('trying to go down')
                play_video(p, sensor, pos, 'DOWN', r)
                print('after')
            except Exception as e:
                print('error')
                print(e)
        #sensor is still
        else:
            print('still')

        prev = sensor.get_currentValue()
        sleep(interval)

try:
    run_altiplayer(player, altSensor, rate, interval)
except Exception as e:
    print(e)
    YAPI.FreeAPI()
    player.quit()
    os.execv(sys.executable, ['python3'] + sys.argv)

YAPI.FreeAPI()