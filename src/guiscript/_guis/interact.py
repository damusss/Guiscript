import pygame
import typing
if typing.TYPE_CHECKING:
    from .manager import Manager

from .state import UIState
from .elements.element import Element
from . import events
from . import common
from . import events


class UIInteract:
    """Update the status of the elements bound to a Manager"""

    def __init__(self, manager: "Manager"):
        self.manager: "Manager" = manager

        self._hovered_el: Element = None
        self._pressed_el: Element = None
        self._right_pressed_el: Element = None
        self._last_scroll_hovered: Element = None

        self._start_idxs: list[int] = None
        self._last_idxs: list[int] = None
        self._text_select_el: Element = None
        
        self.click_sound: pygame.mixer.Sound|None = None
        self.immediate_click_sound: pygame.mixer.Sound|None = None
        self.hover_sound: pygame.mixer.Sound|None = None
        self.leave_hover_sound: pygame.mixer.Sound|None = None
        
    def set_sounds(self,
                click_sound: pygame.mixer.Sound|None = None,
                immediate_click_sound: pygame.mixer.Sound|None = None,
                hover_sound: pygame.mixer.Sound|None = None,
                leave_hover_sound: pygame.mixer.Sound|None = None) -> typing.Self:
        """Set the interaction sounds. Element with custom sounds will override the specified ones"""
        self.click_sound = click_sound
        self.immediate_click_sound = immediate_click_sound
        self.hover_sound = hover_sound
        self.leave_hover_sound = leave_hover_sound
        return self

    def _logic(self):
        if self.manager._last_rendered is None:
            return

        # TEXT SELECTION
        if self._text_select_el is not None and self._start_idxs is not None:
            lines = common.text_wrap_str(self._text_select_el.text.real_text, self._text_select_el.relative_rect.w, self._text_select_el.style.text.font)
            
            if UIState.mouse_pressed[0]:
                end_idxs_info = common.text_click_idx(lines, self._text_select_el.style.text.font, UIState.mouse_pos, self._text_select_el.text.text_rect,
                                                      pygame.Vector2(self._text_select_el.absolute_rect.topleft))
                if end_idxs_info is not None:
                    char_i, line_i, tot_i, raw_text = end_idxs_info
                    self._last_idxs = [char_i, line_i, tot_i]
                    if self._text_select_el.text._selection_end_idxs != self._last_idxs:
                        self._text_select_el.text._selection_end_idxs = self._last_idxs
                        self._text_select_el.status.invoke_callback("on_text_selection_change")

            if self._last_idxs is not None:
                select_rects = common.text_select_rects(self._start_idxs[1], self._start_idxs[0], self._last_idxs[1], self._last_idxs[0],
                                                        lines, self._text_select_el.style.text.font, self._text_select_el.text.text_rect, UIState.mouse_rel.length() != 0)
                if UIState.mouse_pressed[0]:
                    if self._last_idxs[-2] > self._start_idxs[-2] or self._last_idxs[-3] > self._start_idxs[-3]:
                        self._text_select_el.text.set_cursor_index(self._last_idxs[-3]+1, self._last_idxs[-2])
                    else:
                        self._text_select_el.text.set_cursor_index(self._last_idxs[-3], self._last_idxs[-2])
                if select_rects:
                    if select_rects != self._text_select_el.text.selection_rects:
                        self._text_select_el.text.selection_rects = select_rects
                        self._text_select_el.set_dirty()
                        self._text_select_el.status.invoke_callback("on_text_selection_change")

        # LEFT PRESSING
        if self._pressed_el is not None:
            self._pressed_el.status.invoke_callback("when_pressed")
            events._post_base_event(events.PRESSED, self._pressed_el)
            self._pressed_el.status.hovered = self._pressed_el.absolute_rect.collidepoint(UIState.mouse_pos)
            
            # stop pressing
            if (not UIState.mouse_pressed[0] and not self._pressed_el is self.manager.navigation.tabbed_element) \
                or (self._pressed_el is self.manager.navigation.tabbed_element and not UIState.space_pressed):
                self._pressed_el.status.pressed = False
                self._pressed_el.status.invoke_callbacks(
                    "on_stop_press", "on_click")
                events._post_base_event(events.STOP_PRESS, self._pressed_el)
                events._post_base_event(events.CLICK, self._pressed_el)
                self._pressed_el.sounds.play("click")
                
                # selection
                if self._pressed_el.status.can_select:
                    old_selected = self._pressed_el.status.selected
                    self._pressed_el.status.selected = not self._pressed_el.status.selected
                    
                    if old_selected:
                        self._pressed_el.status.invoke_callback("on_deselect")
                        self._pressed_el.buffers.update("selected", False)
                        events._post_base_event(events.DESELECT, self._pressed_el)
                    else:
                        self._pressed_el.status.invoke_callback("on_select")
                        self._pressed_el.buffers.update("selected", True)
                        events._post_base_event(events.SELECT, self._pressed_el)

                self._pressed_el = None
                
        # RIGHT PRESSING
        elif self._right_pressed_el is not None:
            self._right_pressed_el.status.invoke_callback("when_right_pressed")
            events._post_base_event(events.RIGHT_PRESSED, self._right_pressed_el)
            self._right_pressed_el.status.hovered = self._right_pressed_el.absolute_rect.collidepoint(UIState.mouse_pos)
            
            # stop pressing
            if not UIState.mouse_pressed[1]:
                self._right_pressed_el.status.right_pressed = False
                self._right_pressed_el.status.invoke_callbacks(
                    "on_stop_right_press", "on_right_click")
                events._post_base_event(events.STOP_RIGHT_PRESS, self._right_pressed_el)
                events._post_base_event(events.RIGHT_CLICK, self._right_pressed_el)
                self._right_pressed_el = None
                
        # NOT PRESSING
        else:
            last_rendered = self.manager._last_rendered
            if self._hovered_el is not None:
                self._hovered_el.status.hovered = False
                old = self._hovered_el
                self._hovered_el = self.raycast(UIState.mouse_pos, last_rendered.parent if last_rendered else None, True)
                
                if old is not self._hovered_el:
                    old.status.invoke_callback("on_stop_hover")
                    events._post_base_event(events.STOP_HOVER, old)
                    old.sounds.play("leave_hover")
                    
                    if self._last_scroll_hovered is not None:
                        self._last_scroll_hovered.status.scroll_hovered = False
                        self._last_scroll_hovered = None
                else:
                    self._hovered_el.status.hovered = True
            else:
                self._hovered_el = self.raycast(UIState.mouse_pos, last_rendered.parent if last_rendered else None, True)
            # HOVERING
            if self._hovered_el is not None:
                # start hover
                if not self._hovered_el.status.hovered:
                    self._hovered_el.status.hovered = True
                    self._hovered_el.status.invoke_callback("on_start_hover")
                    self._hovered_el.sounds.play("hover")
                    self._hovered_el.status.hover_start_time = pygame.time.get_ticks()
                    events._post_base_event(events.START_HOVER, self._hovered_el)
                    self._find_scroll_hovered(self._hovered_el)
                    
                self._hovered_el.status.invoke_callback("when_hovered")
                events._post_base_event(events.HOVERED, self._hovered_el)
                
                # start left press
                if UIState.mouse_pressed[0] or (UIState.space_pressed and self.manager.navigation.tabbed_element is self._hovered_el):
                    if not self._hovered_el.status.pressed:
                        self._hovered_el.status.pressed = True
                        self._hovered_el.status.invoke_callback("on_start_press")
                        self._hovered_el.status.press_start_time = pygame.time.get_ticks()
                        events._post_base_event(events.START_PRESS, self._hovered_el)
                        self._hovered_el.sounds.play("immediate_click")
                        
                        self._pressed_el = self._hovered_el
                        self._text_select_start_press(self._pressed_el)
                        
                # start right press
                elif UIState.mouse_pressed[1]:
                    if not self._hovered_el.status.right_pressed:
                        self._hovered_el.status.right_pressed = True
                        self._hovered_el.status.invoke_callback("on_start_right_press")
                        self._hovered_el.status.right_press_start_time = pygame.time.get_ticks()
                        events._post_base_event(events.START_RIGHT_PRESS, self._hovered_el)
                        self._right_pressed_el = self._hovered_el

        # CURSORS
        if self.manager.cursors.do_override_cursor:
            if self._hovered_el is not None and self._hovered_el.status.active:
                if (rn := self._hovered_el.get_attr("resizer_name")) is not None:
                    if rn in self.manager.cursors.resize_cursors:
                        pygame.mouse.set_cursor(self.manager.cursors.resize_cursors[rn])
                else:
                    pygame.mouse.set_cursor(self.manager.cursors.hover_cursor)
            else:
                pygame.mouse.set_cursor(self.manager.cursors.default_cursor)

    def raycast(self, position: common.Coordinate, start_parent: Element, can_recurse_above=False) -> Element | None:
        """Find the hovered element at a certain position. Extra arguments are used for recursion. Keyboard navigated elements have priority"""
        if self.manager.navigation.tabbed_element is not None:
            return self.manager.navigation.tabbed_element
        if start_parent is None or not start_parent.status.visible:
            return
        if (not start_parent.absolute_rect.collidepoint(position) or start_parent.ignore_raycast) and can_recurse_above:
            return self.raycast(position, start_parent.parent, True)

        for rev_child in reversed(sorted(start_parent.children, key=lambda el: el.z_index)):
            if not rev_child.absolute_rect.collidepoint(position) or not rev_child.status.visible or rev_child.ignore_raycast:
                continue
            if len(rev_child.children) > 0:
                res = self.raycast(position, rev_child)
                if res and res.status.visible:
                    return res
            return rev_child

        if can_recurse_above:
            return self.raycast(position, start_parent.parent, True)

    def _event(self, event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                if self._text_select_el is not None and self._start_idxs is not None and self._last_idxs is not None:
                    lines = common.text_wrap_str(self._text_select_el.text.real_text,
                                                 self._text_select_el.relative_rect.w,
                                                 self._text_select_el.style.text.font)
                    common.text_select_copy(
                        self._start_idxs[1], self._start_idxs[0], self._last_idxs[1], self._last_idxs[0], lines)

    def _find_scroll_hovered(self, element: Element):
        if element.is_stack() and (element.vscrollbar.status.visible or element.hscrollbar.status.visible):
            element.status.scroll_hovered = True
            self._last_scroll_hovered = element
            return
        if element.parent is not None:
            self._find_scroll_hovered(element.parent)

    def _text_select_start_press(self, element: Element):
        if not element.text.can_select:
            return
        if self._text_select_el is not None:
            self._text_select_el.text.selection_rects = []
            self._text_select_el.set_dirty()
        self._text_select_el = None
        if not (txt := element.text.real_text):
            return
        lines = common.text_wrap_str(
            txt, element.relative_rect.w, element.style.text.font)
        idxs_info = common.text_click_idx(lines, element.style.text.font, UIState.mouse_pos, element.text.text_rect,
                                          pygame.Vector2(element.absolute_rect.topleft))
        if idxs_info is None:
            return
        char_i, line_i, tot_i, raw_text = idxs_info
        self._text_select_el = element
        self._start_idxs = [char_i, line_i, tot_i]
        self._text_select_el.text._selection_start_idxs = self._start_idxs
        self._text_select_el.status.invoke_callback("on_text_selection_change")
        
    def get_hovered(self) -> Element:
        """Return the currently hovered element if any"""
        return self._hovered_el
    
    def get_left_pressed(self) -> Element:
        """Return the currently left pressed element if any"""
        return self._pressed_el
    
    def get_right_pressed(self) -> Element:
        """Return the currently right pressed element if any"""
        return self._right_pressed_el
    
    def get_text_selecting(self) -> Element:
        """Return the currently element that has text being selected if any"""
        return self._text_select_el
    
    def any_interacting(self) -> bool:
        """Return whether any element has some interaction from the user. Useful when deciding if the game 'layer' can receive inputs or not"""
        return self._hovered_el is not None or self._pressed_el is not None or self._right_pressed_el is not None
    
    def get_interacting(self) -> Element:
        """Extension of any_interacting, return the element that is being interacted in any way"""
        return self._hovered_el or self._pressed_el or self._right_pressed_el
