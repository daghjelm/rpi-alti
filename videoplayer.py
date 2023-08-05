from abc import ABC, abstractmethod
import os
import vlc
from time import sleep

def tilde_path(pathstr):
    if pathstr[0] == "~":
        return os.path.expanduser(pathstr)
    return pathstr

class VideoPlayer(ABC):
    @abstractmethod
    def init_rate_pos(self, rate: float, starting_pos: int):
        pass

    @abstractmethod
    def get_length(self) -> int:
        pass

    @abstractmethod
    def set_rate(self, rate: float):
        pass

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def pause(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def get_time(self) -> int:
        pass

    @abstractmethod
    def set_time(self, time: int):
        pass

class VLCPlayer(VideoPlayer):
    def __init__(self, path: str, init_args = []): # type: ignore
        instance = vlc.Instance(*init_args)
        self.video_player = instance.media_player_new(tilde_path(path))
        self.video_player.set_fullscreen(True)
        self.video_player.play()
        sleep(1)
        self.video_player.pause()

    def init_rate_pos(self, rate: float, starting_pos: int):
        self.video_player.play()
        sleep(0.5)        
        self.video_player.set_rate(rate)
        sleep(0.5)        
        self.video_player.pause()
        sleep(0.5)        
        self.video_player.play()
        sleep(0.5)        
        self.video_player.set_time(starting_pos)
        sleep(0.5)        
        self.video_player.pause()
    
    def get_length(self) -> int:
        return self.video_player.get_length()
    
    def set_rate(self, rate: float):
        self.video_player.set_rate(rate)
    
    def play(self):
        self.video_player.play()

    def pause(self):
        self.video_player.pause()

    def stop(self):
        self.video_player.stop()
    
    def get_time(self) -> int:
        return self.video_player.get_time()
    
    def set_time(self, time: int):
        self.video_player.set_time(time)

