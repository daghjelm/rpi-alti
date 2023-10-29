#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, argparse 
from time import sleep
from pathlib import Path

#yoctopuce api
from yoctopuce.yocto_api import YAPI, YRefParam
from yoctopuce.yocto_altitude import YAltitude

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
    parser.add_argument("-s", "--starting_pos", default=10,
                        help="set the starting position of the video to be played", type=int)
    parser.add_argument("-p", "--play_time", default=10,
                        help="set how long the video is to be played before checking for movement again", type=int)
    parser.add_argument("-m", "--margin", default=10,
                        help="set how much time we should leave in the video before the end", type=int)
    parser.add_argument("-i", "--interval", default=1,
                        help="set how much time we should leave in the video before the end", type=int)
    parser.add_argument("-k", "--keycontrol", default=False, 
                        help="decide if you can control direction with arrow keys", type=bool)
    parser.add_argument("-t", "--stopping", default=False,
                        help="decide if being still should mean full stop", type=bool)
    parser.add_argument("-f", "--fraction", default=False, 
                        help="decide if start time should be a fraction (1/4) of entire vid", type=bool)
    parser.add_argument("-d", "--debug", default=True, 
                        help="display debug logs", type=bool)

def testrun(player, sleep_time):
    #playing video fixed with pos 462155 and end_time 465667
    for i in range(100):
        player.play()
        player.set_time(455000)
        sleep(15)
        print(player.get_time())
        player.pause()
        sleep(1)
        player.set_time(232833)
        player.play()
        print(player.get_time())
        sleep(20)

def main():
    #user arguments
    parser = argparse.ArgumentParser(description='Enter optional commands for player')
    add_args(parser)

    args = parser.parse_args()

    assert args.margin <= args.starting_pos

    # instance = vlc.Instance("--input-fast-seek", "--no-xlib", "--vout=mmal_vout)

    video_player = videoplayer.VLCPlayer(args.video_path)

    args.starting_pos *= 1000
    if args.fraction:
        print(video_player.get_length())
        args.starting_pos = video_player.get_length() // 4
    
    assert args.starting_pos < video_player.get_length()

    video_player.init_rate_pos(args.rate, args.starting_pos)

    # testrun(video_player, 3)
    # return

    #get playback rate from arguments
    errmsg = YRefParam()

    # Setup the API to use local USB devices
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        sys.exit("init error" + str(errmsg.value))

    # retreive any altitude sensor
    sensor = YAltitude.FirstAltitude()
    if sensor is None:
        die('No module connected')
        return

    m = sensor.get_module()
    target = m.get_serialNumber()

    altSensor = YAltitude.FindAltitude(target + '.altitude')

    alti_player = altiplayer.AltiPlayer(
        video_player,
        altSensor,
        args.margin,
        args.play_time,
        args.interval,
        keycontrol=args.keycontrol,
        stopping=args.stopping
    )

    try:
        alti_player.run()
    except Exception as e:
        print('exception caught')
        print(e)
        video_player.stop()

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()
