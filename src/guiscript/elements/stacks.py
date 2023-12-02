import pygame

from .element import UIElement
from ..manager import UIManager
from .scrollbars import UIVScrollbar, UIHScrollbar
from ..state import UIState


class HStack(UIElement):
    """Organize children horizontally using stack style settings"""

    def __init__(self,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 scrollbars_style_id: str = "copy"
                 ):
        self.__done = False
        super().__init__(relative_rect, element_id, style_id, ("element", "stack", "hstack"), parent,
                         ui_manager)
        self.scroll_w: int = 1
        self.scroll_h: int = 1
        self.vscrollbar: UIVScrollbar = UIVScrollbar(self, scrollbars_style_id)
        self.hscrollbar: UIHScrollbar = UIHScrollbar(self, scrollbars_style_id)
        self.__done = True
        self.deactivate()
        
    def is_stack(self) -> bool:
        return True

    def refresh_stack(self):
        if not self.ui_manager.running or not self.__done:
            return
        style = self.style
        total_x = style.stack.padding
        total_y = 0

        active_children_num = 0
        children_with_fill_x: list[UIElement] = []
        for i, child in enumerate(self.children):
            if child.ignore_stack or not child.visible:
                continue

            if child.relative_rect.h > total_y and not child.style.stack.fill_y:
                total_y = child.relative_rect.h
            if child.style.stack.fill_x:
                active_children_num += 1
                children_with_fill_x.append(child)
                continue
            if i > 0:
                total_x += style.stack.spacing
            total_x += child.relative_rect.w
            active_children_num += 1

        total_x += style.stack.padding

        if len(children_with_fill_x) > 0:
            space_available = self.relative_rect.w-total_x
            total_x = self.relative_rect.w
            space_available -= style.stack.spacing * \
                (len(children_with_fill_x)-1)
            space_for_each_child = space_available/len(children_with_fill_x)
            for child in children_with_fill_x:
                child.set_size((space_for_each_child, child.relative_rect.h))

        total_y += style.stack.padding * 2

        if (total_y < self.relative_rect.h and style.stack.shrink_y) or \
                (total_y > self.relative_rect.h and style.stack.grow_y):
            self.set_size((self.relative_rect.w, total_y))

        v_bar_needed = self.vscrollbar.is_needed(
            total_y, style.stack.scroll_y, style.stack.grow_y)
        scroll_x = 0
        if v_bar_needed:
            scroll_x = style.stack.scrollbar_size

        spacing = style.stack.spacing
        if style.stack.anchor == "max_spacing":
            if total_x < self.relative_rect.w-scroll_x:
                remaining = self.relative_rect.w-scroll_x-total_x
                total_x = self.relative_rect.w-scroll_x
                spacing = remaining/(max(active_children_num-1, 1)) + \
                    style.stack.padding/(max(active_children_num-1, 1))

        self.hscrollbar.update_size_position(
            total_x-style.stack.spacing, style.stack.scrollbar_size, style.stack.scroll_x, scroll_x, style.stack.grow_x)
        scroll_y = style.stack.scrollbar_size if self.hscrollbar.visible else 0
        self.vscrollbar.update_size_position(
            total_y-style.stack.spacing, style.stack.scrollbar_size, style.stack.scroll_y, scroll_y, style.stack.grow_y)

        self.scroll_w = total_x-scroll_x
        self.scroll_h = total_y-scroll_y

        current_x = style.stack.padding
        if total_x < (self.relative_rect.w-scroll_x):
            if style.stack.shrink_x:
                self.set_size((total_x, self.relative_rect.h))
            else:
                match style.stack.anchor:
                    case "center":
                        current_x = (self.relative_rect.w -
                                     scroll_x)//2-total_x//2
                    case "right":
                        current_x = (self.relative_rect.w-scroll_x)-total_x
        elif total_x > self.relative_rect.w and style.stack.grow_x:
            self.set_size((total_x, self.relative_rect.h))

        i_o = 0
        for i, child in enumerate(self.children):
            if child.ignore_stack or not child.visible:
                i_o += 1
                continue
            if i > i_o:
                current_x += spacing
            child_y = style.stack.padding
            if not child.style.stack.fill_y:
                if child.relative_rect.h < (self.relative_rect.h-scroll_y):
                    match child.style.stack.align:
                        case "center":
                            child_y = (self.relative_rect.h-scroll_y)//2 - \
                                child.relative_rect.h//2
                        case "bottom":
                            child_y = (self.relative_rect.h-scroll_y) - \
                                child.relative_rect.h-style.stack.padding
            else:
                child.set_size(
                    (child.relative_rect.w, self.relative_rect.h-style.stack.padding*2))
            child.set_relative_pos((current_x, child_y))
            current_x += child.relative_rect.w


class VStack(UIElement):
    """Organize children vertically using stack style settings"""

    def __init__(self,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 scrollbars_style_id: str = "copy"
                 ):
        self.__done = False
        super().__init__(relative_rect, element_id, style_id, ("element", "stack", "vstack"), parent,
                         ui_manager)
        self.scroll_w: int = 1
        self.scroll_h: int = 1
        self.vscrollbar: UIVScrollbar = UIVScrollbar(self, scrollbars_style_id)
        self.hscrollbar: UIHScrollbar = UIHScrollbar(self, scrollbars_style_id)
        self.__done = True
        self.deactivate()
        
    def is_stack(self) -> bool:
        return True

    def refresh_stack(self):
        if not self.ui_manager.running or not self.__done:
            return
        style = self.style
        total_x = 0
        total_y = style.stack.padding

        active_children_num = 0
        children_with_fill_y: list[UIElement] = []
        for i, child in enumerate(self.children):
            if child.ignore_stack or not child.visible:
                continue
            if child.relative_rect.w > total_x and not child.style.stack.fill_x:
                total_x = child.relative_rect.w
            if child.style.stack.fill_y:
                active_children_num += 1
                children_with_fill_y.append(child)
                continue
            if i > 0:
                total_y += style.stack.spacing
            total_y += child.relative_rect.h
            active_children_num += 1

        total_y += style.stack.padding

        if len(children_with_fill_y) > 0:
            space_available = self.relative_rect.h-total_y
            total_y = self.relative_rect.h
            space_available -= style.stack.spacing * \
                (len(children_with_fill_y)-1)
            space_for_each_child = space_available/len(children_with_fill_y)
            for child in children_with_fill_y:
                child.set_size((child.relative_rect.w, space_for_each_child))

        total_x += style.stack.padding * 2

        if (total_x < self.relative_rect.w and style.stack.shrink_x) or \
                (total_x > self.relative_rect.w and style.stack.grow_x):
            self.set_size((total_x, self.relative_rect.h))

        v_bar_needed = self.vscrollbar.is_needed(
            total_y, style.stack.scroll_y, style.stack.grow_y)
        scroll_x = 0
        if v_bar_needed:
            scroll_x = style.stack.scrollbar_size

        self.hscrollbar.update_size_position(
            total_x-style.stack.spacing, style.stack.scrollbar_size, style.stack.scroll_x, scroll_x, style.stack.grow_x)
        scroll_y = style.stack.scrollbar_size if self.hscrollbar.visible else 0
        self.vscrollbar.update_size_position(
            total_y-style.stack.spacing, style.stack.scrollbar_size, style.stack.scroll_y, scroll_y, style.stack.grow_y)

        spacing = style.stack.spacing
        if style.stack.anchor == "max_spacing":
            if total_y < self.relative_rect.h-scroll_y:
                remaining = self.relative_rect.h-scroll_y-total_y
                total_y = self.relative_rect.h-scroll_y
                spacing = remaining/(max(active_children_num-1, 1)) + \
                    style.stack.padding/(max(active_children_num-1, 1))

        self.scroll_w = total_x-scroll_x
        self.scroll_h = total_y-scroll_y

        current_y = 0
        if total_y < (self.relative_rect.h-scroll_y):
            if style.stack.shrink_y:
                self.set_size((self.relative_rect.w, total_y))
            else:
                match style.stack.anchor:
                    case "center":
                        current_y = (self.relative_rect.h -
                                     scroll_y)//2-total_y//2
                    case "bottom":
                        current_y = (self.relative_rect.h-scroll_y)-total_y
        elif total_y > self.relative_rect.h and style.stack.grow_y:
            self.set_size((self.relative_rect.w, total_y))
        current_y += style.stack.padding

        i_o = 0
        for i, child in enumerate(self.children):
            if child.ignore_stack or not child.visible:
                i_o += 1
                continue
            if i > i_o:
                current_y += spacing
            child_x = style.stack.padding
            if not child.style.stack.fill_x:
                if child.relative_rect.w < (self.relative_rect.w-scroll_x):
                    match child.style.stack.align:
                        case "center":
                            child_x = (self.relative_rect.w-scroll_x)//2 - \
                                child.relative_rect.w//2
                        case "right":
                            child_x = (self.relative_rect.w-scroll_x) - \
                                child.relative_rect.w-style.stack.padding
            else:
                child.set_size(
                    (self.relative_rect.w-style.stack.padding*2, child.relative_rect.h))
            child.set_relative_pos((child_x, current_y))
            current_y += child.relative_rect.h
