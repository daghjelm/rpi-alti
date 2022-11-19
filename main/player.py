from time import sleep
from yoctopuce.yocto_api import YAPI

class Player():
    def __init__(
        self, 
        player,
        sensor,
        margin,
    ):
        self.player = player
        self.sensor = sensor
        self.margin = margin * 1000 #need margin in ms

        self.full_time = player.get_length()
        self.half_time = self.full_time / 2
    
    # def get_adjusted_duration(self, pos, duration):
    #     return duration + (1 - pos % 1)

    def play_video(self, pos, up, duration):
        end_time = self.half_time if up else self.full_time
        #we shouldn't play longer than the video - the margin
        if(pos < end_time - self.margin - duration / 1000):
            self.player.play()
            YAPI.Sleep(duration)
            self.player.pause()
        #this is if sleeping the duration will put us past end - margin
        elif end_time - self.margin - pos > 0:
            self.player.play()
            sleep(end_time - self.margin - pos)
            self.player.pause()

    def run(self, play_time, interval):
        sensor = self.sensor
        player = self.player
        play_time = play_time * 1000
        pos = player.get_time()
        diff = 0.15

        #get first value
        prev = sensor.get_currentValue()

        player.play()
        sleep(0.5)
        player.pause()

        while sensor.isOnline():
            pos = player.get_time()
            current = sensor.get_currentValue()
            #sensor is moving up
            if current - prev > diff:
                print('up')
                if pos > self.full_time: #changed direction
                    pos = self.full_time - pos
                    player.set_time(pos)
                try:
                    # print('pos:', pos)
                    # adjusted = self.get_adjusted_duration(pos, play_time)
                    # print('adjusted:', adjusted)
                    # print('adjusted + pos:', adjusted + pos)
                    # adjusted = self.get_adjusted_duration(pos, play_time)
                    self.play_video(pos, True, play_time)
                except Exception as e:
                    print(e)
            #sensor if moving down
            elif current - prev < (- diff):
                print('down')
                if pos < self.half_time: #means we changed direction
                    #calculate new position
                    pos = self.full_time - pos
                    player.set_time(pos)
                try:
                    # print('pos:', pos)
                    # adjusted = self.get_adjusted_duration(pos, play_time)
                    # print('adjusted:', adjusted)
                    # print('adjusted + pos:', adjusted + pos)
                    self.play_video(pos, False, play_time)
                except Exception as e:
                    print(e)
            #sensor is still
            else:
                print('still')

            prev = sensor.get_currentValue()
            sleep(interval)
