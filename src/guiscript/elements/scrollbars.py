import pygame

from .element import UIElement
from ..state import UIState


class UIVScrollbar(UIElement):
    def __init__(self, stack: UIElement):
        super().__init__(pygame.Rect(0, 0, 10, 10), stack.element_id+"_vscrollbar", stack.style_id,
                         ("element", "scrollbar", "vscrollbar"), stack, stack.ui_manager)
        self.set_ignore(True, True)
        self.z_index = 100
        self.handle: UIElement = UIElement(pygame.Rect(
            0, 0, 10, 10), self.element_id+"_handle", self.style_id, ("element", "handle", "scrollbarhandle", "vscrollbarhandle"), self, self.ui_manager)
        self.deactivate()

    def is_needed(self, total_h: int, can_scroll: bool, grow_y: bool) -> bool:
        if not can_scroll or grow_y:
            return False
        else:
            if total_h > self.parent.relative_rect.h:
                return True
            else:
                return False

    def update_size_position(self, total_h: int, size: int, can_scroll: bool, scroll_y: int, grow_y: bool):
        self.set_relative_pos((self.parent.relative_rect.w-size, 0))
        self.set_size((size, self.parent.relative_rect.h), False)
        if not can_scroll or grow_y:
            self.visible = False
        else:
            if total_h > self.parent.relative_rect.h:
                self.visible = True
            else:
                self.visible = False
        handle_size_y = (self.parent.relative_rect.h *
                         (self.parent.relative_rect.h-scroll_y))/total_h
        self.handle.set_size((size, handle_size_y), False)

    def on_logic(self):
        if not self.visible:
            return

        prev_y = self.handle.relative_rect.y

        if self.handle.status.pressed:
            self.handle.set_relative_pos(
                (0, self.handle.relative_rect.y+UIState.mouse_rel[1]))

        if UIState.mouse_wheel and not UIState.keys_pressed[pygame.K_LCTRL]:
            self.handle.set_relative_pos(
                (0, self.handle.relative_rect.y-UIState.mouse_wheel*self.ui_manager.scroll_multiplier))

        if self.handle.relative_rect.y < 0:
            self.handle.set_relative_pos((0, 0))
        elif self.handle.relative_rect.bottom > self.relative_rect.h:
            self.handle.set_relative_pos(
                (0, self.relative_rect.h-self.handle.relative_rect.h))

        if self.handle.relative_rect.y != prev_y:
            self.parent.scroll_offset.y = (
                self.handle.relative_rect.y*self.parent.scroll_h)/self.relative_rect.h
            for child in self.parent.children:
                child.update_absolute_rect_pos()
            self.status.invoke_callback("on_move")


class UIHScrollbar(UIElement):
    def __init__(self, stack: UIElement):
        super().__init__(pygame.Rect(0, 0, 10, 10), stack.element_id+"_hscrollbar",
                         stack.style_id, ("element", "scrollbar", "hscrollbar"), stack, stack.ui_manager)
        self.set_ignore(True, True)
        self.z_index = 100
        self.handle: UIElement = UIElement(pygame.Rect(
            0, 0, 10, 10), self.element_id+"_handle", self.style_id, ("element", "handle", "scrollbarhandle", "hscrollbarhandle"), self, self.ui_manager)
        self.deactivate()

    def is_needed(self, total_w: int, can_scroll: bool, grow_x: bool):
        if not can_scroll or grow_x:
            return False
        else:
            if total_w > self.parent.relative_rect.w:
                return True
            else:
                return False

    def update_size_position(self, total_w: int, size: int, can_scroll: bool, scroll_x: int, grow_x: bool):
        self.set_relative_pos((0, self.parent.relative_rect.h-size))
        self.set_size((self.parent.relative_rect.w-scroll_x, size), False)
        if not can_scroll or grow_x:
            self.visible = False
        else:
            if total_w > self.parent.relative_rect.w:
                self.visible = True
            else:
                self.visible = False
        handle_size_x = (self.parent.relative_rect.w *
                         (self.parent.relative_rect.w-scroll_x*2))/total_w
        self.handle.set_size((handle_size_x, size), False)

    def on_logic(self):
        if not self.visible:
            return

        prev_x = self.handle.relative_rect.x

        if self.handle.status.pressed:
            self.handle.set_relative_pos(
                (self.handle.relative_rect.x+UIState.mouse_rel[0], 0))

        if UIState.mouse_wheel and UIState.keys_pressed[pygame.K_LCTRL]:
            self.handle.set_relative_pos(
                (self.handle.relative_rect.x-UIState.mouse_wheel*self.ui_manager.scroll_multiplier, 0))

        if self.handle.relative_rect.x < 0:
            self.handle.set_relative_pos((0, 0))
        elif self.handle.relative_rect.right > self.relative_rect.w:
            self.handle.set_relative_pos(
                (self.relative_rect.w-self.handle.relative_rect.w, 0))

        if self.handle.relative_rect.x != prev_x:
            self.parent.scroll_offset.x = (
                self.handle.relative_rect.x*self.parent.scroll_w)/self.relative_rect.w
            for child in self.parent.children:
                child.update_absolute_rect_pos()
            self.status.invoke_callback("on_move")
