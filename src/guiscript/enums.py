import pygame
from enum import StrEnum, IntEnum


class TextAlign(StrEnum):
    middle = "center"
    topleft = "topleft"
    topright = "topright"
    bottomleft = "bottomleft"
    bottomright = "bottomright"
    midleft = "midleft"
    midright = "midright"
    midtop = "midtop"
    midbottom = "midbottom"
    left = "left"
    right = "right"
    top = "top"
    bottom = "bottom"


class FontAlign(IntEnum):
    center = pygame.FONT_CENTER
    left = pygame.FONT_LEFT
    right = pygame.FONT_RIGHT


class ShapeType(StrEnum):
    rect = "rect"
    circle = "circle"
    ellipse = "ellipse"
    polygon = "polygon"


class StyleType(StrEnum):
    normal = "normal"
    hover = "hover"
    press = "press"


class StyleTarget(StrEnum):
    element_type = "element_type"
    style_id = "style_id"
    element_id = "element_id"


class ElementAlign(StrEnum):
    middle = "center"
    left = "left"
    right = "right"
    top = "top"
    bottom = "bottom"


class StackAnchor(StrEnum):
    middle = "center"
    left = "left"
    right = "right"
    top = "top"
    bottom = "bottom"
    max_spacing = "max_spacing"


class SliderAxis(StrEnum):
    horizontal = "horizontal"
    vertical = "vertical"


class DropMenuDirection(StrEnum):
    up = "up"
    down = "down"


class ProgressBarDirection(StrEnum):
    left_right = "left_right"
    right_left = "right_left"
    top_bottom = "top_bottom"
    bottom_top = "bottom_top"


class AnimPropertyType(StrEnum):
    x = "x"
    y = "y"
    width = "width"
    height = "height"
    
    
class AnimRepeatMode(StrEnum):
    norepeat = "norepeat"
    restart = "restart"
    repeat = "repeat"
    
    
class AnimEaseFunc(StrEnum):
    linear = 'linear'
    ease_in = 'ease_in'
    ease_out = 'ease_out'
    in_quad = 'ease_in_quad'
    out_quad = 'ease_out_quad'
    in_cubic = 'ease_in_cubic'
    out_cubic = 'ease_out_cubic'
    in_quart = 'ease_in_quart'
    out_quart = 'ease_out_quart'
    in_quint = 'ease_in_quint'
    out_quint = 'ease_out_quint'
    in_sine = 'ease_in_sine'
    out_sine = 'ease_out_sine'
    in_expo = 'ease_in_expo'
    out_expo = 'ease_out_expo'
    out_circ = 'ease_out_circ'
    
class StyleAnimPropertyType(StrEnum):
    number = "number"
    color = "color"
