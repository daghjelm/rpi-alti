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

def main():
    video_player = OMXPlayer(VIDEO_PATH, args=['--no-osd'])
    #how long we should wait between checking the sensor value
    #how many seconds of video we should leave
    margin = 10
    #get playback rate from arguments
    errmsg = YRefParam()
    #get rate and starting posistion from args
    video_player.set_rate(float(sys.argv[1]))
    video_player.set_position(int(sys.argv[2]))
    play_time = int(sys.argv[3])

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

    alti_player = player.Player(video_player, sensor, 10)

    #init video in omx
    try:
        alti_player.run(10, 1)
    except Exception as e:
        print(e)
        YAPI.FreeAPI()
        player.quit()
        os.execv(sys.executable, ['python3'] + sys.argv)

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()