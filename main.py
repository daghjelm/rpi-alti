#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, argparse 
import vlc
from time import sleep
from pathlib import Path

#yoctopuce api
from yoctopuce.yocto_api import YAPI, YRefParam
from yoctopuce.yocto_altitude import YAltitude

import altiplayer
import vlc

# sys.path.append(os.path.join("..", "..", "Sources"))
DEFAULT_VIDEO_PATH = Path("/home/computemodule/Desktop/UPP_NER_2.mp4")
DEFAULT_AUDIO_PATH = Path("/home/pi/Desktop/DAG.mp3")

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
    parser.add_argument("-t", "--stopping", default=True,
                        help="decide if being still should mean full stop", type=bool)
    parser.add_argument("-f", "--fraction", default=False, 
                        help="decide if start time should be a fraction (1/4) of entire vid", type=bool)
    parser.add_argument("-d", "--debug", default=True, 
                        help="display debug logs", type=bool)
    parser.add_argument("-a", "--audio_path", default=DEFAULT_AUDIO_PATH, 
                        help="path to audio file", type=str)

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
    

def init_video_player(path: str, rate: float, starting_pos: int):
    instance = vlc.Instance()
    if instance is None:
        raise Exception('instance is None')
    video_player = instance.media_player_new(path)
    video_player.set_fullscreen(True)
    video_player.play()
    sleep(1)
    video_player.pause()

    starting_pos *= 1000
    
    assert starting_pos < video_player.get_length()

    video_player.play()
    sleep(0.5)        
    if rate != 1:
        video_player.set_rate(rate)
        sleep(0.5)        
    video_player.set_time(starting_pos)
    sleep(0.5)        
    video_player.pause()

    return video_player

def init_audio_player(path: str):
    instance = vlc.Instance()
    if instance is None:
        raise Exception('instance is None')
    media_list = instance.media_list_new()
    media_list.add_media(path)

    audio_player = instance.media_list_player_new()
    audio_player.set_media_list(media_list)
    audio_player.set_playback_mode(vlc.PlaybackMode(1))

    return audio_player

def main():
    #user arguments
    parser = argparse.ArgumentParser(description='Enter optional commands for player')
    add_args(parser)

    args = parser.parse_args()

    assert args.margin <= args.starting_pos

    #init video and audio vlc players
    video_player = init_video_player(args.video_path, args.rate, args.starting_pos)
    audio_player = init_audio_player(args.audio_path)

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
        audio_player.play()
    except Exception as e:
        print('exception caught')
        print(e)
        video_player.stop()

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()
