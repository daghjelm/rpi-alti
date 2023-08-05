from time import sleep
from yoctopuce.yocto_api import YAPI
from yoctopuce.yocto_altitude import YAltitude
from videoplayer import VideoPlayer
from pynput import keyboard

class AltiPlayer():
    def __init__(
        self, 
        player: VideoPlayer,
        sensor: YAltitude,
        margin: float,
        play_time: int,
        interval: float,
        stopping: bool = False,
        keycontrol: bool = False
    ):
        self.player = player
        self.sensor = sensor
        self.margin = margin * 1000 #need margin in ms
        self.play_time = play_time * 1000 #as ms
        self.interval = interval
        self.stopping = stopping
        self.keycontrol = keycontrol
        self.pressing_up = False
        self.pressing_down = False

        self.full_time: int = player.get_length()
        self.half_time: int = self.full_time // 2
    
    # def get_adjusted_duration(self, pos, duration):
    #     return duration + (1 - pos % 1)


    # play until end_time, then jump to start_time
    def play_and_loop(self, pos: int, end_time: int, start_time: int):
        time_to_end = end_time - pos
        remaining_time = self.play_time - time_to_end
        self.player.play()
        YAPI.Sleep(time_to_end)
        self.player.set_time(start_time)
        self.player.play()
        YAPI.Sleep(remaining_time)

    def play_video_fixed(self, pos, up):
        end_time = self.half_time if up else self.full_time
        start_time = 0 if up else self.half_time
        plays_past_end = pos + self.play_time > end_time

        #we shouldn't play longer than the video - the margin
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
        print("direction", direction)

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
                print(e)
        #sensor is still
        else:
            assert direction == "still"
            self.player.pause if self.stopping else self.player.set_rate(0.25)
    
    def on_press(self, key):
        print("key", key)
        if key == keyboard.Key.up:
            self.pressing_down = False
            self.pressing_up = not self.pressing_up
            print("pressing up: ", self.pressing_up)
        if key == keyboard.Key.down:
            self.presssing_up = False
            self.pressing_down = not self.pressing_down
            print("pressing down: ", self.pressing_down)

    def run(self):
        diff = 0.6

        if self.keycontrol:
            listener = keyboard.Listener(on_press=self.on_press)
            listener.start()

        # Initial sensor value is first prev
        prev = self.sensor.get_currentValue()

        while self.sensor.isOnline():
            self.calc_dir_and_play(prev, diff)
            prev = self.sensor.get_currentValue()
            sleep(self.interval)