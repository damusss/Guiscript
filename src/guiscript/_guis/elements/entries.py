import pygame
import typing

from ..manager import Manager
from ..state import UIState
from .element import Element
from .stacks import VStack
from .. import events
from .. import settings as settings_


class Textbox(VStack):
    """An element where you can input text on multiple lines"""
    need_event = True

    def __init__(self,
                 relative_rect: pygame.Rect,
                 start_text: str = "",
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.TextboxSettings|None = None
                 ):
        if settings is None:
            settings = settings_.TextboxSettings()
        super().__init__(relative_rect, element_id, style_id, parent, manager)
        self.add_element_type("textbox").status.add_listener("on_click", self._on_self_click)\
            .register_callbacks("on_change", "on_focus", "on_unfocus")
        self.buffers.update("text", start_text)
        self.settings: settings_.TextboxSettings = settings
        
        self._cursor_x: int = 0
        self._cursor_y: int = 0
        self._is_placeholder: bool = True
        self._last_blink: int = 0
        self._action_start_time: int = 0
        self._last_repeat: int = 0
        self._repeat_key: int = None
        self._repeat_func = None
        self._repeat_data = None
        
        self.text_element: Element = Element(pygame.Rect(0,0,0,0),
                                             self.element_id+"_text", settings.inner_style_id+";"+settings.disabled_text_style_id,
                                             ("element", "text", "textbox_text"), self, self.manager)\
                .deactivate().text.set_text(self.settings.placeholder).element.status.enable_selection()\
                .add_multi_listeners(on_select=self._on_inner_select, on_deselect=self._on_inner_deselect, on_text_selection_change=self._selection_changed).element.set_attr("builtin", True)
        self.set_text(start_text)
        
    def _on_self_click(self):
        self.focus()
        self._remove_interaction()
        lines = self._get_lines()
        self._cursor_y = len(lines)-1
        self._cursor_x = len(lines[self._cursor_y])
        self._refresh_cursor_idx()
        self.status.invoke_callback("on_focus")
        events._post_textbox_event("focus", self)
        
    def _selection_changed(self):
        self._cursor_x = self.text_element.text.cursor_x
        self._cursor_y = self.text_element.text.cursor_y
        self._last_blink = pygame.time.get_ticks()
        self.text_element.text._show_cursor = True
        self.text_element.set_dirty()
        
    def on_event(self, event):
        if not self.is_focused():
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.unfocus()
                self.status.invoke_callback("on_unfocus")
                events._post_textbox_event("unfocus", self)
            elif event.key == pygame.K_LEFT:
                self._on_left()
                self._start_repeat(event.key, self._on_left)
            elif event.key == pygame.K_RIGHT:
                self._on_right()
                self._start_repeat(event.key, self._on_right)
            elif event.key == pygame.K_UP:
                self._on_up()
                self._start_repeat(event.key, self._on_up)
            elif event.key == pygame.K_DOWN:
                self._on_down()
                self._start_repeat(event.key, self._on_down)
            elif event.key == pygame.K_BACKSPACE:
                self._on_backspace()
                self._start_repeat(event.key, self._on_backspace)
            elif event.key == pygame.K_DELETE:
                self._on_delete()
                self._start_repeat(event.key, self._on_delete)
            elif event.key == pygame.K_RETURN:
                self._on_enter()
                self._start_repeat(event.key, self._on_enter)
            elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                self._on_unicode(pygame.scrap.get_text())
            elif event.unicode.strip() or event.unicode == " ":
                if event.mod == 0 or event.mod & pygame.KMOD_SHIFT or event.mod & pygame.KMOD_CAPS:
                    self._on_unicode(event.unicode)
                    self._start_repeat(event.key, self._on_unicode, event.unicode)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.absolute_rect.collidepoint(event.pos):
                self.unfocus()
                
    def on_logic(self):
        if UIState.any_pressed or self.manager.interact._text_select_el is self.text_element:
            if self.text_element.text._cursor_draw_pos.x-self.scroll_offset.x >= self.relative_rect.w-self.text_element.style.text.cursor_width:
                self.set_scroll(
                    self.scroll_offset.x+self.text_element.text.text_size("MM")[0], self.scroll_offset.y)
            if self.text_element.text._cursor_draw_pos.x-self.scroll_offset.x <= self.text_element.style.text.cursor_width:
                self.set_scroll(
                    self.scroll_offset.x-self.text_element.text.text_size("MM")[0], self.scroll_offset.y)
        
        if UIState.any_pressed or self.manager.interact._text_select_el is self.text_element:
            if self.text_element.text._cursor_draw_pos.y-self.scroll_offset.y >= self.relative_rect.h-self.text_element.style.text.font.get_height():
                self.set_scroll(self.scroll_offset.x,
                    self.scroll_offset.y+self.text_element.style.text.font.get_height())
            if self.text_element.text._cursor_draw_pos.y-self.scroll_offset.y <= self.text_element.style.text.font.get_height():
                self.set_scroll(self.scroll_offset.x,
                    self.scroll_offset.y-self.text_element.style.text.font.get_height())
        
        if pygame.time.get_ticks()-self._last_blink >= self.settings.blink_speed and self.is_focused():
            self._last_blink = pygame.time.get_ticks()
            if self.text_element.text._show_cursor:
                self.text_element.text._show_cursor = False
            else:
                self.text_element.text._show_cursor = True
            self.text_element.set_dirty()
            
        if not self.is_focused() and self.text_element.text._show_cursor:
            self.text_element.text._show_cursor = False
            self.text_element.set_dirty()

        if self._repeat_key is None:
            return
        if pygame.time.get_ticks() - self._action_start_time >= self.settings.repeat_start_cooldown:
            if pygame.time.get_ticks() - self._last_repeat >= self.settings.repeat_speed:
                if UIState.keys_pressed[self._repeat_key]:
                    if self._repeat_data is not None:
                        self._repeat_func(self._repeat_data)
                    else:
                        self._repeat_func()
                    self._last_repeat = pygame.time.get_ticks()
                else:
                    self._repeat_key = None
                    
    def _start_repeat(self, key, func, data=None):
        self._action_start_time = pygame.time.get_ticks()
        self._last_repeat = pygame.time.get_ticks()
        self._repeat_key, self._repeat_func, self._repeat_data = key, func, data
        
    def _get_lines(self):
        return self.text_element.text.real_text.split("\n")
    
    def _split_on_cursor(self, line):
        return line[:self._cursor_x], line[self._cursor_x:]
    
    def _lines_to_txt(self, lines):
        self.text_element.text.set_text("\n".join(lines))
    
    def _refresh_cursor_idx(self):
        self.text_element.text.set_cursor_index(self._cursor_x, self._cursor_y, True)
        self._last_blink = pygame.time.get_ticks()

    def _remove_interaction(self):
        if self.manager.interact._text_select_el is self.text_element:
            self.manager.interact._text_select_el = None
        self.text_element.text.selection_rects = []
        self.text_element.set_dirty()

    def _on_inner_select(self):
        self.focus()
        self.status.invoke_callback("on_focus")
        events._post_textbox_event("focus", self)

    def _on_inner_deselect(self):
        self.text_element.status.select()
        
    def _remove_selection(self):
        if not self.text_element is self.manager.interact._text_select_el:
            return False
        selection = self.text_element.text._get_selection(True)
        if selection is None:
            self._remove_interaction()
            return False
        
        self._remove_interaction()
        if selection[3] == selection[2]:
            lines = self._get_lines()
            line = lines[selection[2]]
            nline = line[:selection[0]]+line[selection[1]+1:]
            lines[selection[2]] = nline
            self._lines_to_txt(lines)
            self._cursor_x = selection[0]
        else:
            li = selection[2]
            finaltxt = ""
            pa = 0
            while True:
                lines = self._get_lines()
                line = lines[li]
                if li == selection[2]:
                    nl = line[:selection[0]+1]
                    lines[li] = nl
                    li += 1
                    self._lines_to_txt(lines)
                elif li == selection[3]-pa:
                    finaltxt = line[selection[1]:]
                    lines.pop(li)
                    self._lines_to_txt(lines)
                    break
                else:
                    lines.pop(li)
                    self._lines_to_txt(lines)
                    pa += 1
            lines = self._get_lines()
            lines[selection[2]] += finaltxt
            self._cursor_x = selection[0]+1
        self._cursor_y = selection[2]
        self._refresh_cursor_idx()
        self._lines_to_txt(lines)

        self.status.invoke_callback("on_change", self.get_text())
        events._post_textbox_event("change", self)
        self.buffers.update("text", self.get_text())
        return True
        
    # KEYS
    def _on_left(self):
        self._remove_interaction()
        if self._cursor_x > 0:
            self._cursor_x -= 1
        elif self._cursor_y > 0:
            self._cursor_y -= 1
            line = self._get_lines()[self._cursor_y]
            self._cursor_x = len(line)
        self._refresh_cursor_idx()

    def _on_right(self):
        self._remove_interaction()
        lines = self._get_lines()
        if self._cursor_x <= len(lines[self._cursor_y])-1:
            self._cursor_x += 1
        elif self._cursor_y < len(lines)-1:
            self._cursor_y += 1
            self._cursor_x = 0
        self._refresh_cursor_idx()
        
    def _on_up(self):
        self._remove_interaction()
        if self._cursor_y <= 0:
            return
        self._cursor_y -= 1
        line = self._get_lines()[self._cursor_y]
        if self._cursor_x > len(line):
            self._cursor_x = len(line)
        self._refresh_cursor_idx()
        
    def _on_down(self):
        self._remove_interaction()
        lines = self._get_lines()
        if self._cursor_y >= len(lines)-1:
            return
        self._cursor_y += 1
        line = lines[self._cursor_y]
        if self._cursor_x > len(line):
            self._cursor_x = len(line)
        self._refresh_cursor_idx()
        
    def _on_enter(self):
        lines = self._get_lines()
        line = lines[self._cursor_y]
        left, right = self._split_on_cursor(line)
        lines[self._cursor_y] = left
        lines.insert(self._cursor_y+1, right)
        self._lines_to_txt(lines)
        self._cursor_y += 1
        self._cursor_x = 0
        self._refresh_cursor_idx()
        
        self.status.invoke_callback("on_change", self.get_text())
        events._post_textbox_event("change", self)
        self.buffers.update("text", self.get_text())
        
    def _on_backspace(self):
        if self._remove_selection():
            return
        if self._cursor_y <= 0 and self._cursor_x <= 0:
            return
        
        lines = self._get_lines()
        cline = lines[self._cursor_y]
        if self._cursor_x > 0:
            left, right = self._split_on_cursor(cline)
            nline = left[:self._cursor_x-1]+right
            lines[self._cursor_y] = nline
            self._lines_to_txt(lines)
            self._cursor_x -= 1
        else:
            prevline = lines[self._cursor_y-1]
            merged_line = prevline+cline
            lines.pop(self._cursor_y)
            lines[self._cursor_y-1] = merged_line
            self._lines_to_txt(lines)
            self._cursor_y -= 1
            self._cursor_x = len(merged_line)-len(cline)
        self._refresh_cursor_idx()

        self.status.invoke_callback("on_change", self.get_text())
        events._post_textbox_event("change", self)
        self.buffers.update("text", self.get_text())
        
    def _on_delete(self):
        if self._remove_selection():
            return
        
        lines = self._get_lines()
        cline = lines[self._cursor_y]
        if self._cursor_x <= len(cline)-1:
            left, right = self._split_on_cursor(cline)
            nline = left+right[1:]
            lines[self._cursor_y] = nline
            self._lines_to_txt(lines)
        elif self._cursor_y <= len(lines)-1:
            try:
                nextline = lines[self._cursor_y+1]
                merged_line = cline+nextline
                lines.pop(self._cursor_y+1)
                lines[self._cursor_y] = merged_line
                self._lines_to_txt(lines)
            except IndexError:
                pass

        self.status.invoke_callback("on_change", self.get_text())
        events._post_textbox_event("change", self)
        self.buffers.update("text", self.get_text())
        
    def _on_unicode(self, unicode: str):
        self._remove_selection()
        split_add = unicode.split("\n")
        lines = self._get_lines()
        lls, rls = [], []
        for i,l in enumerate(lines):
            if i < self._cursor_y:
                lls.append(l)
            elif i > self._cursor_y:
                rls.append(l)
            else:
                lls.append(l[:self._cursor_x])
                rls.append(l[self._cursor_x:])
        left = "\n".join(lls)
        right = "\n".join(rls)
        ntext = left+unicode+right
        self.text_element.text.set_text(ntext)
        if len(split_add) == 1:
            self._cursor_x += len(split_add[0])
        else:
            self._cursor_y += len(split_add)-1
            self._cursor_x = len(split_add[-1])
        
        self._refresh_cursor_idx()
        self.status.invoke_callback("on_change", self.get_text())
        events._post_textbox_event("change", self)
        self.buffers.update("text", self.get_text())
        
    def unfocus(self) -> typing.Self:
        """Unfocus the entry"""
        self.text_element.status.deselect()
        self.text_element.text.set_cursor_index(-1)
        self._remove_interaction()
        if not self.text_element.text.real_text.strip():
            self._is_placeholder = True
            self.text_element.text.set_text(self.settings.placeholder)
            self.text_element.set_style_id(
                self.text_element.style_id+";"+self.settings.disabled_text_style_id)
        return self

    def focus(self) -> typing.Self:
        """Focus the entry"""
        if self._is_placeholder:
            self.text_element.text.set_text("")
            self._cursor_index = 0
            self._is_placeholder = False
            self.text_element.set_style_id(self.text_element.style_id.replace(
                ";"+self.settings.disabled_text_style_id, ""))
        self.text_element.status.select()
        self._refresh_cursor_idx()
        return self

    def is_focused(self) -> bool:
        """Return whether the entry is focused"""
        return self.text_element.status.selected

    def get_text(self) -> str:
        """Return the text inside the entry"""
        if self._is_placeholder:
            return ""
        return self.text_element.text.real_text

    def set_text(self, text: str) -> typing.Self:
        """Manually set the text of the entry"""
        self.focus()
        self.text_element.text.set_text(text)
        self.unfocus()
        self.buffers.update("text", self.get_text())
        return self
    
    def add_text(self, text: str) -> typing.Self:
        """Manually add text on the cursor position, replacing the selection if necessary"""
        self.focus()
        self._on_unicode(text)
        return self

    def set_cursor_index(self, x: int, y: int) -> typing.Self:
        """Manually set the cursor index of the entry"""
        self._cursor_y = pygame.math.clamp(y, 0, len(self._get_lines())-1)
        self._cursor_x = pygame.math.clamp(x, 0, len(self._get_lines()[self._cursor_y]))
        self._refresh_cursor_idx()
        return self

    def remove_selection(self) -> typing.Self:
        """Manually delete the currently selected text"""
        self._remove_selection()
        return

class Entry(VStack):
    """An element where you can input text on a single line"""
    need_event = True

    def __init__(self,
                 relative_rect: pygame.Rect,
                 start_text: str = "",
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.EntrySettings|None = None
                 ):
        if settings is None:
            settings = settings_.EntrySettings()
        super().__init__(relative_rect, element_id, style_id, parent, manager, "invisible")
        self.vscrollbar.deactivate()
        self.hscrollbar.deactivate()
        self.add_element_type("entry").status.add_listener("on_click", self._on_self_click)\
            .register_callbacks("on_change", "on_focus", "on_unfocus")
        self.buffers.update("text", start_text)
        self.settings: settings_.EntrySettings = settings

        self._cursor_index: int = 0
        self._is_placeholder: bool = True
        self._last_blink: int = 0
        self._action_start_time: int = 0
        self._last_repeat: int = 0
        self._repeat_key: int = None
        self._repeat_func = None
        self._repeat_data = None

        self.text_element: Element = Element(pygame.Rect(0, 0, 0, 0),
                                             self.element_id+"_text", settings.inner_style_id +";"+settings.disabled_text_style_id,
                                             ("element", "text", "entry_text"), self, self.manager)\
            .deactivate().text.set_text(self.settings.placeholder).element.status.enable_selection()\
            .add_multi_listeners(on_select=self._on_inner_select, on_deselect=self._on_inner_deselect, on_text_selection_change=self._selection_changed).element.set_attr("builtin", True)
        self.set_text(start_text)
        
    def _on_self_click(self):
        self.focus()
        self._remove_interaction()
        self._cursor_index = len(self.text_element.text.real_text)
        self._refresh_cursor_idx()
        self.status.invoke_callback("on_focus")
        events._post_entry_event("focus", self)

    def _selection_changed(self):
        self._cursor_index = self.text_element.text.cursor_x
        self._last_blink = pygame.time.get_ticks()
        self.text_element.text._show_cursor = True
        self.text_element.set_dirty()

    def on_event(self, event):
        if not self.is_focused():
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.unfocus()
                self.status.invoke_callback("on_unfocus")
                events._post_entry_event("unfocus", self)
            elif event.key == pygame.K_LEFT:
                self._on_left()
                self._start_repeat(event.key, self._on_left)
            elif event.key == pygame.K_RIGHT:
                self._on_right()
                self._start_repeat(event.key, self._on_right)
            elif event.key == pygame.K_BACKSPACE:
                self._on_backspace()
                self._start_repeat(event.key, self._on_backspace)
            elif event.key == pygame.K_DELETE:
                self._on_delete()
                self._start_repeat(event.key, self._on_delete)
            elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                self._on_unicode(pygame.scrap.get_text())
            elif event.unicode.strip() or event.unicode == " ":
                if event.mod == 0 or event.mod & pygame.KMOD_SHIFT or event.mod & pygame.KMOD_CAPS:
                    self._on_unicode(event.unicode)
                    self._start_repeat(
                        event.key, self._on_unicode, event.unicode)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not self.absolute_rect.collidepoint(event.pos):
                self.unfocus()

    def on_logic(self):
        if UIState.any_pressed or self.manager.interact._text_select_el is self.text_element:
            if self.text_element.text._cursor_draw_pos.x-self.scroll_offset.x >= self.relative_rect.w-self.text_element.style.text.cursor_width:
                self.set_scroll(
                    self.scroll_offset.x+self.text_element.text.text_size("MM")[0], self.scroll_offset.y)
            if self.text_element.text._cursor_draw_pos.x-self.scroll_offset.x <= self.text_element.style.text.cursor_width:
                self.set_scroll(
                    self.scroll_offset.x-self.text_element.text.text_size("MM")[0], self.scroll_offset.y)

        if pygame.time.get_ticks()-self._last_blink >= self.settings.blink_speed and self.is_focused():
            self._last_blink = pygame.time.get_ticks()
            if self.text_element.text._show_cursor:
                self.text_element.text._show_cursor = False
            else:
                self.text_element.text._show_cursor = True
            self.text_element.set_dirty()
            
        if not self.is_focused() and self.text_element.text._show_cursor:
            self.text_element.text._show_cursor = False
            self.text_element.set_dirty()

        if self._repeat_key is None:
            return
        if pygame.time.get_ticks() - self._action_start_time >= self.settings.repeat_start_cooldown:
            if pygame.time.get_ticks() - self._last_repeat >= self.settings.repeat_speed:
                if UIState.keys_pressed[self._repeat_key]:
                    if self._repeat_data is not None:
                        self._repeat_func(self._repeat_data)
                    else:
                        self._repeat_func()
                    self._last_repeat = pygame.time.get_ticks()
                else:
                    self._repeat_key = None

    def _start_repeat(self, key, func, data=None):
        self._action_start_time = pygame.time.get_ticks()
        self._last_repeat = pygame.time.get_ticks()
        self._repeat_key, self._repeat_func, self._repeat_data = key, func, data

    def _on_left(self):
        self._remove_interaction()
        if self._cursor_index > 0:
            self._cursor_index -= 1
        self._refresh_cursor_idx()

    def _on_right(self):
        self._remove_interaction()
        if self._cursor_index < len(self.text_element.text.real_text):
            self._cursor_index += 1
        self._refresh_cursor_idx()

    def _on_backspace(self):
        if self._remove_selection():
            return
        if self._cursor_index <= 0:
            return
        left, right = self._split_on_cursor()
        self.text_element.text.set_text(left[0:-1]+right)
        self._cursor_index -= 1
        self._refresh_cursor_idx()

        self.status.invoke_callback("on_change", self.get_text())
        events._post_entry_event("change", self)
        self.buffers.update("text", self.get_text())

    def _on_delete(self):
        if self._remove_selection():
            return
        if self._cursor_index >= len(self.text_element.text.real_text):
            return
        left, right = self._split_on_cursor()
        self.text_element.text.set_text(left+right[1:])

        self.status.invoke_callback("on_change", self.get_text())
        events._post_entry_event("change", self)
        self.buffers.update("text", self.get_text())

    def _on_unicode(self, unicode: str):
        self._remove_selection()
        left, right = self._split_on_cursor()
        self.text_element.text.set_text(left+unicode+right)
        self._cursor_index += len(unicode)
        self._refresh_cursor_idx()

        self.status.invoke_callback("on_change", self.get_text())
        events._post_entry_event("change", self)
        self.buffers.update("text", self.get_text())

    def _remove_selection(self):
        if not self.text_element is self.manager.interact._text_select_el:
            return False
        selection = self.text_element.text._get_selection()
        if selection is None:
            self._remove_interaction()
            return False
        self._remove_interaction()
        left, right = self.text_element.text.real_text[0:selection[0]
                                                  ], self.text_element.text.real_text[selection[1]+1:]
        self.text_element.text.set_text(left+right)
        self._cursor_index = selection[0]
        self._refresh_cursor_idx()

        self.status.invoke_callback("on_change", self.get_text())
        events._post_entry_event("change", self)
        self.buffers.update("text", self.get_text())
        return True

    def _split_on_cursor(self):
        return self.text_element.text.real_text[0:self._cursor_index], self.text_element.text.real_text[self._cursor_index:]

    def _refresh_cursor_idx(self):
        self.text_element.text.set_cursor_index(self._cursor_index, show=True)
        self._last_blink = pygame.time.get_ticks()

    def _remove_interaction(self):
        if self.manager.interact._text_select_el is self.text_element:
            self.manager.interact._text_select_el = None
        self.text_element.text.selection_rects = []
        self.text_element.set_dirty()

    def _on_inner_select(self):
        self.focus()
        self.status.invoke_callback("on_focus")
        events._post_entry_event("focus", self)

    def _on_inner_deselect(self):
        self.text_element.status.select()

    def unfocus(self) -> typing.Self:
        """Unfocus the entry"""
        self.text_element.status.deselect()
        self.text_element.text.set_cursor_index(-1)
        self._remove_interaction()
        if not self.text_element.text.real_text.strip():
            self._is_placeholder = True
            self.text_element.text.set_text(self.settings.placeholder)
            self.text_element.set_style_id(
                self.text_element.style_id+";"+self.settings.disabled_text_style_id)
        return self

    def focus(self) -> typing.Self:
        """Focus the entry"""
        if self._is_placeholder:
            self.text_element.text.set_text("")
            self._cursor_index = 0
            self._is_placeholder = False
            self.text_element.set_style_id(self.text_element.style_id.replace(
                ";"+self.settings.disabled_text_style_id, ""))
        self.text_element.status.select()
        self._refresh_cursor_idx()
        return self

    def is_focused(self) -> bool:
        """Return whether the entry is focused"""
        return self.text_element.status.selected

    def get_text(self) -> str:
        """Return the text inside the entry"""
        if self._is_placeholder:
            return ""
        return self.text_element.text.real_text

    def set_text(self, text: str) -> typing.Self:
        """Manually set the text of the entry"""
        text = str(text)
        self.focus()
        self.text_element.text.set_text(text.replace("\n", ""))
        self.unfocus()
        self.buffers.update("text", self.get_text())
        return self

    def add_text(self, text: str) -> typing.Self:
        """Manually add text on the cursor position, replacing the selection if necessary"""
        text = str(text)
        self.focus()
        self._on_unicode(text.replace("\n", ""))
        return self

    def set_cursor_index(self, index: int) -> typing.Self:
        """Manually set the cursor index of the entry"""
        self._cursor_index = pygame.math.clamp(
            index, 0, len(self.text_element.text.real_text))
        self._refresh_cursor_idx()
        return self
    
    def move_cursor(self, places: int) -> typing.Self:
        return self.set_cursor_index(self._cursor_index+places)
    
    def delete_at_cursor(self, forward: bool = False) -> typing.Self:
        self._on_delete() if forward else self._on_backspace()
        return self

    def remove_selection(self) -> typing.Self:
        """Manually delete the currently selected text"""
        self._remove_selection()
        return
