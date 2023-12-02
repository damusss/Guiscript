import math
import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import UIElement

from .error import UIError
from .state import UIState

Coordinate: typing.TypeAlias = typing.Iterable[float] | pygame.Vector2
Color: typing.TypeAlias = typing.Iterable[int] | str | pygame.Color
StatusCallback: typing.TypeAlias = typing.Callable[[
    "UIElement"], typing.Any] | None


def style_id_or_copy(element: "UIElement", style_id: str) -> str:
    return element.style_id if style_id == "copy" else style_id


def align_text(t_rect: pygame.Rect, el_rect: pygame.Rect, padding: int, y_padding: int, align: str) -> pygame.Rect:
    match align:
        case "center":
            t_rect.center = el_rect.center
        case "topleft":
            t_rect.topleft = (el_rect.left+padding, el_rect.top+y_padding)
        case "topright":
            t_rect.topright = (el_rect.right-padding, el_rect.top+y_padding)
        case "bottomleft":
            t_rect.bottomleft = (el_rect.left+padding,
                                 el_rect.bottom-y_padding)
        case "bottomright":
            t_rect.bottomright = (el_rect.right-padding,
                                  el_rect.bottom-y_padding)
        case "midleft" | "left":
            t_rect.midleft = (el_rect.left+padding, el_rect.centery)
        case "midright" | "right":
            t_rect.midright = (el_rect.right-padding, el_rect.centery)
        case "midtop" | "top":
            t_rect.midtop = (el_rect.centerx, el_rect.top+y_padding)
        case "midbottom" | "bottom":
            t_rect.midbottom = (el_rect.centerx, el_rect.bottom-y_padding)
        case _:
            raise UIError(f"Unsupported text align: '{align}'")
    return t_rect


def text_wrap_str(text: str, wrapsize: int, font: pygame.Font) -> list[str]:
    text = text.strip()
    if not text:
        return []
    paragraphs = text.split("\n")
    paragraph_lines = []
    space = font.size(' ')[0]
    for paragraph in paragraphs:
        words = paragraph.split(' ')
        x, y, maxw, i = 0, 0, wrapsize, 0
        lines = []
        line = ""
        for abs_i, word in enumerate(words):
            if not word:
                continue
            wordw, wordh = font.render(word, True, (0, 0, 0)).get_size()
            if i != 0:
                line += " "
            line += word
            if x + wordw >= maxw:
                x = i = 0
                y += wordh
                if abs_i != 0:
                    line = line.removesuffix(" "+word)
                lines.append(line)
                if abs_i != 0:
                    line = word
            x += wordw
            if x != 0:
                x += space
            i += 1
        lines.append(line)
        paragraph_lines += lines
    return paragraph_lines


def text_click_idx(lines: list[str], font: pygame.Font, pos: pygame.Vector2, rect: pygame.Rect, absolute_topleft: pygame.Vector2) -> tuple[int, int, int, str] | None:
    if len(lines) <= 0:
        return
    rel_pos = pos-absolute_topleft
    if not rect.collidepoint(rel_pos):
        return
    line_idx = int((rel_pos.y-rect.top)//font.get_height())
    if line_idx < 0 or line_idx >= len(lines):
        return
    line = lines[line_idx]
    if not line:
        return
    start_x = tot_w = char_i = 0
    if font.align == pygame.FONT_CENTER:
        start_x = rect.w//2-font.size(line)[0]//2
    elif font.align == pygame.FONT_RIGHT:
        start_x = rect.w-font.size(line)[0]
    rel_x = rel_pos.x
    if rel_x <= start_x:
        return
    for i, char in enumerate(line):
        char_w = font.size(char)[0]
        tot_w += char_w
        if tot_w+start_x >= rel_x:
            char_i = i
            break
    else:
        return
    tot_i = 0
    if line_idx > 0:
        for l in lines[:line_idx]:
            tot_i += len(l)
    tot_i += char_i
    return char_i, line_idx, tot_i, "".join(lines)


def text_select_rects(start_li: int, start_ci: int, end_li: int, end_ci: int, lines: list[str], font: pygame.Font, rect: pygame.Rect, rel_move: bool = False) -> list[pygame.Rect]:
    if start_li > end_li:
        start_li, end_li = end_li, start_li
        start_ci, end_ci = end_ci, start_ci
    rects = []
    font_h = font.get_height()
    try:
        if start_li == end_li:
            line = lines[start_li]
            offset = 0
            if font.align == pygame.FONT_CENTER:
                offset = rect.w//2-font.size(line)[0]//2
            elif font.align == pygame.FONT_RIGHT:
                offset = rect.w-font.size(line)[0]
            if start_ci == end_ci:
                if not rel_move or not UIState.mouse_pressed[0]:
                    return rects
                char = lines[start_li][start_ci]
                rects.append(pygame.Rect(rect.left+offset+font.size(line[:start_ci])[0], font_h*start_li+rect.top, font.size(char)[0], font_h))
                return rects
            if start_ci > end_ci:
                start_ci, end_ci = end_ci, start_ci
            rects.append(pygame.Rect(rect.left+offset+font.size(line[:start_ci])[0],
                                     font_h*start_li+rect.top, font.size(line[start_ci:end_ci+1])[0], font_h))
        else:
            mid_lines = lines[start_li+1:end_li]
            start_line = lines[start_li]
            end_line = lines[end_li]
            start_offset = end_offset = 0
            if font.align == pygame.FONT_CENTER:
                start_offset = rect.w//2-font.size(start_line)[0]//2
                end_offset = rect.w//2-font.size(end_line)[0]//2
            elif font.align == pygame.FONT_RIGHT:
                start_offset = rect.w-font.size(start_line)[0]
                end_offset = rect.w-font.size(end_line)[0]
            rects.append(pygame.Rect(rect.left+start_offset+font.size(start_line[:start_ci])[0],
                                     font_h*start_li+rect.top, font.size(start_line[start_ci:])[0], font_h))
            rects.append(pygame.Rect(rect.left+end_offset, font_h*end_li +
                         rect.top, font.size(end_line[:end_ci+1])[0], font_h))
            for i, line in enumerate(mid_lines):
                offset = 0
                if font.align == pygame.FONT_CENTER:
                    offset = rect.w//2-font.size(line)[0]//2
                elif font.align == pygame.FONT_RIGHT:
                    offset = rect.w-font.size(line)[0]
                rects.append(pygame.Rect(rect.left+offset, font_h *
                             (i+start_li+1)+rect.top, font.size(line)[0], font_h))
    except Exception as e:
        return rects
    return rects


def text_select_copy(start_li: int, start_ci: int, end_li: int, end_ci: int, lines: list[str]):
    copy_str = ""
    if start_li > end_li:
        start_li, end_li = end_li, start_li
        start_ci, end_ci = end_ci, start_ci
    if start_li == end_li:
        if start_ci > end_ci:
            start_ci, end_ci = end_ci, start_ci
        copy_str = lines[start_li][start_ci:end_ci+1]
    else:
        mid_lines = lines[start_li+1:end_li]
        copy_str += " "*start_ci+lines[start_li][start_ci:]+"\n"
        for line in mid_lines:
            copy_str += line+"\n"
        copy_str += lines[end_li][:end_ci]
    pygame.scrap.put_text(copy_str)


def generate_menu_surface(original_image: pygame.Surface, width: int, height: int, border: int) -> pygame.Surface:
    if border < 1:
        return original_image
    # setup
    s, s2 = border, border*2
    width, height = int(width), int(height)
    menu_surf: pygame.Surface = original_image
    mw, mh = menu_surf.get_width(), menu_surf.get_height()
    # main surfs
    try:
        big_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    except pygame.error:
        return original_image
    big_surf.fill(0)
    inner_surf = pygame.transform.scale(menu_surf.subsurface(
        (s, s, mw-s2, mh-s2)), (max(width-s2, 1), max(height-s2, 1)))
    # corners
    topleft = menu_surf.subsurface((0, 0, s, s))
    topright = menu_surf.subsurface((mw-s, 0, s, s))
    bottomleft = menu_surf.subsurface((0, mh-s, s, s))
    bottomright = menu_surf.subsurface((mw-s, mh-s, s, s))
    # sides
    top = pygame.transform.scale(menu_surf.subsurface(
        (s, 0, mw-s2, s)), (max(width-s2, 1), s))
    bottom = pygame.transform.scale(menu_surf.subsurface(
        (s, mh-s, mw-s2, s)), (max(width-s2, 1), s))
    left = pygame.transform.scale(menu_surf.subsurface(
        (0, s, s, mh-s2)), (s, max(height-s2, 1)))
    right = pygame.transform.scale(menu_surf.subsurface(
        (mw-s, s, s, mh-s2)), (s, max(height-s2, 1)))
    # blitting
    big_surf.blit(inner_surf, (s, s))
    big_surf.blit(topleft, (0, 0))
    big_surf.blit(topright, (width-s, 0))
    big_surf.blit(bottomleft, (0, height-s))
    big_surf.blit(bottomright, (width-s, height-s))
    big_surf.blit(top, (s, 0))
    big_surf.blit(bottom, (s, height-s))
    big_surf.blit(left, (0, s))
    big_surf.blit(right, (width-s, s))
    # return
    return big_surf


def lerp(a: float, b: float, t: float) -> float:
    return a + t*(b-a)


def linear(t: float) -> float:
    return t


def ease_in(t: float) -> float:
    return t * t


def ease_out(t: float) -> float:
    return t * (2 - t)


def ease_in_quad(t: float) -> float:
    return t * t


def ease_out_quad(t: float) -> float:
    return t * (2 - t)


def ease_in_cubic(t: float) -> float:
    return t * t * t


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_quart(t: float) -> float:
    return t * t * t * t


def ease_out_quart(t: float) -> float:
    return 1 - (1 - t) ** 4


def ease_in_quint(t: float) -> float:
    return t * t * t * t * t


def ease_out_quint(t: float) -> float:
    return 1 - (1 - t) ** 5


def ease_in_sine(t: float) -> float:
    return 1 - math.cos((t * math.pi) / 2)


def ease_out_sine(t: float) -> float:
    return math.sin((t * math.pi) / 2)


def ease_in_expo(t: float) -> float:
    return 0 if t == 0 else 2 ** (10 * (t - 1))


def ease_out_expo(t: float) -> float:
    return 1 if t == 1 else 1 - 2 ** (-10 * t)


def ease_out_circ(t: float) -> float:
    return math.sqrt(abs(1 - (t - 1) * (t - 1)))


ANIMATION_FUNCTIONS = {
    'linear': linear,
    'ease_in': ease_in,
    'ease_out': ease_out,
    'ease_in_quad': ease_in_quad,
    'ease_out_quad': ease_out_quad,
    'ease_in_cubic': ease_in_cubic,
    'ease_out_cubic': ease_out_cubic,
    'ease_in_quart': ease_in_quart,
    'ease_out_quart': ease_out_quart,
    'ease_in_quint': ease_in_quint,
    'ease_out_quint': ease_out_quint,
    'ease_in_sine': ease_in_sine,
    'ease_out_sine': ease_out_sine,
    'ease_in_expo': ease_in_expo,
    'ease_out_expo': ease_out_expo,
    'ease_out_circ': ease_out_circ,
}


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
    "on_move",
    "on_first_frame",
    "on_animation_end"
]


Z_INDEXES = {
    "ghost": -100,
    "element": 0,
    "scrollbar": 100,
    "menu": 150,
    "tooltip": 200,
}


STYLE_ANIMATION_TYPES = {
    "stack": {
        "spacing": "number",
        "padding": "number",
        "scrollbar_size": "number"
    },
    "bg": {
        "color": "color",
        "border_radius": "number"
    },
    "image": {
        "padding": "number",
        "border_radius": "number",
        "border_size": "number",
        "border_scale": "number",
        "outline_width": "number",
        "outline_color": "color"
    },
    "shape": {
        "color": "color",
        "outline_width": "number",
        "padding": "number",
        "rect_border_radius": "number",
        "ellipse_padding_x": "number",
        "ellipse_padding_y": "number"
    },
    "text": {
        "color": "color",
        "selection_color": "color",
        "padding": "number",
        "y_padding": "number",
        "font_size": "number"
    },
    "icon": {
        "scale": "number",
        "padding": "number"
    },
    "outline": {
        "color": "color",
        "navigation_color": "color",
        "width": "number",
        "border_radius": "number"
    }
}

DEFAULT_STYLE_GSS: str = """
// BUILTIN ELEMENT TYPES
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

imagebutton, iconbutton:: {
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

slideshow, gif, videoplayer_video, videoplayer_control_stack, dropmenu:: {
    bg.enabled false;
    outline.enabled false;
}

slider:: {
    bg.enabled false;
    outline.enabled false;
}

videoplayer:: {
    image.enabled true;
}

progressbar:: {
    shape.enabled true;
    shape.type rect;
}

dropmenu:: {
    stack.padding 0;
}

selectionlist:: {
    stack.padding 2;
    stack.spacing 2;
    stack.anchor top;
}

line:: {
    bg.color (50, 50, 50);
    bg.border_radius 1;
    outline.border_radius 1;
}

// SPECIFIC
slideshow_arrow:: {
    text.font_name googleicons;
    text.font_size 30;
    bg.enabled false;
    outline.enabled false;
}

soundplayer_button,videoplayer_button:: {
    text.font_name googleicons;
    text.font_size 30;
    bg.enabled false;
    outline.enabled false;
}

dropmenu_arrow::{
    text.font_name googleicons;
    text.font_size 30;
}

dropmenu_option, selectionlist_option:: {
    stack.fill_x true;
    outline.enabled false;
    bg.border_radius 0;
    outline.border_radius 0;
}

dropmenu_menu:: {
    stack.grow_y true;
    stack.padding 2;
    stack.spacing 2;
}

slideshow_arrow, soundplayer_button, videoplayer_button:hover:press {
    bg.enabled true;
}

tooltip_title:: {
    text.font_size 23;
}

tooltip_description:: {
    text.font_size 20;
}

// BUILTIN STYLE GROUPS
.active_cont:hover {
    bg.color (32, 32, 32);
}

.active_cont:press {
    bg.color (17, 17, 17);
}

.active_cont {
    bg.color (25, 25, 25);
}

.invis_cont, invisible_container:: {
    bg.enabled false;
    outline.enabled false;
    stack.padding 0;
}

.invisible:: {
    bg.enabled false;
    outline.enabled false;
    text.enabled false;
    image.enabled false;
    icon.enabled false;
    shape.enabled false;
    stack.padding false;
}

.icons_font:: {
    text.font_name googleicons;
    text.font_size 30;
}

.no_scroll:: {
    stack.scroll_x false;
    stack.scroll_y false;
}

.no_padding:: {
    stack.padding 0;
    text.padding 0;
    image.padding 0;
    shape.padding 0;
}

.fill:: {
    stack.fill_x true;
    stack.fill_y true;
}

.fill_x:: {
    stack.fill_x true;
}

.fill_y:: {
    stack.fill_y true;
}
"""
