import pygame
import typing
import numpy
import cv2
from ffpyplayer.player import MediaPlayer

from .stacks import HStack
from .factories import Slider, Button, Image
from .element import Element
from ..manager import Manager
from ..state import UIState
from ..enums import ElementAlign, StackAnchor
from .. import common
from .. import settings as settings_
from ..import events

# VIDEO PLAYER


class SoundPlayer(HStack):
    """Element with control over a sound"""

    def __init__(self,
                 sound: pygame.mixer.Sound,
                 filename: str,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.SoundPlayerSettings|None = None
                 ):
        if settings is None:
            settings = settings_.SoundPlayerSettings()
        self.__done = False
        super().__init__(relative_rect, element_id, style_id, parent, manager)
        self.add_element_types("player", "soundplayer")
        self.settings = settings
        if self.settings.sliders_settings is None:
            self.settings.sliders_settings = settings_.SliderSettings()
        self.media_player = MediaPlayer(filename, ff_opts={"paused": True})
        self.filename = filename
        self.playing = self.paused = self.muted = False
        self.media_player.set_volume(settings.start_volume)
        self.pg_sound = sound
        self.duration = self.pg_sound.get_length()
        self.volume_before_mute = self.media_player.get_volume()
        self.play_start_time = self.start_position = self.pause_position = 0

        style = self.style
        self.play_button = Button(
            self.settings.play_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_play_button",
            common.style_id_or_copy(self, self.settings.buttons_style_id),
            False, self, self.manager
        ).set_attr("builtin", True)
        self.track_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            common.style_id_or_copy(self, self.settings.sliders_style_id),
            self, self.manager,
            self.settings.sliders_settings
        ).set_attr("builtin", True)
        self.volume_button = Button(
            self.settings.volume_up_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_volume_button",
            common.style_id_or_copy(self, self.settings.buttons_style_id),
            False, self, self.manager
        ).set_attr("builtin", True)
        self.volume_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            common.style_id_or_copy(self, self.settings.sliders_style_id),
            self, self.manager,
            self.settings.sliders_settings
        ).set_attr("builtin", True)
        self.__done = True

        self.play_button.add_element_types(
            "soundplayer_button", "soundplayer_play_button")
        self.volume_button.add_element_types(
            "soundplayer_button", "soundplayer_volume_button")
        self.track_slider.add_element_types(
            "soundplayer_slider", "soundplayer_track_slider")
        self.volume_slider.add_element_types(
            "soundplayer_slider", "soundplayer_volume_slider")
        self.play_button.status.add_listener(
            "on_stop_press", self._on_play_click)
        self.volume_button.status.add_listener(
            "on_stop_press", self._on_volume_click)
        self.track_slider.status.add_listener("on_move", self._on_track_move)
        self.volume_slider.status.add_listener("on_move", self._on_volume_move)

        self.status.register_callbacks(
            "on_toggle", "on_mute", "on_volume_move", "on_track_move")

        self.build()
        self.stop()
        self.volume_slider.set_value(settings.start_volume)

    def play(self):
        """Manually start playing the sound"""
        self.playing = True
        self.play_start_time = pygame.time.get_ticks()/1000
        self.media_player.set_pause(False)
        self.media_player.seek(self.start_position,
                               seek_by_bytes=False, relative=False)
        return self

    def stop(self, start_position: float = 0) -> typing.Self:
        """Manually stop playing the sound. start_position will determine the position in time where the sound will seek when it starts playing again"""
        self.media_player.set_pause(True)
        self.playing = self.paused = False
        self.track_slider.set_value(start_position/self.duration)
        self.start_position = self.pause_position = start_position
        return self

    def pause(self) -> typing.Self:
        """Manually pause the sound"""
        self.media_player.set_pause(True)
        self.playing = False
        self.paused = True
        self.pause_position = (pygame.time.get_ticks(
        )/1000-self.play_start_time)+self.pause_position

    def resume(self) -> typing.Self:
        """Manually resume the sound"""
        self.media_player.set_pause(False)
        self.playing = True
        self.paused = False
        self.play_start_time = pygame.time.get_ticks()/1000
        return self

    def set_volume(self, volume: float) -> typing.Self:
        """Manually set the volume of the sound"""
        self.media_player.set_volume(volume)
        self.volume_slider.set_value(volume)
        return self

    def mute(self) -> typing.Self:
        """Manually mute the sound"""
        self.volume_before_mute = self.get_volume()
        self.media_player.set_volume(0)
        self.volume_slider.set_value(0)
        self.muted = True
        return self

    def unmute(self) -> typing.Self:
        """Manually unmute the sound"""
        self.media_player.set_volume(self.volume_before_mute)
        self.volume_slider.set_value(self.volume_before_mute)
        self.muted = False
        return self

    def seek(self, time_seconds: float) -> typing.Self:
        """Manually seek to a position in time"""
        was_paused = not self.playing or self.paused
        self.stop(time_seconds)
        self.play()
        if was_paused:
            self.pause()
        return self

    def seek_percent(self, percent: float) -> typing.Self:
        """Manually seek to a position in time, expressed in percentage"""
        self.seek(self.duration*(percent/100))
        return self

    def get_volume(self) -> float:
        """Return the volume of the sound"""
        return self.volume_slider.get_value()

    def get_time_passed(self) -> float:
        """Return how much time has passed since the sound started playing"""
        if self.playing:
            return ((pygame.time.get_ticks()/1000-self.play_start_time)+self.pause_position)
        return self.pause_position/self.duration

    def get_time_remaining(self) -> float:
        """Return how much time is left until the sound stops"""
        return self.duration-self.get_time_passed()

    def _on_play_click(self, btn):
        if not self.playing and not self.paused:
            self.play()
        elif not self.playing and self.paused:
            self.resume()
        else:
            self.pause()
        events._post_sound_player_event(events.SOUNDPLAYER_TOGGLE, self)
        self.status.invoke_callback("on_toggle")

    def _on_volume_click(self, btn):
        if self.muted:
            self.unmute()
        else:
            self.mute()
        events._post_sound_player_event(events.SOUNDPLAYER_MUTE, self)
        self.status.invoke_callback("on_mute")

    def _on_track_move(self, slider):
        was_paused = not self.playing or self.paused
        self.stop(self.duration*self.track_slider.get_value())
        self.play()
        if was_paused:
            self.pause()
        events._post_sound_player_event(events.SOUNDPLAYER_TRACK_MOVE, self)
        self.status.invoke_callback("on_track_move")

    def _on_volume_move(self, slider):
        self.media_player.set_volume(self.get_volume())
        events._post_sound_player_event(events.SOUNDPLAYER_VOLUME_MOVE, self)
        self.status.invoke_callback("on_volume_move")

    def on_logic(self):
        self.play_button.set_text(
            self.settings.play_txt if not self.playing else self.settings.pause_txt)
        vol = self.get_volume()
        self.volume_button.set_text(self.settings.volume_mute_txt if vol <=
                                    0 else self.settings.volume_up_txt if vol > 0.38 else self.settings.volume_down_txt)
        if self.playing or self.paused:
            if not self.paused:
                time_passed = ((pygame.time.get_ticks()/1000 -
                               self.play_start_time)+self.pause_position)
                self.track_slider.set_value(
                    time_passed/self.duration)
                if time_passed >= self.duration:
                    self.stop()
                    events._post_sound_player_event(
                        events.SOUNDPLAYER_END, self)
            else:
                self.track_slider.set_value(
                    self.pause_position/self.duration)
        else:
            if self.track_slider.get_value() != 0:
                self.track_slider.set_value(0)

    def build(self):
        if not self.manager._running:
            return
        if not self.__done:
            return
        style = self.style
        btn_size = (self.settings.buttons_size,
                    self.relative_rect.h-style.stack.padding*2)
        self.play_button.set_size(btn_size)
        self.volume_button.set_size(btn_size)
        self.volume_slider.set_size(
            (self.relative_rect.w*self.settings.volume_rel_w, self.relative_rect.h-style.stack.padding*2))
        self.track_slider.set_size((self.relative_rect.w-style.stack.padding-self.volume_slider.relative_rect.w -
                                   self.settings.buttons_size*2-style.stack.spacing*5, self.relative_rect.h-style.stack.padding*2))


class VideoPlayer(Element):
    """Element with control over a video and its sound"""

    def __init__(self,
                 filename: str,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.VideoPlayerSettings|None = None
                 ):
        if settings is None:
            settings = settings_.VideoPlayerSettings()
        self.settings = settings
        if self.settings.sliders_settings is None:
            self.settings.sliders_settings = settings_.SliderSettings()
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "player", "videoplayer"), parent, manager)
        self.filename = filename
        self.media_player = MediaPlayer(filename, ff_opts={
                                        "fast": True, "framedrop": True, "paused": True, "sync": "video"})
        self.video_player = cv2.VideoCapture(self.filename)
        self.fps = self.video_player.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(
            self.video_player.get(cv2.CAP_PROP_FRAME_COUNT))
        self.frame_width = int(self.video_player.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(
            self.video_player.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_surface = pygame.Surface(
            (self.frame_width, self.frame_height)).convert()
        self.last_frame_update = 0
        self.filename = filename
        self.playing = self.paused = self.muted = False
        self.media_player.set_volume(settings.start_volume)
        self.duration = self.total_frames / self.fps

        self.volume_before_mute = self.media_player.get_volume()
        self.play_start_time = self.start_position = self.pause_position = 0
        self.deactivate()

        self.__done = False
        style = self.style
        self.video_image = Image(None,
                                 pygame.Rect(0, 0, 100, 100),
                                 self.element_id+"_video_image",
                                 common.style_id_or_copy(
                                     self, self.settings.video_style_id),
                                 self, self.manager).set_attr("builtin", True)
        self.control_stack = HStack(
            pygame.Rect(0, 0, 200, 50),
            self.element_id+"_control_stack",
            common.style_id_or_copy(self, self.settings.control_style_id), self, self.manager
        ).set_attr("builtin", True)

        self.play_button = Button(
            self.settings.play_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_play_button",
            common.style_id_or_copy(self, self.settings.buttons_style_id),
            False, self.control_stack, self.manager
        ).set_attr("builtin", True)
        self.track_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            common.style_id_or_copy(self, self.settings.sliders_style_id),
            self.control_stack, self.manager,
            self.settings.sliders_settings
        ).set_attr("builtin", True)
        self.volume_button = Button(
            self.settings.volume_up_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_volume_button",
            common.style_id_or_copy(self, self.settings.buttons_style_id),
            False, self.control_stack, self.manager
        ).set_attr("builtin", True)
        self.volume_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            common.style_id_or_copy(self, self.settings.sliders_style_id),
            self.control_stack, self.manager,
            self.settings.sliders_settings
        ).set_attr("builtin", True)
        self.__done = True

        self.video_image.add_element_types("videoplayer_video")
        self.control_stack.add_element_types("videoplayer_control_stack")
        self.play_button.add_element_types(
            "videoplayer_button", "videoplayer_play_button")
        self.volume_button.add_element_types(
            "videoplayer_button", "videoplayer_volume_button")
        self.track_slider.add_element_types(
            "videoplayer_slider", "videoplayer_track_slider")
        self.volume_slider.add_element_types(
            "videoplayer_slider", "videoplayer_volume_slider")
        self.play_button.status.add_listener(
            "on_stop_press", self._on_play_click)
        self.volume_button.status.add_listener(
            "on_stop_press", self._on_volume_click)
        self.track_slider.status.add_listener("on_move", self._on_track_move)
        self.volume_slider.status.add_listener("on_move", self._on_volume_move)

        self.status.register_callbacks(
            "on_toggle", "on_mute", "on_volume_move", "on_track_move")

        self.build()
        self.volume_slider.set_value(settings.start_volume)
        self.track_slider.set_value(0)
        success, frame = self.video_player.read()
        if success:
            pygame.pixelcopy.array_to_surface(
                self.frame_surface,
                numpy.flip(numpy.rot90(frame[::-1]))
            )
            self.video_image.image.set_surface(self.frame_surface.convert_alpha(), True)
        self.stop()

    def play(self):
        """Manually play the video and sound"""
        self.playing = True
        self.play_start_time = pygame.time.get_ticks()/1000
        self.media_player.set_pause(False)
        self.media_player.seek(self.start_position,
                               seek_by_bytes=False, relative=False)
        self.video_player.set(cv2.CAP_PROP_POS_MSEC, self.start_position*1000)
        return self

    def stop(self, start_position: float = 0) -> typing.Self:
        """Manually stop the video and sound. The start_position will determine the seeking position the next time the video starts"""
        self.media_player.set_pause(True)
        self.playing = self.paused = False
        self.track_slider.set_value(start_position/self.duration)
        self.start_position = self.pause_position = start_position
        return self

    def pause(self) -> typing.Self:
        """Manually pause the video and sound"""
        self.media_player.set_pause(True)
        self.playing = False
        self.paused = True
        self.pause_position = (pygame.time.get_ticks(
        )/1000-self.play_start_time)+self.pause_position

    def resume(self) -> typing.Self:
        """Manually resume the video and sound"""
        self.media_player.set_pause(False)
        self.playing = True
        self.paused = False
        self.play_start_time = pygame.time.get_ticks()/1000
        return self

    def set_volume(self, volume: float) -> typing.Self:
        """Manually set the video and sound"""
        self.media_player.set_volume(volume)
        self.volume_slider.set_value(volume)
        return self

    def mute(self) -> typing.Self:
        """Manually mute the video and sound"""
        self.volume_before_mute = self.get_volume()
        self.media_player.set_volume(0)
        self.volume_slider.set_value(0)
        self.muted = True
        return self

    def unmute(self) -> typing.Self:
        """Manually unmute the video and sound"""
        self.media_player.set_volume(self.volume_before_mute)
        self.volume_slider.set_value(self.volume_before_mute)
        self.muted = False
        return self

    def seek(self, time_seconds: float) -> typing.Self:
        """Manually seek the video and sound to a position in time"""
        was_paused = not self.playing or self.paused
        self.stop(time_seconds)
        self.play()
        success, frame = self.video_player.read()
        if success:
            pygame.pixelcopy.array_to_surface(
                self.frame_surface,
                numpy.flip(numpy.rot90(frame[::-1]))
            )
            self.video_image.image.set_surface(self.frame_surface, True)
        if was_paused:
            self.pause()
        return self

    def seek_percent(self, percent: float) -> typing.Self:
        """Manually seek the video and sound to a position in time expressed as a percentage"""
        self.seek(self.duration*(percent/100))
        return self

    def get_volume(self) -> float:
        """Return the sound volume"""
        return self.volume_slider.get_value()

    def get_time_passed(self) -> float:
        """Return how much time has passed since the sound started playing"""
        if self.playing:
            return ((pygame.time.get_ticks()/1000-self.play_start_time)+self.pause_position)
        return self.pause_position/self.duration

    def get_time_remaining(self) -> float:
        """Return how much time is left until the sound stops"""
        return self.duration-self.get_time_passed()

    def _on_play_click(self):
        if not self.playing and not self.paused:
            self.play()
        elif not self.playing and self.paused:
            self.resume()
        else:
            self.pause()
        events._post_video_player_event(events.VIDEOPLAYER_TOGGLE, self)
        self.status.invoke_callback("on_toggle")

    def _on_volume_click(self):
        if self.muted:
            self.unmute()
        else:
            self.mute()
        events._post_video_player_event(events.VIDEOPLAYER_MUTE, self)
        self.status.invoke_callback("on_mute")

    def _on_track_move(self):
        was_paused = not self.playing or self.paused
        self.stop(self.duration*self.track_slider.get_value())
        success, frame = self.video_player.read()
        if success:
            pygame.pixelcopy.array_to_surface(
                self.frame_surface,
                numpy.flip(numpy.rot90(frame[::-1]))
            )
            self.video_image.image.set_surface(self.frame_surface.convert_alpha(), True)
        self.play()
        if was_paused:
            self.pause()
        events._post_video_player_event(events.VIDEOPLAYER_TRACK_MOVE, self)
        self.status.invoke_callback("on_track_move")

    def _on_volume_move(self):
        self.media_player.set_volume(self.get_volume())
        events._post_video_player_event(events.VIDEOPLAYER_VOLUME_MOVE, self)
        self.status.invoke_callback("on_volume_move")

    def on_logic(self):
        self.play_button.set_text(
            self.settings.play_txt if not self.playing else self.settings.pause_txt)
        vol = self.get_volume()
        self.volume_button.set_text(self.settings.volume_mute_txt if vol <=
                                    0 else self.settings.volume_up_txt if vol > 0.38 else self.settings.volume_down_txt)
        if self.playing or self.paused:
            if not self.paused:
                time_passed = ((pygame.time.get_ticks()/1000 -
                               self.play_start_time)+self.pause_position)
                self.track_slider.set_value(
                    time_passed/self.duration)
                if UIState.frame_count-self.last_frame_update >= self.fps/3:
                    success, frame = self.video_player.read()
                    if success:
                        pygame.pixelcopy.array_to_surface(
                            self.frame_surface,
                            numpy.flip(numpy.rot90(frame[::-1]))
                        )
                        self.video_image.image.set_surface(
                            self.frame_surface.convert_alpha(), True)
                    self.last_frame_update = UIState.frame_count
                if time_passed >= self.duration:
                    self.stop()
                    events._post_video_player_event(
                        events.VIDEOPLAYER_END, self)
            else:
                self.track_slider.set_value(
                    self.pause_position/self.duration)
        else:
            if self.track_slider.get_value() != 0:
                self.track_slider.set_value(0)

    def build(self):
        if not self.manager._running:
            return
        if not self.__done:
            return
        style = self.style
        self.video_image.set_relative_pos(
            (style.stack.padding, style.stack.padding))
        self.video_image.set_size((self.relative_rect.w-style.stack.padding*2,
                                  self.relative_rect.h-self.settings.control_h-style.stack.padding*2))
        self.control_stack.set_relative_pos(
            (style.stack.padding, self.video_image.relative_rect.bottom+style.stack.spacing))
        self.control_stack.set_size(
            (self.relative_rect.w, self.settings.control_h))

        style = self.control_stack.style
        btn_size = (self.settings.buttons_size,
                    self.control_stack.relative_rect.h-style.stack.padding*2)
        self.play_button.set_size(btn_size)
        self.volume_button.set_size(btn_size)
        self.volume_slider.set_size(
            (self.control_stack.relative_rect.w*self.settings.volume_rel_w, self.control_stack.relative_rect.h-style.stack.padding*2))
        self.track_slider.set_size((self.control_stack.relative_rect.w-style.stack.padding-self.volume_slider.relative_rect.w -
                                   self.settings.buttons_size*2-style.stack.spacing*5, self.control_stack.relative_rect.h-style.stack.padding*2))
