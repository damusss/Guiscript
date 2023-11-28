import pygame
import typing
if typing.TYPE_CHECKING:
    from .manager import UIManager

from .state import UIState
from .elements.element import UIElement
from .events import _post_base_event
from . import common
from . import events


class UIInteract:
    """Update the status of the elements bound to a UIManager"""

    def __init__(self, ui_manager: "UIManager"):
        pygame.scrap.init()
        self.ui_manager: "UIManager" = ui_manager

        self.hovered_el: UIElement = None
        self.pressed_el: UIElement = None
        self.right_pressed_el: UIElement = None

        self.start_idxs: list[int] = None
        self.last_idxs: list[int] = None
        self.text_select_el: UIElement = None

    def logic(self):
        """[Internal] Main update function called by the UIManager"""
        if self.ui_manager.last_rendered is None:
            return

        # text selection
        if self.text_select_el is not None and self.start_idxs is not None:
            lines = common.text_wrap_str(self.text_select_el.text.get_active_text(
            ), self.text_select_el.relative_rect.w, self.text_select_el.style.text.font)
            if UIState.mouse_pressed[0]:
                end_idxs_info = common.text_click_idx(lines, self.text_select_el.style.text.font, UIState.mouse_pos, self.text_select_el.text.text_rect,
                                                      pygame.Vector2(self.text_select_el.absolute_rect.topleft))
                if end_idxs_info is not None:
                    char_i, line_i, tot_i, raw_text = end_idxs_info
                    self.last_idxs = [char_i, line_i, tot_i]

            if self.last_idxs is not None:
                select_rects = common.text_select_rects(self.start_idxs[1], self.start_idxs[0], self.last_idxs[1], self.last_idxs[0],
                                                        lines, self.text_select_el.style.text.font, self.text_select_el.text.text_rect, UIState.mouse_rel.length() != 0)
                if select_rects:
                    self.text_select_el.text.selection_rects = select_rects
        # we are pressing something
        if self.pressed_el is not None:
            # fire when_pressed
            self.pressed_el.status.invoke_callback("when_pressed")
            _post_base_event(events.PRESSED, self.pressed_el)
            # update hover
            self.pressed_el.status.hovered = self.pressed_el.absolute_rect.collidepoint(
                UIState.mouse_pos)
            # we are not pressing no more
            if (not UIState.mouse_pressed[0] and not self.pressed_el is self.ui_manager.navigation.tabbed_element) or (self.pressed_el is self.ui_manager.navigation.tabbed_element and not UIState.space_pressed):
                # set pressed
                self.pressed_el.status.pressed = False
                # fire on_stop_press
                self.pressed_el.status.invoke_callbacks(
                    "on_stop_press", "on_click")
                _post_base_event(events.STOP_PRESS, self.pressed_el)
                _post_base_event(events.CLICK, self.pressed_el)
                # update selection
                if self.pressed_el.status.can_select:
                    # toggle selection
                    old_selected = self.pressed_el.status.selected
                    self.pressed_el.status.selected = not self.pressed_el.status.selected
                    # fire on_select/on_deselect
                    if old_selected:
                        self.pressed_el.status.invoke_callback("on_deselect")
                        self.pressed_el.buffers.update("selected", False)
                        _post_base_event(events.DESELECT, self.pressed_el)
                    else:
                        self.pressed_el.status.invoke_callback("on_select")
                        self.pressed_el.buffers.update("selected", True)
                        _post_base_event(events.SELECT, self.pressed_el)
                    
                # remove pressed el
                self.pressed_el = None
        # we are pressing with right
        elif self.right_pressed_el is not None:
            # fire when_right_pressed
            self.right_pressed_el.status.invoke_callback("when_right_pressed")
            _post_base_event(events.RIGHT_PRESSED, self.right_pressed_el)
            # update hover
            self.right_pressed_el.status.hovered = self.right_pressed_el.absolute_rect.collidepoint(
                UIState.mouse_pos)
            # we aint pressing
            if not UIState.mouse_pressed[1]:
                # set not right pressed and remove right pressed el
                self.right_pressed_el.status.right_pressed = False
                # fire on_stop_right_press
                self.right_pressed_el.status.invoke_callbacks(
                    "on_stop_right_press", "on_right_click")
                _post_base_event(events.STOP_RIGHT_PRESS,
                                 self.right_pressed_el)
                _post_base_event(events.RIGHT_CLICK, self.right_pressed_el)
                self.right_pressed_el = None
        else:
            # we aint pressing anything
            last_rendered = self.ui_manager.last_rendered
            # we have something already hovered
            if self.hovered_el is not None:
                # remove hover status, and raycast again
                self.hovered_el.status.hovered = False
                old = self.hovered_el
                self.hovered_el = self.raycast(
                    UIState.mouse_pos, last_rendered.parent if last_rendered else None, True)
                # if we changed hover, fire on_stop_hover
                if old is not self.hovered_el:
                    old.status.invoke_callback("on_stop_hover")
                    _post_base_event(events.STOP_HOVER, old)
                else:
                    self.hovered_el.status.hovered = True
            else:
                # we didnt have something hovered so just raycast
                self.hovered_el = self.raycast(
                    UIState.mouse_pos, last_rendered.parent if last_rendered else None, True)
            # we are actually hovering something
            if self.hovered_el is not None:
                # TODO: set scroll hover
                # if was not hovered set hovered and fire on_start_hover
                if not self.hovered_el.status.hovered:
                    self.hovered_el.status.hovered = True
                    self.hovered_el.status.invoke_callback("on_start_hover")
                    self.hovered_el.status.hover_start_time = pygame.time.get_ticks()
                    _post_base_event(events.START_HOVER, self.hovered_el)
                # fire when_hovered
                self.hovered_el.status.invoke_callback("when_hovered")
                _post_base_event(events.HOVERED, self.hovered_el)
                # we start pressing left
                if UIState.mouse_pressed[0] or (UIState.space_pressed and self.ui_manager.navigation.tabbed_element is self.hovered_el):
                    if not self.hovered_el.status.pressed:
                        # fire on_start_press
                        self.hovered_el.status.pressed = True
                        self.hovered_el.status.invoke_callback(
                            "on_start_press")
                        self.hovered_el.status.press_start_time = pygame.time.get_ticks()
                        _post_base_event(events.START_PRESS, self.hovered_el)
                        # set pressed and set pressed el
                        self.pressed_el = self.hovered_el
                        self.text_select_start_press(self.pressed_el)
                # we start pressing right
                elif UIState.mouse_pressed[1]:
                    if not self.hovered_el.status.right_pressed:
                        # fire on_start_right_press
                        self.hovered_el.status.right_pressed = True
                        self.hovered_el.status.invoke_callback(
                            "on_start_right_press")
                        self.hovered_el.status.right_press_start_time = pygame.time.get_ticks()
                        _post_base_event(
                            events.START_RIGHT_PRESS, self.hovered_el)
                        # set right pressed and set right pressed el
                        self.right_pressed_el = self.hovered_el

    def raycast(self, position: common.Coordinate, start_parent: UIElement, can_recurse_above=False) -> UIElement | None:
        """Find the hovered element at a certain position. Extra arguments are used for recursion. Keyboard navigated elements have priority"""
        if self.ui_manager.navigation.tabbed_element is not None:
            return self.ui_manager.navigation.tabbed_element
        if start_parent is None or not start_parent.visible:
            return
        if (not start_parent.absolute_rect.collidepoint(position) or start_parent.ignore_raycast) and can_recurse_above:
            return self.raycast(position, start_parent.parent, True)

        for rev_child in reversed(sorted(start_parent.children, key=lambda el: el.z_index)):
            if not rev_child.absolute_rect.collidepoint(position) or not rev_child.visible or rev_child.ignore_raycast:
                continue
            if len(rev_child.children) > 0:
                res = self.raycast(position, rev_child)
                if res and res.visible:
                    return res
            return rev_child
        
        if can_recurse_above:
            return self.raycast(position, start_parent.parent, True)

    def event(self, event: pygame.Event):
        """[Internal] Manage copy events for selected text"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and event.mod == pygame.KMOD_LCTRL:
                if self.text_select_el is not None and self.start_idxs is not None and self.last_idxs is not None:
                    lines = common.text_wrap_str(self.text_select_el.text.get_active_text(),
                                                 self.text_select_el.relative_rect.w, self.text_select_el.style.text.font)
                    common.text_select_copy(
                        self.start_idxs[1], self.start_idxs[0], self.last_idxs[1], self.last_idxs[0], lines)

    def text_select_start_press(self, element: UIElement):
        """[Internal] Start selecting text on an element"""
        if not element.text.can_select:
            return
        if not (txt := element.text.get_active_text()):
            return
        if self.text_select_el is not None:
            self.text_select_el.text.selection_rects = []
        self.text_select_el = None
        lines = common.text_wrap_str(
            txt, element.relative_rect.w, element.style.text.font)
        idxs_info = common.text_click_idx(lines, element.style.text.font, UIState.mouse_pos, element.text.text_rect,
                                          pygame.Vector2(element.absolute_rect.topleft))
        if idxs_info is None:
            return
        char_i, line_i, tot_i, raw_text = idxs_info
        self.text_select_el = element
        self.start_idxs = [char_i, line_i, tot_i]
