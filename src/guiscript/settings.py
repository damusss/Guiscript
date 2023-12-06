import dataclasses

from .enums import SliderAxis, ProgressBarDirection, DropMenuDirection


@dataclasses.dataclass(slots=True)
class SlideshowSettings:
    """Initialization settings for the slideshow element"""
    arrows_rel_h: float = 0.22
    arrows_w: int = 30
    arrows_padding: int = 10
    left_arrow_txt: str = "arrow_left"
    right_arrow_txt: str = "arrow_right"
    arrows_style_id: str = "copy"


@dataclasses.dataclass(slots=True)
class SliderSettings:
    """Initialization settings for the slider element"""
    handle_size: int = 20
    bar_size: int = 11
    axis: str = SliderAxis.horizontal
    start_value: float = 0.5
    bar_style_id: str = "copy"
    handle_style_id: str = "copy"


@dataclasses.dataclass(slots=True)
class SoundPlayerSettings:
    """Initialization settings for the sound player element"""
    start_volume: int = 1
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
    """Initialization settings for the video player element"""
    start_volume: int = 1
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


@dataclasses.dataclass(slots=True)
class ProgressBarSettings:
    """Initialization settings for the progress bar element"""
    direction: str = ProgressBarDirection.left_right
    max_value: float = 100


@dataclasses.dataclass(slots=True)
class DropMenuSettings:
    """Initialization settings for the drop menu element"""
    direction: str = DropMenuDirection.down
    option_height: float = 30
    arrow_rel_w: float = 0.15
    down_arrow_txt: str = "arrow_drop_down"
    up_arrow_txt: str = "arrow_drop_up"
    menu_style_id: str = "copy"
    option_style_id: str = "copy"
    inner_buttons_style_id: str = "copy"


@dataclasses.dataclass(slots=True)
class SelectionListSettings:
    """Initialization settings for the selection list element"""
    option_height: float = 30
    multi_select: bool = False
    option_style_id: str = "copy"


SlideshowDefaultSettings = SlideshowSettings()
SliderDefaultSettings = SliderSettings()
SoundPlayerDefaultSettings = SoundPlayerSettings(
    sliders_settings=SliderDefaultSettings)
VideoPlayerDefaultSettings = VideoPlayerSettings(
    sliders_settings=SliderDefaultSettings)
ProgressBarDefaultSettings = ProgressBarSettings()
DropMenuDefaultSettings = DropMenuSettings()
SelectionListDefaultSettings = SelectionListSettings()
