import pygame
import typing

from .element import Element
from .stacks import HStack, VStack
from .factories import Button
from ..manager import Manager
from ..state import UIState
from .. import settings as settings_
from .. import common
from .. import events


class ModalContainer(VStack):
    """A helper container that covers all the screen containing a specified element. Default styling will darken the sorrounding and starts hidden"""
    need_event = True

    def __init__(self,
                 modal_element: Element,
                 element_id: str = "none",
                 style_id: str = "",
                 manager: Manager | None = None,
                 settings: settings_.ModalSettings = settings_.ModalDefaultSettings
                 ):
        super().__init__(pygame.Rect(), element_id, style_id, None, manager)
        self.set_size(self.manager.root.relative_rect.size).add_element_type("modal_container").hide()
        if settings.hide_when_clicking_sourroundings:
            self.activate()
        self.settings: settings_.ModalSettings = settings
        self.modal_element: Element = modal_element
        self.modal_element.set_parent(self)

    def on_destroy(self):
        if self.settings.destroy_modal_element_on_destroy:
            self.modal_element.destroy()

    def on_event(self, event: pygame.Event):
        if event.type == pygame.VIDEORESIZE:
            self.set_size((event.w, event.h))
        elif self.settings.hide_when_clicking_sourroundings and event.type == events.CLICK and event.element is self:
            self.hide()


class Window(Element):
    """A floating element with a title bar, a close button and a content container that can be dragged and resized"""

    window_stack: list["Window"] = []

    def __init__(self,
                 relative_rect: pygame.Rect,
                 title: str = "Guiscript Window",
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.WindowSettings = settings_.WindowDefaultSettings,
                 ):
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "window",), parent, manager)
        self.set_ignore(True, True).set_z_index(common.Z_INDEXES["window-start"]+len(
            Window.window_stack)).status.register_callbacks("on_close", "on_collapse").set_drag(True)
        if settings.can_resize:
            self.set_resizers(settings.resizers, settings.resizers_size, settings.min_size,
                              settings.max_size, style_id=settings.resizers_style_id).deactivate()
        self.settings: settings_.WindowSettings = settings
        self.title_bar: HStack = HStack(pygame.Rect(0, 0, 1, 1), self.element_id+"_title_bar",
                                        "invis_cont", self, self.manager).add_element_type("window_title_bar")\
            .set_anchor("parent", "left", "left")\
            .set_anchor("parent", "right", "right")\
            .set_anchor("parent", "top", "top").set_attr("builtin", True)
        self.title: Button = Button(title, pygame.Rect(0, 0, 0, 0), self.element_id+"_title",
                                    common.style_id_or_copy(self, settings.title_style_id), False, self.title_bar, self.manager)\
            .add_element_type("window_title").status.add_multi_listeners(when_pressed=self._on_title_drag, on_stop_press=self._on_title_stop_drag)\
            .element.text.disable_selection().element.set_attr("builtin", True)
        if settings.have_collapse_button:
            if self.settings.min_size[1] > self.settings.title_bar_height+self.style.stack.padding*2:
                self.settings.min_size = (
                    self.settings.min_size[0], self.settings.title_bar_height+self.style.stack.padding*2)
                self.resize_min = self.settings.min_size
            self.collapse_btn: Button | None = Button(settings.collapse_down_txt, pygame.Rect(0, 0, settings.title_bar_height, settings.title_bar_height),
                                                      self.element_id+"_collapse_btn", common.style_id_or_copy(self, settings.collapse_button_style_id), False, self.title_bar, self.manager)\
                .add_element_type("window_collapse_button").status.add_listener("on_click", self._on_collapse_click).element.set_attr("builtin", True)
        else:
            self.collapse_btn: Button | None = None
        if settings.have_close_button:
            self.close_btn: Button | None = Button(settings.close_button_txt, pygame.Rect(0, 0, settings.title_bar_height, settings.title_bar_height),
                                                   self.element_id+"_close_btn", common.style_id_or_copy(self, settings.close_button_style_id), False, self.title_bar, self.manager)\
                .add_element_type("window_close_button").status.add_listener("on_click", self._on_close_click).element.set_attr("builtin", True)
        else:
            self.close_btn: Button | None = None
        self._before_collapse_h: int = self.relative_rect.h
        self.content: VStack = VStack(pygame.Rect(0, 0, 1, 1), self.element_id+"_content", common.style_id_or_copy(self, settings.content_style_id),
                                      self, self.manager, settings.scrollbars_style_id).add_element_type("window_content")\
            .set_anchor("parent", "left", "left")\
            .set_anchor("parent", "right", "right")\
            .set_anchor(self.title_bar, "top", "bottom")\
            .set_anchor("parent", "bottom", "bottom").set_attr("builtin", True)
        Window.window_stack.append(self)
        self.collapsed: bool = False
        self.move_on_top()
        self.build()

    def _on_close_click(self):
        self.status.invoke_callback("on_close")
        events._post_window_event("close", self)
        if self.settings.hide_on_close:
            self.hide()
        if self.settings.destroy_on_close:
            self.destroy()

    def _on_title_drag(self):
        if not self.status.can_drag:
            self.status.dragging = False
            return
        self.move_on_top()
        self.status.dragging = True
        if UIState.mouse_rel.length() <= 0:
            return
        self.set_relative_pos(
            (self.relative_rect.x+UIState.mouse_rel.x, self.relative_rect.y+UIState.mouse_rel.y))
        self.status.invoke_callback("on_drag")
        events._post_window_event("drag", self)

    def _on_collapse_click(self):
        self.collapse()
        self.status.invoke_callback("on_collapse")
        events._post_window_event("collapse", self)

    def _on_title_stop_drag(self):
        self.status.dragging = False

    def collapse(self) -> typing.Self:
        """Toggle the collapse status of the window"""
        if self.collapsed:
            self.set_size((self.relative_rect.w, self._before_collapse_h))
            if self.settings.have_collapse_button:
                self.collapse_btn.text.set_text(
                    self.settings.collapse_down_txt)
            self.collapsed = False
        else:
            self._before_collapse_h = self.relative_rect.h
            self.set_size(
                (self.relative_rect.w, self.settings.title_bar_height+self.style.stack.padding*2))
            if self.settings.have_collapse_button:
                self.collapse_btn.text.set_text(self.settings.collapse_up_txt)
            self.collapsed = True
        return self

    def enter(self) -> VStack:
        """Return the window's content container, a 'prettifying' function when using the context manager"""
        return self.content

    def set_title(self, title: str) -> typing.Self:
        """Shortcut to set the window's title"""
        self.title.text.set_text(title)
        return self

    def get_title(self) -> str:
        """Shortcut to retrieve the window's title"""
        return self.title.text.real_text

    def move_on_top(self) -> typing.Self:
        """Move this window on top of the stack"""
        previous_idx = self.z_index
        new_idx = common.Z_INDEXES["window-start"]+len(Window.window_stack)
        if previous_idx == new_idx:
            return self
        if new_idx > common.Z_INDEXES["window-end"]:
            return self
        self.set_z_index(new_idx)
        for win in Window.window_stack:
            if win is not self and win.z_index > previous_idx:
                win.set_z_index(win.z_index-1)
        return self

    def on_destroy(self):
        if self in Window.window_stack:
            Window.window_stack.remove(self)

    def build(self):
        self.title_bar.set_size(
            (self.relative_rect.w-self.style.stack.padding*2, self.settings.title_bar_height))
        self.title_bar.anchors_padding(self.style.stack.padding)
        self.content.anchors_padding(self.style.stack.padding, "top")
        self.content._anchors["top"].offset = self.style.stack.spacing
