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

#all inputs are in whole seconds
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
    parser.add_argument("-i", "--interval", default=1.0,
                        help="how long we should wait between checking sensor values", type=float)
    parser.add_argument("--diff", default=0.5,
                        help="what should be the cutoff in sensor value", type=float)
    parser.add_argument("-b", "--time_to_blank", default=10,
                        help="how long should the video be paused before blanking", type=int)
    parser.add_argument("-a", "--audio_path", default=DEFAULT_AUDIO_PATH, 
                        help="path to audio file", type=str)

    #booleans 
    parser.add_argument("-k", "--keycontrol", action=argparse.BooleanOptionalAction, default=False, 
                        help="decide if you can control direction with arrow keys", type=bool)

    parser.add_argument("-t", "--stopping", action=argparse.BooleanOptionalAction, default=False,
                        help="decide if being still should mean full stop", type=bool)

    parser.add_argument('-d', '--debug', action=argparse.BooleanOptionalAction, default=False, 
                        help='print debug statements', type=bool)

    parser.add_argument('--half_start', action=argparse.BooleanOptionalAction, default=False, 
                        help='start at half time', type=bool)

def init_video_player(path: str, rate: float, starting_pos: int, half_start=False):
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

    if half_start:
        full_time = video_player.get_length()
        video_player.set_time(full_time // 4)
    else:
        video_player.set_time(starting_pos)
    sleep(1)        
    video_player.pause()
    sleep(1)        

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

    #init video and audio vlc players
    video_player = init_video_player(args.video_path, args.rate, args.starting_pos, args.half_start)
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
    
    #alti sensor with values from args
    alti_player = altiplayer.AltiPlayer(
        player=video_player,
        sensor=altSensor,
        margin=args.margin,
        play_time=args.play_time,
        interval=args.interval,
        keycontrol=args.keycontrol,
        stopping=args.stopping,
        debug=args.debug,
        time_to_blank=args.time_to_blank,
        diff=args.diff,
    )

    try:
        audio_player.play()
        alti_player.run()
    except Exception as e:
        print('exception caught')
        print(e)
        video_player.stop()

    YAPI.FreeAPI()

if __name__ == "__main__":
    main()
