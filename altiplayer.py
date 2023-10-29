from time import sleep
from yoctopuce.yocto_api import YAPI
from yoctopuce.yocto_altitude import YAltitude
from mediaplayer import MediaPlayer
import threading

class AltiPlayer():
    def __init__(
        self, 
        player: MediaPlayer,
        sensor: YAltitude,
        margin: int,
        play_time: int,
        interval: float,
        stopping: bool = False,
        keycontrol: bool = False,
        debug: bool = True
    ):
        self.player = player
        self.sensor = sensor
        self.margin = margin * 1000 #need margin in ms
        self.play_time = play_time * 1000 #as ms
        self.interval = interval
        self.stopping = stopping
        self.keycontrol = keycontrol
        self.debug = debug

        self.pressing_up = False
        self.pressing_down = False

        self.paused = True 

        self.full_time: int = player.get_length()
        self.half_time: int = self.full_time // 2
    
    # def get_adjusted_duration(self, pos, duration):
    #     return duration + (1 - pos % 1)

    def log(self, *args):
        if self.debug:
            print(*args)

    # play until end_time, then jump to start_time
    def play_and_loop(self, pos: int, end_time: int, start_time: int):
        time_to_end = end_time - pos
        remaining_time = self.play_time - time_to_end
        self.log('playing and looping with pos:', pos, 'end_time:', end_time, 'start_time:', start_time)
        self.log('remaining_time:', remaining_time, 'time_to_end:', time_to_end, 'play_time:', self.play_time)
        sleep1 = YAPI.Sleep(time_to_end)
        self.player.set_time(start_time)
        self.log('set time to', start_time)
        sleep2 = YAPI.Sleep(remaining_time)
        self.log('sleep1:', sleep1, 'sleep2:', sleep2)

    def play_video_fixed(self, pos, up):
        #vlc stops if you play past end of video, so we add a margin
        end_time = self.half_time if up else (self.full_time - self.margin) 
        start_time = 0 if up else self.half_time
        plays_past_end = pos + self.play_time >= end_time

        self.log('playing video fixed with pos: {pos}, end_time: {end_time}, start_time'.format(pos=pos, end_time=end_time))
        self.log('plays_past_end: {plays_past_end}, is_playing(): {is_playing}'.format(plays_past_end=plays_past_end, is_playing=self.player.is_playing()))
        self.log('player time', self.player.get_time(), 'full player time', self.player.get_length())

        if not self.stopping:
            self.player.set_rate(1)
        if plays_past_end:
            self.play_and_loop(pos, end_time, start_time)
        else:
            self.player.play()
            YAPI.Sleep(self.play_time)
        
    def calc_dir_and_play(self, prev, diff):
        pos = self.player.get_time()
        current = self.sensor.get_currentValue()

        going_up = current - prev > diff or self.pressing_up
        going_down = current - prev < -diff or self.pressing_down

        direction = "up" if going_up else "down" if going_down else "still"
        self.log("direction", direction)

        # being passed half way means the video is playing backwards
        # --------------- | ----------------
        #    up    self.half_time    down
        changed_direction = (going_up and pos > self.half_time) or \
                            (going_down and pos < self.half_time)

        if going_up or going_down:
            if changed_direction:
                pos = self.full_time - pos
                self.player.set_time(pos)
            try:
                self.play_video_fixed(pos, going_up)
            except Exception as e:
                self.log(e)
        #sensor is still
        else:
            assert direction == "still"
            if self.stopping:
                if self.player.is_playing():
                    self.player.pause()
            elif not (self.player.get_rate() == 0.25):
                self.player.set_rate(0.25)
            self.log('still and is playing?', self.player.is_playing())
    
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
        diff = 0.6

        if self.keycontrol:
            input_thread = threading.Thread(target=self.listen_for_input)
            input_thread.start()

        # Initial sensor value is first prev
        prev = self.sensor.get_currentValue()

        while self.sensor.isOnline():
            self.calc_dir_and_play(prev, diff)
            prev = self.sensor.get_currentValue()
            sleep(self.interval)