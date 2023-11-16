import pygame
import typing
from . import common
if typing.TYPE_CHECKING:
    from .elements.element import UIElement


class UIStatus:
    """Hold an element current status and callbacks"""

    def __init__(self, element: "UIElement"):
        self.element: "UIElement" = element
        
        self.hovered: bool = False
        self.pressed: bool = False
        self.right_pressed: bool = False

        self.selected: bool = False
        self.scroll_hovered: bool = False

        self.can_select: bool = False
        self.can_navigate: bool = True
        
        self.hover_start_time: float = 0
        self.press_start_time: float = 0
        self.right_press_start_time: float = 0

        self.callbacks: dict[str, list[common.StatusCallback]] = {}
        self.register_callbacks(*common.DEFAULT_CALLBACKS)

    def register_callback(self, name: str, start_listeners: list[common.StatusCallback] = None) -> typing.Self:
        """Create a new callback type and add given listeners to it"""
        if start_listeners is None:
            start_listeners = []
        self.callbacks[name] = start_listeners
        return self

    def register_callbacks(self, *names: str) -> typing.Self:
        """Create multiple callback types at once"""
        for name in names:
            self.register_callback(name)
        return self

    def add_listener(self, callback_name: str, callback: common.StatusCallback) -> typing.Self:
        """Add a callback function to the given callback type. Callbacks will be called passing the element and the invoker args. If the function takes no arguments the element will not be passed"""
        if not callback_name in self.callbacks:
            self.register_callback(callback_name, [callback])
            return self
        self.callbacks[callback_name].append(callback)
        return self

    def add_listeners(self, callback_name: str, *callbacks: common.StatusCallback) -> typing.Self:
        """Add multiple callback functions to the same callback type. Callbacks will be called passing the element and the invoker args. If the function takes no arguments the element will not be passed"""
        for callback in callbacks:
            self.add_listener(callback_name, callback)
        return self
    
    def add_multi_listeners(self, **names_callbacks: common.StatusCallback) -> typing.Self:
        """Add different callbacks to different callback types provided with kwargs. Callbacks will be called passing the element and the invoker args. If the function takes no arguments the element will not be passed"""
        for name, callback in names_callbacks.items():
            self.add_listener(name, callback)
        return self

    def invoke_callback(self, name: str, *args) -> typing.Self:
        """Invoke all functions registered to the given callback name. Callbacks will be called passing the element and the invoker args. If the function takes no arguments the element will not be passed"""
        if not name in self.callbacks:
            return self
        for callback in self.callbacks[name]:
            try:
                callback(self.element, *args)
            except TypeError as e:
                if "takes 0 positional arguments but 1 was given" in str(e) or "takes 1 positional argument but 2 were given" in str(e):
                    callback(*args)
                    return self
                raise e
        return self

    def invoke_callbacks(self, *names: str) -> typing.Self:
        """Invoke all functions registered to the given callback names. Callbacks will be called passing the element and the invoker args. If the function takes no arguments the element will not be passed"""
        for name in names:
            self.invoke_callback(name)
        return self

    def enable_selection(self) -> typing.Self:
        """Set the can_select flag to True"""
        self.can_select = True
        return self

    def disable_selection(self) -> typing.Self:
        """Set the can_select flag to False"""
        self.can_select = False
        return self

    def enable_navigation(self) -> typing.Self:
        """Set the can_navigate flag to True. The element will be able to be navigated with the keyboard"""
        self.can_navigate = True
        return self

    def disable_navigation(self) -> typing.Self:
        """Set the can_navigate flag to False. The element won't be able to be navigated with the keyboard"""
        self.can_navigate = False
        if self.element is self.element.ui_manager.navigation.tabbed_element:
            self.element.ui_manager.navigation.stop_navigating()
        return self

    def select(self) -> typing.Self:
        """Manually select the element and update the 'selected' buffer"""
        self.selected = True
        self.element.buffers.update("selected", True)
        return self

    def deselect(self) -> typing.Self:
        """Manually deselect the element and update the 'selected' buffer"""
        self.selected = False
        self.element.buffers.update("selected", False)
        return self
    
    def get_hover_time(self) -> float:
        """Return the time elapsed since the user started hovering the element. If the element is not hovered, return -1"""
        if not self.hovered:
            return -1
        return pygame.time.get_ticks()-self.hover_start_time
    
    def get_press_time(self) -> float:
        """Return the time elapsed since the user started pressing the element. If the element is not pressed, return -1"""
        if not self.pressed:
            return -1
        return pygame.time.get_ticks()-self.press_start_time
    
    def get_right_press_time(self) -> float:
        """Return the time elapsed since the user started right pressing the element. If the element is not right pressed, return -1"""
        if not self.right_pressed:
            return -1
        return pygame.time.get_ticks()-self.right_press_start_time
