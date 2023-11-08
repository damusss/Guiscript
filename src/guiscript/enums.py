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
