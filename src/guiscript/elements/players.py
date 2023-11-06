import pygame
import typing
import numpy
import cv2
from ffpyplayer.player import MediaPlayer

from .stacks import VStack, HStack
from .factories import Slider, Button, Image
from .element import UIElement
from ..manager import UIManager
from ..state import UIState
from ..enums import ElementAlign, StackAnchor
from ..common import style_id_or_copy
from .. import settings as settings_
from ..import events

# VIDEO PLAYER


class SoundPlayer(HStack):
    def __init__(self,
                 sound: pygame.mixer.Sound,
                 filename: str,
                 relative_rect: pygame.Rect,
                 start_volume: int = 1,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 settings: settings_.SoundPlayerSettings = settings_.SoundPlayerDefaultSettings
                 ):
        self._done = False
        super().__init__(relative_rect, element_id, style_id,
                         StackAnchor.max_spacing, parent, ui_manager)
        self.add_element_types("player", "sound_player")
        self.settings = settings
        if self.settings.sliders_settings is None:
            self.settings.sliders_settings = settings_.SliderDefaultSettings
        self.media_player = MediaPlayer(filename, ff_opts={"paused": True})
        self.filename = filename
        self.playing = self.paused = self.muted = False
        self.media_player.set_volume(start_volume)
        self.pg_sound = sound
        self.duration = self.pg_sound.get_length()
        self.volume_before_mute = self.media_player.get_volume()
        self.play_start_time = self.start_position = self.pause_position = 0

        style = self.callback_component.get_style()
        self.play_button = Button(
            self.settings.play_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_play_button",
            style_id_or_copy(self, self.settings.buttons_style_id),
            False, self, self.ui_manager
        )
        self.track_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            style_id_or_copy(self, self.settings.sliders_style_id),
            self, self.ui_manager, ElementAlign.middle,
            self.settings.sliders_settings
        )
        self.volume_button = Button(
            self.settings.volume_up_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_volume_button",
            style_id_or_copy(self, self.settings.buttons_style_id),
            False, self, self.ui_manager
        )
        self.volume_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            style_id_or_copy(self, self.settings.sliders_style_id),
            self, self.ui_manager, ElementAlign.middle,
            self.settings.sliders_settings
        )
        self._done = True

        self.play_button.add_element_types(
            "sound_player_button", "sound_player_play_button")
        self.volume_button.add_element_types(
            "sound_player_button", "sound_player_volume_button")
        self.track_slider.add_element_types(
            "sound_player_slider", "sound_player_track_slider")
        self.volume_slider.add_element_types(
            "sound_player_slider", "sound_player_volume_slider")
        self.play_button.status.add_listener(
            "on_stop_press", self.on_play_click)
        self.volume_button.status.add_listener(
            "on_stop_press", self.on_volume_click)
        self.track_slider.status.add_listener("on_move", self.on_track_move)
        self.volume_slider.status.add_listener("on_move", self.on_volume_move)

        self.status.register_callbacks(
            "on_toggle", "on_mute", "on_volume_move", "on_track_move")

        self.size_changed()
        self.stop()
        self.volume_slider.set_value(start_volume)

    def play(self):
        self.playing = True
        self.play_start_time = pygame.time.get_ticks()/1000
        self.media_player.set_pause(False)
        self.media_player.seek(self.start_position,
                               seek_by_bytes=False, relative=False)
        return self

    def stop(self, start_position: float = 0) -> typing.Self:
        self.media_player.set_pause(True)
        self.playing = self.paused = False
        self.track_slider.set_value(start_position/self.duration)
        self.start_position = self.pause_position = start_position
        return self

    def pause(self) -> typing.Self:
        self.media_player.set_pause(True)
        self.playing = False
        self.paused = True
        self.pause_position = (pygame.time.get_ticks(
        )/1000-self.play_start_time)+self.pause_position

    def resume(self) -> typing.Self:
        self.media_player.set_pause(False)
        self.playing = True
        self.paused = False
        self.play_start_time = pygame.time.get_ticks()/1000
        return self

    def set_volume(self, volume: float) -> typing.Self:
        self.media_player.set_volume(volume)
        self.volume_slider.set_value(volume)
        return self

    def mute(self) -> typing.Self:
        self.volume_before_mute = self.get_volume()
        self.media_player.set_volume(0)
        self.volume_slider.set_value(0)
        self.muted = True
        return self

    def unmute(self) -> typing.Self:
        self.media_player.set_volume(self.volume_before_mute)
        self.volume_slider.set_value(self.volume_before_mute)
        self.muted = False
        return self

    def seek(self, time_seconds: float) -> typing.Self:
        was_paused = not self.playing or self.paused
        self.stop(time_seconds)
        self.play()
        if was_paused:
            self.pause()
        return self

    def seek_percent(self, percent: float) -> typing.Self:
        self.seek(self.duration*(percent/100))
        return self

    def get_volume(self) -> float:
        return self.volume_slider.get_value()

    def get_time_passed(self) -> float:
        if self.playing:
            return ((pygame.time.get_ticks()/1000-self.play_start_time)+self.pause_position)
        return self.pause_position/self.duration

    def get_time_remaining(self) -> float:
        return self.duration-self.get_time_passed()

    def on_play_click(self, btn):
        if not self.playing and not self.paused:
            self.play()
        elif not self.playing and self.paused:
            self.resume()
        else:
            self.pause()
        events._post_sound_player_event(events.SOUND_PLAYER_TOGGLE, self)
        self.status.invoke_callback("on_toggle")

    def on_volume_click(self, btn):
        if self.muted:
            self.unmute()
        else:
            self.mute()
        events._post_sound_player_event(events.SOUND_PLAYER_MUTE, self)
        self.status.invoke_callback("on_mute")

    def on_track_move(self, slider):
        was_paused = not self.playing or self.paused
        self.stop(self.duration*self.track_slider.get_value())
        self.play()
        if was_paused:
            self.pause()
        events._post_sound_player_event(events.SOUND_PLAYER_TRACK_MOVE, self)
        self.status.invoke_callback("on_track_move")

    def on_volume_move(self, slider):
        self.media_player.set_volume(self.get_volume())
        events._post_sound_player_event(events.SOUND_PLAYER_VOLUME_MOVE, self)
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
                        events.SOUND_PLAYER_END, self)
            else:
                self.track_slider.set_value(
                    self.pause_position/self.duration)
        else:
            if self.track_slider.get_value() != 0:
                self.track_slider.set_value(0)

    def size_changed(self):
        if not self._done:
            return
        style = self.callback_component.get_style()
        btn_size = (self.settings.buttons_size,
                    self.relative_rect.h-style.stack.padding*2)
        self.play_button.set_size(btn_size)
        self.volume_button.set_size(btn_size)
        self.volume_slider.set_size(
            (self.relative_rect.w*self.settings.volume_rel_w, self.relative_rect.h-style.stack.padding*2))
        self.track_slider.set_size((self.relative_rect.w-style.stack.padding-self.volume_slider.relative_rect.w -
                                   self.settings.buttons_size*2-style.stack.spacing*5, self.relative_rect.h-style.stack.padding*2))


class VideoPlayer(UIElement):
    def __init__(self,
                 filename: str,
                 relative_rect: pygame.Rect,
                 start_volume: int = 1,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 settings: settings_.VideoPlayerSettings = settings_.VideoPlayerDefaultSettings
                 ):
        self.settings = settings
        if self.settings.sliders_settings is None:
            self.settings.sliders_settings = settings_.SliderDefaultSettings
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "player", "video_player"), parent, ui_manager)
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
        self.media_player.set_volume(start_volume)
        self.duration = self.total_frames / self.fps

        self.volume_before_mute = self.media_player.get_volume()
        self.play_start_time = self.start_position = self.pause_position = 0
        self.deactivate()

        self._done = False
        style = self.callback_component.get_style()
        self.video_image = Image(None,
                                 pygame.Rect(0, 0, 100, 100),
                                 self.element_id+"_video_image",
                                 style_id_or_copy(
                                     self, self.settings.video_style_id),
                                 self, self.ui_manager)
        self.control_stack = HStack(
            pygame.Rect(0, 0, 200, 50),
            self.element_id+"_control_stack",
            style_id_or_copy(self, self.settings.control_style_id),
            StackAnchor.max_spacing, self, self.ui_manager
        )

        self.play_button = Button(
            self.settings.play_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_play_button",
            style_id_or_copy(self, self.settings.buttons_style_id),
            False, self.control_stack, self.ui_manager
        )
        self.track_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            style_id_or_copy(self, self.settings.sliders_style_id),
            self.control_stack, self.ui_manager, ElementAlign.middle,
            self.settings.sliders_settings
        )
        self.volume_button = Button(
            self.settings.volume_up_txt,
            pygame.Rect(0, 0, self.settings.buttons_size,
                        self.relative_rect.h-style.stack.padding*2),
            self.element_id+"_volume_button",
            style_id_or_copy(self, self.settings.buttons_style_id),
            False, self.control_stack, self.ui_manager
        )
        self.volume_slider = Slider(
            pygame.Rect(0, 0, 100, 100),
            self.element_id+"_track_slider",
            style_id_or_copy(self, self.settings.sliders_style_id),
            self.control_stack, self.ui_manager, ElementAlign.middle,
            self.settings.sliders_settings
        )
        self._done = True

        self.video_image.add_element_types("video_player_video")
        self.control_stack.add_element_types("video_player_control_stack")
        self.play_button.add_element_types(
            "video_player_button", "video_player_play_button")
        self.volume_button.add_element_types(
            "video_player_button", "video_player_volume_button")
        self.track_slider.add_element_types(
            "video_player_slider", "video_player_track_slider")
        self.volume_slider.add_element_types(
            "video_player_slider", "video_player_volume_slider")
        self.play_button.status.add_listener(
            "on_stop_press", self.on_play_click)
        self.volume_button.status.add_listener(
            "on_stop_press", self.on_volume_click)
        self.track_slider.status.add_listener("on_move", self.on_track_move)
        self.volume_slider.status.add_listener("on_move", self.on_volume_move)

        self.status.register_callbacks(
            "on_toggle", "on_mute", "on_volume_move", "on_track_move")

        self.size_changed()
        self.volume_slider.set_value(start_volume)
        self.track_slider.set_value(0)
        success, frame = self.video_player.read()
        if success:
            pygame.pixelcopy.array_to_surface(
                self.frame_surface,
                numpy.flip(numpy.rot90(frame[::-1]))
            )
            self.video_image.image.set_surface(self.frame_surface, True)
        self.stop()

    def play(self):
        self.playing = True
        self.play_start_time = pygame.time.get_ticks()/1000
        self.media_player.set_pause(False)
        self.media_player.seek(self.start_position,
                               seek_by_bytes=False, relative=False)
        self.video_player.set(cv2.CAP_PROP_POS_MSEC, self.start_position*1000)
        return self

    def stop(self, start_position: float = 0) -> typing.Self:
        self.media_player.set_pause(True)
        self.playing = self.paused = False
        self.track_slider.set_value(start_position/self.duration)
        self.start_position = self.pause_position = start_position
        return self

    def pause(self) -> typing.Self:
        self.media_player.set_pause(True)
        self.playing = False
        self.paused = True
        self.pause_position = (pygame.time.get_ticks(
        )/1000-self.play_start_time)+self.pause_position

    def resume(self) -> typing.Self:
        self.media_player.set_pause(False)
        self.playing = True
        self.paused = False
        self.play_start_time = pygame.time.get_ticks()/1000
        return self

    def set_volume(self, volume: float) -> typing.Self:
        self.media_player.set_volume(volume)
        self.volume_slider.set_value(volume)
        return self

    def mute(self) -> typing.Self:
        self.volume_before_mute = self.get_volume()
        self.media_player.set_volume(0)
        self.volume_slider.set_value(0)
        self.muted = True
        return self

    def unmute(self) -> typing.Self:
        self.media_player.set_volume(self.volume_before_mute)
        self.volume_slider.set_value(self.volume_before_mute)
        self.muted = False
        return self

    def seek(self, time_seconds: float) -> typing.Self:
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
        self.seek(self.duration*(percent/100))
        return self

    def get_volume(self) -> float:
        return self.volume_slider.get_value()

    def get_time_passed(self) -> float:
        if self.playing:
            return ((pygame.time.get_ticks()/1000-self.play_start_time)+self.pause_position)
        return self.pause_position/self.duration

    def get_time_remaining(self) -> float:
        return self.duration-self.get_time_passed()

    def on_play_click(self):
        if not self.playing and not self.paused:
            self.play()
        elif not self.playing and self.paused:
            self.resume()
        else:
            self.pause()
        events._post_video_player_event(events.VIDEO_PLAYER_TOGGLE, self)
        self.status.invoke_callback("on_toggle")

    def on_volume_click(self):
        if self.muted:
            self.unmute()
        else:
            self.mute()
        events._post_video_player_event(events.VIDEO_PLAYER_MUTE, self)
        self.status.invoke_callback("on_mute")

    def on_track_move(self):
        was_paused = not self.playing or self.paused
        self.stop(self.duration*self.track_slider.get_value())
        success, frame = self.video_player.read()
        if success:
            pygame.pixelcopy.array_to_surface(
                self.frame_surface,
                numpy.flip(numpy.rot90(frame[::-1]))
            )
            self.video_image.image.set_surface(self.frame_surface, True)
        self.play()
        if was_paused:
            self.pause()
        events._post_video_player_event(events.VIDEO_PLAYER_TRACK_MOVE, self)
        self.status.invoke_callback("on_track_move")

    def on_volume_move(self):
        self.media_player.set_volume(self.get_volume())
        events._post_video_player_event(events.VIDEO_PLAYER_VOLUME_MOVE, self)
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
                            self.frame_surface, True)
                    self.last_frame_update = UIState.frame_count
                if time_passed >= self.duration:
                    self.stop()
                    events._post_video_player_event(
                        events.VIDEO_PLAYER_END, self)
            else:
                self.track_slider.set_value(
                    self.pause_position/self.duration)
        else:
            if self.track_slider.get_value() != 0:
                self.track_slider.set_value(0)

    def size_changed(self):
        if not self._done:
            return
        style = self.callback_component.get_style()
        self.video_image.set_relative_pos(
            (style.stack.padding, style.stack.padding))
        self.video_image.set_size((self.relative_rect.w-style.stack.padding*2,
                                  self.relative_rect.h-self.settings.control_h-style.stack.padding*2))
        self.control_stack.set_relative_pos(
            (style.stack.padding, self.video_image.relative_rect.bottom+style.stack.spacing))
        self.control_stack.set_size(
            (self.relative_rect.w, self.settings.control_h))

        style = self.control_stack.callback_component.get_style()
        btn_size = (self.settings.buttons_size,
                    self.control_stack.relative_rect.h-style.stack.padding*2)
        self.play_button.set_size(btn_size)
        self.volume_button.set_size(btn_size)
        self.volume_slider.set_size(
            (self.control_stack.relative_rect.w*self.settings.volume_rel_w, self.control_stack.relative_rect.h-style.stack.padding*2))
        self.track_slider.set_size((self.control_stack.relative_rect.w-style.stack.padding-self.volume_slider.relative_rect.w -
                                   self.settings.buttons_size*2-style.stack.spacing*5, self.control_stack.relative_rect.h-style.stack.padding*2))
