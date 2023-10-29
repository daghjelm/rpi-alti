from abc import ABC, abstractmethod
import os
import vlc
from time import sleep


class MediaPlayer(ABC):
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
    def get_rate(self) -> float:
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

    @abstractmethod
    def is_playing(self) -> bool:
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def can_pause(self):
        pass

    @abstractmethod
    def pause_idom(self):
        pass

class AudioPlayer():
    def __init__(self, path: str, init_args = []): # type: ignore
        instance = vlc.Instance(*init_args)
        self.audio_player = instance.media_player_new(path)
    
    def play(self):
        self.audio_player.play()
    
    def pause(self):
        self.audio_player.pause()

class VLCPlayer(MediaPlayer):
    def __init__(self, path: str, init_args = []): # type: ignore
        instance = vlc.Instance(*init_args)
        self.video_player = instance.media_player_new(path)
        self.video_player.set_fullscreen(True)
        self.video_player.play()
        sleep(1)
        self.video_player.pause()

    def init_rate_pos(self, rate: float, starting_pos: int):
        self.video_player.set_rate(rate)
        self.video_player.set_time(starting_pos)
        sleep(0.5)        
        self.video_player.play()
        sleep(0.5)        
        self.video_player.pause()
    
    def get_length(self) -> int:
        return self.video_player.get_length()
    
    def set_rate(self, rate: float):
        self.video_player.set_rate(rate)

    def get_rate(self) -> float:
        return self.video_player.get_rate()
    
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
    
    def is_playing(self) -> bool:
        return self.video_player.is_playing()
    
    def get_state(self):
        return self.video_player.get_state()

    def can_pause(self):
        return self.video_player.can_pause()
    
    def pause_idom(self):
        if self.is_playing():
            self.video_player.pause()