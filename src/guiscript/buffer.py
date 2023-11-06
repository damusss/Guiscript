import typing
from . import common
if typing.TYPE_CHECKING:
    from .elements.element import UIElement

BufferValueT = typing.TypeVar("BufferValueT")


class UIBuffer(typing.Generic[BufferValueT]):
    def __init__(self, value: BufferValueT, on_change: common.StatusCallback = None, specific_name: str = "UnnamedBuffer"):
        self.value: BufferValueT = value
        self.on_change: common.StatusCallback = on_change
        self.name: str = specific_name
        self.specific_name: str = specific_name

    def update(self, value: BufferValueT, element: "UIElement" = None) -> typing.Self:
        if value == self.value: return self
        self.value = value
        if self.on_change:
            self.on_change(self.value, element, self.name, self.specific_name)
        return self


class UIBuffers:
    def __init__(self, element: "UIElement"):
        self.element: "UIElement" = element
        self.buffers: dict[str, UIBuffer] = {}

    def bind(self, name: str, buffer: UIBuffer) -> typing.Self:
        self.buffers[name] = buffer
        buffer.name = name
        return self

    def get(self, name: str) -> UIBuffer:
        return self.buffers.get(name, None)

    def update(self, name: str, value) -> typing.Self:
        if not name in self.buffers:
            return self
        self.buffers[name].update(value, self.element)
        return self
