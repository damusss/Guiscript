import pygame
from enum import StrEnum, IntEnum


class TextAlign(StrEnum):
    """Text alignment inside the element boundaries for the text element component"""
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
    """Integer enum replacing pygame font align constants, used to align wrapped text differently"""
    center = pygame.FONT_CENTER
    left = pygame.FONT_LEFT
    right = pygame.FONT_RIGHT


class ShapeType(StrEnum):
    """The shapes supported by the shape element component"""
    rect = "rect"
    circle = "circle"
    ellipse = "ellipse"
    polygon = "polygon"


class StyleType(StrEnum):
    """[Internal] The types a UIStyle can be"""
    normal = "normal"
    hover = "hover"
    press = "press"


class StyleTarget(StrEnum):
    """[Internal] The target of a style holder"""
    element_type = "element_type"
    style_id = "style_id"
    element_id = "element_id"


class ElementAlign(StrEnum):
    """Where is the element placed in the parent in the opposite axis of the stack"""
    middle = "center"
    left = "left"
    right = "right"
    top = "top"
    bottom = "bottom"


class StackAnchor(StrEnum):
    """Where are elements anchored where there is space left in the stack's axis"""
    middle = "center"
    left = "left"
    right = "right"
    top = "top"
    bottom = "bottom"
    max_spacing = "max_spacing"


class SliderAxis(StrEnum):
    """The directions a slider can have"""
    horizontal = "horizontal"
    vertical = "vertical"


class DropMenuDirection(StrEnum):
    """The directions a drop menu can have"""
    up = "up"
    down = "down"


class ProgressBarDirection(StrEnum):
    """The directions a progress bar can have"""
    left_right = "left_right"
    right_left = "right_left"
    top_bottom = "top_bottom"
    bottom_top = "bottom_top"


class AnimPropertyType(StrEnum):
    """What a property animation is targetting"""
    x = "x"
    y = "y"
    width = "width"
    height = "height"
    render_x = "render_x"
    render_y = "render_y"


class AnimRepeatMode(StrEnum):
    """How should the property animation repeat when it ends"""
    norepeat = "norepeat"
    restart = "restart"
    repeat = "repeat"


class AnimEaseFunc(StrEnum):
    """The easing function to use when animating"""
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
    """Types supported by style animations"""
    number = "number"
    color = "color"
    

class Resizer(StrEnum):
    """Names of the resizers an element can have"""
    top = "top"
    bottom = "bottom"
    left = "left"
    right = "right"
    topleft = "topleft"
    bottomleft = "bottomleft"
    topright = "topright"
    bottomright = "bottomright"
    
    
class Anchor(StrEnum):
    """Dynamic element anchor names"""
    none = "none"
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
