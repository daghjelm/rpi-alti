from abc import ABC, abstractmethod
import os
import vlc

def tilde_path(pathstr):
    if pathstr[0] == "~":
        return os.path.expanduser(pathstr)
    return pathstr

class VideoPlayer(ABC):

    @abstractmethod
    def init_rate_pos(self, rate, starting_pos):
        pass

    @abstractmethod
    def get_length(self) -> int:
        pass

    @abstractmethod
    def set_rate(self, rate):
        pass

    @abstractmethod
    def play(self):
        pass

    @abstractmethod
    def get_time(self) -> int:
        pass

    @abstractmethod
    def set_time(self, time):
        pass

class VLCPlayer(VideoPlayer):
    def __init__(self, path, init_args):
        instance = vlc.Instance(*init_args)
        self.video_player = instance.media_player_new(tilde_path(path))
        self.video_player.set_fullscreen(True)

    def set_init_rate_pos(self, rate, starting_pos):
        self.video_player.set_rate(rate)
        self.video_player.play()
        self.video_player.pause()
        self.video_player.set_time(starting_pos)
    
    def get_length(self):
        return self.video_player.get_length()
    
    def set_rate(self, rate):
        self.video_player.set_rate(rate)
    
    def play(self):
        self.video_player.play()
    
    def get_time(self):
        self.video_player.get_time()
    
    def set_time(self, time):
        self.video_player.set_time(time)

