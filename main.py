#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, argparse 
from time import sleep
from pathlib import Path

#yoctopuce api
from yoctopuce.yocto_api import *
from yoctopuce.yocto_altitude import *

import altiplayer
import videoplayer 

# sys.path.append(os.path.join("..", "..", "Sources"))
DEFAULT_VIDEO_PATH = Path("/home/computemodule/Desktop/UPP_NER_2.mp4")

def die(msg):
   sys.exit(msg + ' (check USB cable)')

def add_args(parser):
    parser.add_argument("-v", "--video_path", default=DEFAULT_VIDEO_PATH, help='path to the video that is to be played', type=str)
    parser.add_argument("-r", "--rate", default=1,
         help="set playback rate", type=float)
    parser.add_argument("-s", "--starting_pos", default=0,
        help="set the starting position of the video to be played", type=int)
    parser.add_argument("-p", "--play_time", default=10,
        help="set how long the video is to be played before checking for movement again", type=int)
    parser.add_argument("-m", "--margin", default=10,
        help="set how much time we should leave in the video before the end", type=int)
    parser.add_argument("-i", "--interval", default=1,
        help="set how much time we should leave in the video before the end", type=float)

def testrun(player, sleep_time):
    player.play(3)

    sleep(2)

    player.set_time(10000)
    sleep(1)
    print("play 1")
    player.play()
    sleep(sleep_time)

    player.set_time(20000)
    sleep(1)
    print("play 2")
    player.play()
    sleep(sleep_time)

    player.set_time(30000)
    sleep(1)
    print("play 3")
    player.play()
    sleep(sleep_time)

    player.set_time(40000)
    print("play 4")
    player.play()
    sleep(sleep_time)
    player.pause()

def main():
    #user arguments
    parser = argparse.ArgumentParser(description='Enter optional commands for player')
    add_args(parser)

    args = parser.parse_args()

    # instance = vlc.Instance("--input-fast-seek", "--no-xlib", "--vout=mmal_vout)

    video_player = videoplayer.VLCPlayer(args.video_path)
    video_player.init_rate_pos(args.rate, args.starting_pos)

    testrun(video_player)

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

    alti_player = altiplayer.AltiPlayer(
        video_player,
        altSensor,
        args.margin,
        args.play_time,
        args.interval,
    )

    try:
        alti_player.run()
    except Exception as e:
        print('exception caught')
        print(e)
        YAPI.FreeAPI()
        video_player.stop()
        os.execv(sys.executable, ['python3'] + sys.argv)

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()
