#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, argparse, subprocess
from time import sleep
from pathlib import Path
import vlc

#yoctopuce api
from yoctopuce.yocto_api import *
from yoctopuce.yocto_altitude import *

#import main.player as player
import player

# add ../../Sources to the PYTHONPATH
sys.path.append(os.path.join("..", "..", "Sources"))
DEFAULT_VIDEO_PATH = Path("/home/computemodule/Desktop/UPP_NER_2.mp4")

def tilde_path(pathstr):
    if pathstr[0] == "~":
        return os.path.expanduser(pathstr)
    return pathstr

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
        help="set how much time we should leave in the video before the end", type=int)

def main():
    #user arguments
    parser = argparse.ArgumentParser(description='Enter optional commands for player')
    add_args(parser)

    args = parser.parse_args()

    #subprocess.run(["export", "DISPLAY=:0"])
    os.system("export DISPLAY=:0")

    # video_player = OMXPlayer(args.video_path, args=['--no-osd'])
    video_player = vlc.MediaPlayer(tilde_path(args.video_path))
    video_player.set_fullscreen(True)

    video_player.play()
    sleep(2)
    video_player.pause()
    video_player.set_rate(args.rate)
    print(args.starting_pos)
    video_player.set_time(args.starting_pos)

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
        print('exception caught')
        print(e)
        YAPI.FreeAPI()
        video_player.stop()
        os.execv(sys.executable, ['python3'] + sys.argv)

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()
