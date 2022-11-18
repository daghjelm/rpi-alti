#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys
import math
import sys
from time import sleep
from pathlib import Path

#yoctopuce api
from yoctopuce.yocto_api import *
from yoctopuce.yocto_altitude import *
#omx player wrapper
from omxplayer.player import OMXPlayer

import player

# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("..", "..", "Sources"))
VIDEO_PATH = Path("../../Videos/UPP_NER_2.mp4")


def die(msg):
   sys.exit(msg + ' (check USB cable)')

def set_start_rate_and_pos(p, rate, pos, default_rate, default_pos):
    p.set_rate(rate) if rate else p.set_rate(default_rate)
    p.set_position(pos) if pos else p.set_position(default_pos)

def main():
    video_player = OMXPlayer(VIDEO_PATH, args=['--no-osd'])

    #how long we should wait between checking the sensor value
    interval = 1

    #how long to play each iteration
    play_time = int(sys.argv[3])
    if (not play_time):
        play_time = 10

    #how many seconds of video we should leave
    margin = 10
    #get playback rate from arguments
    errmsg = YRefParam()

    #set rate and position from arguments
    set_start_rate_and_pos(video_player, float(sys.argv[1]), int(sys.argv[2]), 1, 0)

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

    alti_player = player.Player(video_player, altSensor, margin)

    #init video in omx
    try:
        alti_player.run(play_time, interval)
    except Exception as e:
        print(e)
        YAPI.FreeAPI()
        player.quit()
        os.execv(sys.executable, ['python3'] + sys.argv)

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()