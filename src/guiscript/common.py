import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import UIElement

VERSION = "WIP"

Coordinate: typing.TypeAlias = typing.Iterable[float] | pygame.Vector2
Color: typing.TypeAlias = typing.Iterable[int] | str | pygame.Color
StatusCallback: typing.TypeAlias = typing.Callable[["UIElement"], typing.Any] | None


def style_id_or_copy(element: "UIElement", style_id: str) -> str:
    return element.style_id if style_id == "copy" else style_id


DEFAULT_CALLBACKS: list[str] = [
    "when_hovered",
    "when_pressed",
    "when_right_pressed",
    "on_start_hover",
    "on_start_press",
    "on_start_right_press",
    "on_stop_hover",
    "on_stop_press",
    "on_stop_right_press",
    "on_select",
    "on_deselect",
    "on_click",
    "on_right_click",
    "on_move"
]

DEFAULT_STYLE_GSS: str = """
// BUILTIN ELEMENT TYPES
element:: {
    text.enabled false;
    shape.enabled false;
    image.enabled false;
    icon.enabled false;
}

label:: {
    text.enabled true;
    bg.enabled false;
    outline.enabled false;
}

icon:: {
    icon.enabled true;
    outline.enabled false;
    bg.enabled false;
}

button:: {
    text.enabled true;
    outline.enabled true;
    bg.enabled true;
}

image_button, icon_button:: {
    text.enabled false;
}

image:: {
    image.enabled true;
    image.outline_width 1;
}

stack, scrollbar, slideshow, slider_bar, player::{
    bg.color $DARK_COLOR;
}

checkbox:hover: {
    shape.enabled false;
    text.enabled false;
}

checkbox:press {
    shape.enabled true;
    text.enabled false;
}

slideshow, gif, video_player_video, video_player_control_stack:: {
    bg.enabled false;
    outline.enabled false;
}

slider:: {
    bg.enabled false;
    outline.enabled false;
}

video_player:: {
    image.enabled true;
}

// SPECIFIC
slideshow_arrow:: {
    text.font_name googleicons;
    text.font_size 30;
    bg.enabled false;
    outline.enabled false;
}

sound_player_button,video_player_button:: {
    text.font_name googleicons;
    text.font_size 30;
    bg.enabled false;
    outline.enabled false;
}

slideshow_arrow, sound_player_button, video_player_button:hover:press {
    bg.enabled true;
}

// BUILTIN STYLE GROUPS
.invis_cont, invisible_container:: {
    bg.enabled false;
    outline.enabled false;
    stack.padding 0;
}

.icons_font:: {
    text.font_name googleicons;
    text.font_size 30;
}

.no_scroll {
    stack.scroll_x false;
    stack.scroll_y false;
}

.no_padding {
    stack.padding 0;
    text.padding 0;
    image.padding 0;
    shape.padding 0;
}
"""
