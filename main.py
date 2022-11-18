#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys
import math
import sys
import argparse
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
    parser = argparse.ArgumentParser(description='Enter optional commands for player')
    parser.add_argument("-r", "--rate", default=1,
         help="set playback rate", type=float)
    parser.add_argument("-s", "--starting_pos", default=0,
        help="set the starting position of the video to be played", type=int)
    parser.add_argument("-p", "--play_time", default=10,
        help="set how long the video is to be played before checking for movement again", type=int)
    parser.add_argument("-m", "--margin", default=10,
        help="set how much time we should leave in the video before the end", type=int)
    parser.add_argument("-i", "--interval", default=1,
        help="set how much time we should leave in the video before the end", type=int)

    args = parser.parse_args()

    video_player = OMXPlayer(VIDEO_PATH, args=['--no-osd'])

    #get playback rate from arguments
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

    alti_player = player.Player(video_player, altSensor, args.margin)

    #init video in omx
    try:
        alti_player.run(args.play_time, args.interval)
    except Exception as e:
        print(e)
        YAPI.FreeAPI()
        player.quit()
        os.execv(sys.executable, ['python3'] + sys.argv)

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()