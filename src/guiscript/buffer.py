import typing
from . import common
if typing.TYPE_CHECKING:
    from .elements.element import UIElement


class UIBuffer[T]:
    """Buffer objects used to sync some properties of elements like the selected status. The on_change call back will be called passing (value, element, name, specific_name) arguments"""

    def __init__(self, value: T, on_change: common.StatusCallback = None, specific_name: str = "UnnamedBuffer"):
        self.value: T = value
        self.on_change: common.StatusCallback = on_change
        self.name: str = specific_name
        self.specific_name: str = specific_name

    def update(self, value: T, element: "UIElement" = None) -> typing.Self:
        """Update the buffer's value and call the on_change callback"""
        if value == self.value:
            return self
        self.value = value
        if self.on_change:
            self.on_change(self.value, element, self.name, self.specific_name)
        return self


class UIBuffers:
    """Keeps bound buffers of an element"""

    def __init__(self, element: "UIElement"):
        self.element: "UIElement" = element
        self.buffers: dict[str, UIBuffer] = {}

    def bind(self, name: str, buffer: UIBuffer, idk) -> typing.Self:
        """Bind a buffer object to a name. The element will sync the buffer value"""
        self.buffers[name] = buffer
        buffer.name = name
        return self

    def get(self, name: str) -> UIBuffer:
        """Return the buffer object bound to a name"""
        return self.buffers.get(name, None)

    def update(self, name: str, value) -> typing.Self:
        """Update a buffer object's value if it exists"""
        if not name in self.buffers:
            return self
        self.buffers[name].update(value, self.element)
        return self
