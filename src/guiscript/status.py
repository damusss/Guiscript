import typing
from . import common
if typing.TYPE_CHECKING:
    from .elements.element import UIElement


class UIStatus:
    def __init__(self, element: "UIElement"):
        self.element: "UIElement" = element
        self.hovered: bool = False
        self.pressed: bool = False
        self.right_pressed: bool = False
        
        self.inactive_hovered: bool = False
        self.inactive_pressed: bool = False
        self.inactive_right_pressed: bool = False
        
        self.selected: bool = False
        self.scroll_hovered: bool = False
        
        self.can_select: bool = False
        self.can_navigate: bool = True

        self.callbacks: dict[str, list[common.StatusCallback]] = {}
        self.register_callbacks(*common.DEFAULT_CALLBACKS)

    def register_callback(self, name: str, start_listeners: list[common.StatusCallback] = None) -> typing.Self:
        if start_listeners is None:
            start_listeners = []
        self.callbacks[name] = start_listeners
        return self

    def register_callbacks(self, *names: str) -> typing.Self:
        for name in names:
            self.register_callback(name)
        return self

    def add_listener(self, callback_name: str, callback: common.StatusCallback) -> typing.Self:
        if not callback_name in self.callbacks:
            self.register_callback(callback_name, [callback])
            return self
        self.callbacks[callback_name].append(callback)
        return self

    def add_listeners(self, callback_name: str, *callbacks: common.StatusCallback) -> typing.Self:
        for callback in callbacks:
            self.add_listener(callback_name, callback)
        return self

    def invoke_callback(self, name: str, *args) -> typing.Self:
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
        for name in names:
            self.invoke_callback(name)
        return self

    def enable_selection(self) -> typing.Self:
        self.can_select = True
        return self

    def disable_selection(self) -> typing.Self:
        self.can_select = False
        return self
    
    def enable_navigation(self) -> typing.Self:
        self.can_navigate = True
        return self

    def disable_navigation(self) -> typing.Self:
        self.can_navigate = False
        if self.element is self.element.ui_manager.navigation.tabbed_element:
            self.element.ui_manager.navigation.stop_navigating()
        return self

    def select(self) -> typing.Self:
        self.selected = True
        self.element.buffers.update("selected", True)
        return self

    def deselect(self) -> typing.Self:
        self.selected = False
        self.element.buffers.update("selected", False)
        return self
