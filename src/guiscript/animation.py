import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import UIElement
    from .style import UIStyle

from .enums import AnimPropertyType, AnimRepeatMode, AnimEaseFunc, StyleAnimPropertyType
from . import common


class UIAnimation:
    """Base class for UI animations"""

    def start(self) -> typing.Self:
        """Start animating"""
        ...

    def logic(self):
        """Update the value"""
        ...

    def apply_value(self) -> typing.Self:
        """Apply the value to the element/style"""
        ...

    def get_elapsed_time(self) -> float:
        """Return how much time passed since 'start' was called"""
        return 0


class UIPropertyAnim(UIAnimation):
    """Animation object for element properties"""

    def __init__(self,
                 element: "UIElement",
                 property_type: AnimPropertyType,
                 increase: float,
                 duration_ms: float,
                 repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                 ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in,
                 start: bool = True
                 ):
        self.element: "UIElement" = element
        self.property_type: AnimPropertyType = property_type
        self.repeat_mode: AnimRepeatMode = repeat_mode
        self.ease_func = common.ANIMATION_FUNCTIONS[ease_func_name]
        self.direction = 1
        self.increase_dir = 1 if increase >= 0 else -1
        self.end_value: float = abs(increase)
        self.duration_ms: float = duration_ms
        if self.duration_ms <= 0:
            self.duration_ms = 1
        self.start_value: float = getattr(
            element.relative_rect, self.property_type)
        self.current_value: float = 0
        self.started: bool = False
        self.start_time: int = -1
        self.dead: bool = False
        UIAnimUpdater.register(self)
        if start:
            self.start()

    def start(self) -> typing.Self:
        self.started = True
        self.current_value: float = 0
        self.start_time = pygame.time.get_ticks()
        return self

    def get_elapsed_time(self) -> float:
        if not self.started:
            return -1
        return pygame.time.get_ticks()-self.start_time

    def apply_value(self) -> typing.Self:
        match self.property_type:
            case AnimPropertyType.x:
                self.element.set_relative_pos(
                    (self.start_value+self.current_value*self.increase_dir, self.element.relative_rect.y))
            case AnimPropertyType.y:
                self.element.set_relative_pos(
                    (self.element.relative_rect.x, self.start_value+self.current_value*self.increase_dir))
            case AnimPropertyType.width:
                self.element.set_size(
                    (self.start_value+self.current_value*self.increase_dir, self.element.relative_rect.height), True)
            case AnimPropertyType.height:
                self.element.set_size(
                    (self.element.relative_rect.width, self.start_value+self.current_value*self.increase_dir), True)
        return self

    def logic(self):
        if not self.started:
            return
        lerp_val = common.lerp(0, self.end_value, self.ease_func(
            self.get_elapsed_time()/self.duration_ms))
        if self.direction == 1:
            self.current_value = lerp_val
            if self.current_value > self.end_value-1:
                self.current_value = self.end_value
                match self.repeat_mode:
                    case AnimRepeatMode.norepeat:
                        self.started = False
                        self.dead = True
                    case AnimRepeatMode.restart:
                        self.start()
                    case AnimRepeatMode.repeat:
                        self.direction = -1
                        self.start_time = pygame.time.get_ticks()
        else:
            self.current_value = self.end_value-lerp_val
            if self.current_value <= 1:
                self.current_value = 0
                match self.repeat_mode:
                    case AnimRepeatMode.norepeat:
                        self.started = False
                        self.direction = 1
                        self.dead = True
                    case AnimRepeatMode.restart:
                        self.direction = 1
                        self.start()
                    case AnimRepeatMode.repeat:
                        self.direction = 1
                        self.start_time = pygame.time.get_ticks()

        self.apply_value()


class UIStyleAnim(UIAnimation):
    """Animation object for style properties"""

    def __init__(self,
                 style: "UIStyle",
                 styles: list["UIStyle"],
                 comp_name: str,
                 property_name: str,
                 property_type: StyleAnimPropertyType,
                 duration_ms: float,
                 value,
                 ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in
                 ):
        self.style: "UIStyle" = style
        self.styles: list["UIStyle"] = styles
        self.comp_name: str = comp_name
        self.property_name: str = property_name
        self.property_type: StyleAnimPropertyType = property_type
        self.duration_ms: float = duration_ms
        if self.duration_ms <= 0:
            self.duration_ms = 1
        self.end_value = value if self.property_type == StyleAnimPropertyType.number else pygame.Color(
            value) if self.property_type == StyleAnimPropertyType.color else None
        self.ease_func = common.ANIMATION_FUNCTIONS[ease_func_name]
        self.should_build_font = self.comp_name == "text" and self.property_name in [
            "sysfont", "font_name", "font_size"]
        self.start_time = -1
        self.start_value = None
        self.current_value = None
        self.completed = True

    def apply_value(self) -> typing.Self:
        for style in self.styles:
            setattr(getattr(style, self.comp_name),
                    self.property_name, self.current_value)
            style.dirty = True
            if self.should_build_font:
                style.text.build_font()
        return self

    def start(self) -> typing.Self:
        self.completed = False
        start_value = getattr(
            getattr(self.style, self.comp_name), self.property_name)
        self.start_value = start_value if self.property_type == StyleAnimPropertyType.number else pygame.Color(
            start_value) if self.property_type == StyleAnimPropertyType.color else None
        self.current_value = self.start_value
        self.start_time = pygame.time.get_ticks()
        return self

    def get_elapsed_time(self) -> float:
        if self.completed:
            return -1
        return pygame.time.get_ticks()-self.start_time

    def logic(self):
        if self.completed:
            return

        if self.property_type == StyleAnimPropertyType.number:
            lerp_val = common.lerp(self.start_value, self.end_value, self.ease_func(
                self.get_elapsed_time()/self.duration_ms))

            self.current_value = lerp_val
            if abs(self.end_value-self.current_value) <= 1:
                self.current_value = self.end_value
                self.completed = True

        elif self.property_type == StyleAnimPropertyType.color:
            self.current_value = self.start_value.lerp(self.end_value, pygame.math.clamp(self.ease_func(
                self.get_elapsed_time()/self.duration_ms), 0.0, 1.0))
            if abs(self.end_value.r-self.current_value.r) <= 1 and \
                    abs(self.end_value.g-self.current_value.g) <= 1 and \
                    abs(self.end_value.b-self.current_value.b) <= 1 and \
                    abs(self.end_value.a-self.current_value.a) <= 1:

                self.current_value = self.end_value
                self.completed = True

        self.apply_value()


class UIAnimUpdater:
    """Static class that updates element property animations"""
    animations: list[UIPropertyAnim] = []

    @classmethod
    def logic(cls):
        """[Internal] Update animations and remove finished ones. Called by 'static_logic'"""
        for anim in list(cls.animations):
            anim.logic()
            if anim.dead:
                cls.animations.remove(anim)

    @classmethod
    def register(cls, animation: UIPropertyAnim) -> typing.Self:
        """[Internal] Add an animation to the animations to update. Called automatically by the animation"""
        cls.animations.append(animation)
        return cls