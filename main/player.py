from time import sleep
from yoctopuce.yocto_api import YAPI
from yoctopuce.yocto_altitude import YAltitude
from vlc import MediaPlayer

class Player():
    def __init__(
        self, 
        player: MediaPlayer,
        sensor: YAltitude,
        margin: float,
        play_time: int,
        interval: float
    ):
        self.player = player
        self.sensor = sensor
        self.margin = margin * 1000 #need margin in ms
        self.play_time = play_time * 1000 #as ms

        self.full_time = player.get_length()
        self.half_time = self.full_time / 2
    
    # def get_adjusted_duration(self, pos, duration):
    #     return duration + (1 - pos % 1)

    def play_video_fixed(self, pos, up, duration):
        end_time = self.half_time if up else self.full_time
        #we shouldn't play longer than the video - the margin
        if pos < end_time - self.margin - duration:
            self.player.set_rate(1)
            self.player.play()
            print("duration", duration)
            YAPI.Sleep(duration)
            self.player.set_rate(0.25)
            # self.player.pause()
        #this is if sleeping the duration will put us past end - margin
        elif end_time - self.margin - pos > 0:
            self.player.set_rate(1)
            self.player.play()
            print("end_time - self.margin - pos", end_time - self.margin - pos)
            YAPI.Sleep(end_time - self.margin - pos)
            self.player.set_rate(0.25)
        
    def calc_dir_and_play(self, prev, diff):
        pos = self.player.get_time()
        current = self.sensor.get_currentValue()

        going_up = current - prev > diff
        going_down = current - prev < -diff

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
                self.play_video_fixed(pos, going_up, self.play_time)
            except Exception as e:
                print(e)
        #sensor is still
        else:
            print('still')


    def run(self):
        diff = 0.15

        # Initial sensor value is first prev
        prev = self.sensor.get_currentValue()

        while self.sensor.isOnline():
            self.calc_dir_and_play(prev, diff)
            prev = self.sensor.get_currentValue()
            sleep(self.interval)