import dataclasses

from .enums import SliderAxis


@dataclasses.dataclass(slots=True)
class SlideshowSettings:
    arrows_rel_h: float = 0.22
    arrows_w: int = 30
    arrows_padding: int = 10
    left_arrow_txt: str = "arrow_left"
    right_arrow_txt: str = "arrow_right"
    arrows_style_id: str = "copy"


@dataclasses.dataclass(slots=True)
class SliderSettings:
    handle_size: int = 20
    bar_size: int = 11
    axis: str = SliderAxis.horizontal
    start_value: float = 0.5
    bar_style_id: str = "copy"
    handle_style_id: str = "copy"


@dataclasses.dataclass(slots=True)
class SoundPlayerSettings:
    buttons_size: int = 30
    volume_rel_w: float = 0.2
    play_txt: str = "play_arrow"
    pause_txt: str = "pause"
    volume_up_txt: str = "volume_up"
    volume_down_txt: str = "volume_down"
    volume_mute_txt: str = "volume_off"
    buttons_style_id: str = "copy"
    sliders_style_id: str = "copy"
    sliders_settings: SliderSettings = None
    

@dataclasses.dataclass(slots=True)
class VideoPlayerSettings:
    buttons_size: int = 30
    control_h: float = 50
    volume_rel_w: float = 0.2
    play_txt: str = "play_arrow"
    pause_txt: str = "pause"
    volume_up_txt: str = "volume_up"
    volume_down_txt: str = "volume_down"
    volume_mute_txt: str = "volume_off"
    buttons_style_id: str = "copy"
    sliders_style_id: str = "copy"
    video_style_id: str = "copy"
    control_style_id: str = "copy"
    sliders_settings: SliderSettings = None

SlideshowDefaultSettings = SlideshowSettings()
SliderDefaultSettings = SliderSettings()
SoundPlayerDefaultSettings = SoundPlayerSettings(sliders_settings=SliderDefaultSettings)
VideoPlayerDefaultSettings = VideoPlayerSettings(sliders_settings=SliderDefaultSettings)
