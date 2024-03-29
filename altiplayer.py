from time import sleep, time_ns, time
from yoctopuce.yocto_api import YAPI
from yoctopuce.yocto_altitude import YAltitude
import threading
import os

class AltiPlayer():
    EXTRA_TIME_FOR_BLACK_SCREEN = 1000  # milliseconds
    LOOP_MARGIN = 150 # milliseconds

    def __init__(
        self, 
        player,
        sensor: YAltitude,
        margin: int,
        play_time: int,
        interval: float,

        diff: float = 0.2,
        stopping: bool = False,
        keycontrol: bool = False,
        debug: bool = True,
        time_to_blank: int = 20,
    ):
        self.player = player
        self.sensor = sensor
        self.margin = margin * 1000 #need margin in ms
        self.play_time = play_time * 1000 #as ms
        self.interval = interval
        self.diff = diff

        self.stopping = stopping
        self.keycontrol = keycontrol
        self.debug = debug
        self.time_to_blank = time_to_blank

        self.pressing_up = False
        self.pressing_down = False

        self.blanked = False
        self.pos_before_blank = 0
        self.still_start = time()

        self.last_moving = True
        self.curr_moving = True

        # video has margin s of black screen at the end
        # this is to avoid going passed the end of the video and quitting vlc
        # the black part is also used for blanking
        self.full_time: int = player.get_length() - (margin * 1000)
        self.half_time: int = self.full_time // 2
    
    def log(self, *args):
        if self.debug:
            print(*args)

    # play until end_time, then jump to start_time
    def play_and_loop(self, pos: int, end_time: int, start_time: int):
        time_to_end = end_time - pos - AltiPlayer.LOOP_MARGIN
        remaining_time = self.play_time - time_to_end
        self.log('playing and looping with pos:', pos, 'end_time:', end_time, 'start_time:', start_time)
        self.log('remaining_time:', remaining_time, 'time_to_end:', time_to_end, 'play_time:', self.play_time)
        YAPI.Sleep(time_to_end)
        self.player.pause()
        self.player.set_time(start_time)
        self.player.play()
        YAPI.Sleep(remaining_time)

    def play_video_fixed(self, pos, up):
        end_time = self.half_time if up else self.full_time
        start_time = 0 if up else self.half_time
        plays_past_end = pos + self.play_time >= end_time

        self.log('playing video fixed with pos: {pos}, end_time: {end_time}, start_time'.format(pos=pos, end_time=end_time))
        self.log('plays_past_end: {plays_past_end}, is_playing(): {is_playing}'.format(plays_past_end=plays_past_end, is_playing=self.player.is_playing()))
        self.log('player time', self.player.get_time(), 'full player time', self.player.get_length())

        if not self.stopping:
            self.player.set_rate(1)
        if plays_past_end:
            if not self.player.is_playing():
                self.player.play()
            self.play_and_loop(pos, end_time, start_time)
        else:
            self.player.play()
            YAPI.Sleep(self.play_time)
    
    #current = most recent value
    def is_going_up(self, current, prev):
        return current - prev > self.diff or self.pressing_up

    #current = most recent value
    def is_going_down(self, current, prev):
        return current - prev < -self.diff or self.pressing_down
    
    def calc_dir_and_play(self, prev, prev2):
        pos = self.get_correct_pos()
        current = self.sensor.get_currentValue()
        self.log("pos", "prev", "prev2", "current", pos, prev, prev2, current)

        going_up = self.is_going_up(prev2, prev) and self.is_going_up(current, prev2)
        going_down = self.is_going_down(prev2, prev) and self.is_going_down(current, prev2)

        direction = "up" if going_up else "down" if going_down else "still"
        self.log("direction", direction)

        # being passed half way means the video is playing backwards
        # --------------- | ----------------
        #    up    self.half_time    down
        changed_direction = (going_up and pos > self.half_time) or \
                            (going_down and pos < self.half_time)

        if going_up or going_down:
            self.update_motion_state(True)
            if self.blanked:
                self.player.set_time(pos)
            if changed_direction:
                pos = self.full_time - pos
                self.player.set_time(pos)
            self.blanked = False
            try:
                self.play_video_fixed(pos, going_up)
            except Exception as e:
                self.log(e)
        else: # sensor is still
            self.handle_still()

    # if the screen is blanked, pos should be the last pos before blanking
    def get_correct_pos(self):
        if self.blanked:
            return self.pos_before_blank
        return self.player.get_time()
    
    def update_motion_state(self, is_moving):
        self.last_moving = self.curr_moving
        self.curr_moving = is_moving 
    
    #being still means handling extra logic for blanking and stopping
    def handle_still(self):
        if self.blanked:
            return

        self.update_motion_state(False)

        if self.last_moving != self.curr_moving:
            self.still_start = time()
        time_still = time() - self.still_start

        # if we've been still for more than time_to_blank, blank screen
        if time_still >= self.time_to_blank:
            self.blank()
        if self.stopping:
            if self.player.is_playing():
                self.player.pause()
        elif not (self.player.get_rate() == 0.25) and not self.blanked:
            self.player.set_rate(0.25)
        self.log('still and is playing?', self.player.is_playing())
    
    def blank(self):
        #last 10 s of the video is black screen so add 1 s to full time 
        #to end up in the black screen
        self.pos_before_blank = self.player.get_time()
        self.player.set_time(self.full_time + AltiPlayer.EXTRA_TIME_FOR_BLACK_SCREEN)
        self.blanked = True
        if self.player.is_playing():
            self.player.pause()
    
    def on_input(self, input):
        if input == "u":
            self.pressing_down = False
            self.pressing_up = not self.pressing_up
            self.log("pressing up: ", self.pressing_up)
        if input == "d": 
            self.presssing_up = False
            self.pressing_down = not self.pressing_down
            self.log("pressing down: ", self.pressing_down)
        if input == "p":
            self.player.pause()
            self.log("pausing")
        if input == "sh":
            self.player.set_time(self.half_time)
            self.log("set half time")
        if input == "sb":
            self.player.set_time(0)
            self.log("set beggining")
        if input == "t":
            self.log("time:", self.player.get_time())
        if input == "s":
            self.player.stop()
            self.log("stopping")
        if input == "q":
            self.player.stop()
            self.log("quiting")
            exit() 

    def listen_for_input(self):
        while True:
            user_input = input()
            self.on_input(user_input)
            self.log(f"You entered: {user_input}")

    def run(self):
        if self.keycontrol:
            input_thread = threading.Thread(target=self.listen_for_input)
            input_thread.start()

        # Initial sensor value is first prev
        prev = self.sensor.get_currentValue()
        prev2 = prev
        interval = int(self.interval * 1000)

        while self.sensor.isOnline():
            # we give two values so that the player triggers
            # less often due to random variance in the altitude sensor
            self.calc_dir_and_play(prev, prev2)
            prev = self.sensor.get_currentValue()
            YAPI.Sleep(interval // 2)
            prev2 = self.sensor.get_currentValue()
            YAPI.Sleep(interval // 2)