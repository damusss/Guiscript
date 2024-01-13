import dataclasses
import typing

from .enums import SliderAxis, ProgressBarDirection, DropMenuDirection, Resizer
from . import common
from . import utils


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
    close_when_click_outside: bool = True
    down_arrow_txt: str = "arrow_drop_down"
    up_arrow_txt: str = "arrow_drop_up"
    menu_style_id: str = "copy"
    option_style_id: str = "copy"
    inner_buttons_style_id: str = "copy"
    menu_parent: typing.Any | None = None


@dataclasses.dataclass(slots=True)
class SelectionListSettings:
    """Initialization settings for the selection list element"""
    option_height: float = 30
    multi_select: bool = False
    option_style_id: str = "copy"


@dataclasses.dataclass(slots=True)
class EntrySettings:
    """Initialization settings for the entry element"""
    placeholder: str = "Start typing..."
    inner_style_id: str = ""
    blink_speed: int = 400
    repeat_speed: int = 40
    repeat_start_cooldown: int = 370
    disabled_text_style_id: str = "entry_disabled_text"
    
    
@dataclasses.dataclass(slots=True)
class TextboxSettings:
    """Initialization settings for the textbox element"""
    placeholder: str = "Start typing..."
    inner_style_id: str = ""
    blink_speed: int = 400
    repeat_speed: int = 40
    repeat_start_cooldown: int = 370
    disabled_text_style_id: str = "entry_disabled_text"


@dataclasses.dataclass(slots=True)
class WindowSettings:
    """Initialization settings for the window element"""
    close_button_txt: str = "X"
    title_bar_height: int = 30
    can_resize: bool = True
    destroy_on_close: bool = True
    hide_on_close: bool = False
    have_close_button: bool = True
    have_collapse_button: bool = False
    resizers: tuple[Resizer] = utils.ALL_RESIZERS
    resizers_size: int = 5
    max_size: common.Coordinate | None = None
    min_size: common.Coordinate | None = (120, 60)
    resizers_style_id: str = "copy"
    close_button_style_id: str = "copy"
    collapse_button_style_id: str = "copy"
    title_style_id: str = "copy"
    content_style_id: str = "copy"
    scrollbars_style_id: str = "copy"
    collapse_down_txt: str = "arrow_drop_down"
    collapse_up_txt: str = "arrow_drop_up"
    
    
@dataclasses.dataclass(slots=True)
class ModalSettings:
    destroy_modal_element_on_destroy: bool = True
    hide_when_clicking_sourroundings: bool = False


SlideshowDefaultSettings = SlideshowSettings()
SliderDefaultSettings = SliderSettings()
SoundPlayerDefaultSettings = SoundPlayerSettings(
    sliders_settings=SliderDefaultSettings)
VideoPlayerDefaultSettings = VideoPlayerSettings(
    sliders_settings=SliderDefaultSettings)
ProgressBarDefaultSettings = ProgressBarSettings()
DropMenuDefaultSettings = DropMenuSettings()
SelectionListDefaultSettings = SelectionListSettings()
EntryDefaultSettings = EntrySettings()
TextboxDefaultSettings = TextboxSettings()
WindowDefaultSettings = WindowSettings()
CollapsingWindowDefaultSettings = WindowSettings(
    have_collapse_button=True, have_close_button=False)
ModalDefaultSettings = ModalSettings()
