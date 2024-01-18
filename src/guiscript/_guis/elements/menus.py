import pygame
import typing

from ..manager import Manager
from .element import Element
from .factories import Button
from .stacks import VStack

from .. import settings as settings_
from .. import common
from .. import events


class DropMenu(Element):
    """An element with a menu that can open and closes with options to choose from"""
    need_event = True

    def __init__(self,
                 options: list[str],
                 start_option: str,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.DropMenuSettings|None = None
                 ):
        if settings is None:
            settings = settings_.DropMenuSettings()
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "menu", "dropmenu"), parent, manager)
        self.deactivate().status.register_callbacks(
            "on_option_select", "on_menu_toggle")
        self.settings: settings_.DropMenuSettings = settings
        self.__done = False
        self.options: list[str] = options
        self.option_button: Button = Button(start_option,
                                            pygame.Rect(0, 0, 0, 0),
                                            self.element_id+"_selected_option",
                                            common.style_id_or_copy(
                                                self, self.settings.inner_buttons_style_id),
                                            False, self, self.manager).status.add_listener("on_click", self._on_arrow_click).element\
            .add_element_types("dropmenu_button", "dropmenu_selected_option").set_attr("builtin", True)
        self.arrow_button: Button = Button(self.settings.down_arrow_txt if self.settings.direction == "down" else self.settings.up_arrow_txt,
                                           pygame.Rect(0, 0, 0, 0),
                                           self.element_id+"_arrow",
                                           common.style_id_or_copy(
                                               self, self.settings.inner_buttons_style_id),
                                           False, self, self.manager).status.add_listener("on_click", self._on_arrow_click).element\
            .add_element_types("dropmenu_button", "dropmenu_arrow").set_attr("builtin", True)
        self.menu_cont: VStack = VStack(pygame.Rect(0, 0, 0, 0),
                                        self.element_id+"_menu",
                                        common.style_id_or_copy(
                                            self, self.settings.menu_style_id),
                                        self.parent if settings.menu_parent is None else settings.menu_parent, self.manager)\
            .set_ignore(stack=True, scroll=True).hide().set_z_index(common.Z_INDEXES["menu"]).add_element_type("dropmenu_menu").set_attr("builtin", True)
        self.__done = True
        self.build()
        self._build_options()
        self.position_changed()

    def set_options(self, options: list[str], selected_option: str) -> typing.Self:
        """Set the options and the selected option"""
        self.options = list(options)
        self.option_button.set_text(selected_option)
        self.build()
        self._build_options()
        return self

    def get_selected(self) -> str:
        """Return the selected option as a string"""
        return self.option_button.text.real_text

    def select(self, option: str) -> typing.Self:
        """Manually set the selected option"""
        self.option_button.set_text(option)
        return self

    def open_menu(self) -> typing.Self:
        """Manually open the options menu"""
        self.menu_cont.show()
        self.arrow_button.set_text(
            self.settings.up_arrow_txt if self.settings.direction == "down" else self.settings.down_arrow_txt)
        return self

    def close_menu(self) -> typing.Self:
        """Manually close the options menu"""
        self.menu_cont.hide()
        self.arrow_button.set_text(
            self.settings.down_arrow_txt if self.settings.direction == "down" else self.settings.up_arrow_txt)
        return self

    def toggle_menu(self) -> typing.Self:
        """Manually toggle the options menu open or close depending on the current state"""
        if self.menu_cont.status.visible:
            self.close_menu()
        else:
            self.open_menu()
        return self
    
    def get_open(self) -> bool:
        """Return whether the drop menu is open or not"""
        return self.menu_cont.status.visible

    def _on_option_click(self, btn: Button):
        self.close_menu()
        self.select(btn.text.real_text)
        self.status.invoke_callback(
            "on_option_select", btn.text.real_text)
        events._post_dropmenu_event("select", self)
        events._post_dropmenu_event("toggle", self)

    def _on_arrow_click(self):
        self.toggle_menu()
        self.status.invoke_callback("on_menu_toggle")
        events._post_dropmenu_event("toggle", self)

    def build(self):
        if not self.manager._running:
            return
        if not self.__done:
            return
        self.arrow_button.set_size(
            (self.relative_rect.w*self.settings.arrow_rel_w, self.relative_rect.h-self.style.stack.padding*2))
        self.option_button.set_size((self.relative_rect.w-self.arrow_button.relative_rect.w -
                                    self.style.stack.padding*2, self.relative_rect.h-self.style.stack.padding*2))
        self.option_button.set_relative_pos(
            (self.style.stack.padding, self.style.stack.padding))
        self.arrow_button.set_relative_pos(
            (self.option_button.relative_rect.w, self.style.stack.padding))
        self.menu_cont.set_size(
            (self.relative_rect.w-self.style.stack.padding*2, 1))
        
    def _build_options(self):
        self.menu_cont.destroy_children()
        self.menu_cont._done = False
        for i, opt in enumerate(self.options):
            Button(opt, pygame.Rect(0, 0, 0, self.settings.option_height),
                   self.element_id +
                   f"_option_{i}", common.style_id_or_copy(
                self.menu_cont, self.settings.option_style_id),
                False, self.menu_cont, self.manager).status.add_listener("on_click", self._on_option_click).element.add_element_type("dropmenu_option").set_attr("builtin", True)
        self.menu_cont._done = True
        self.menu_cont._refresh_stack()

    def on_logic(self):
        if self.settings.direction == "down":
            self.menu_cont.set_absolute_pos(
                (self.absolute_rect.x+self.style.stack.padding, self.absolute_rect.bottom+self.style.stack.spacing+self.parent.scroll_offset.y))
        else:
            self.menu_cont.set_absolute_pos((self.absolute_rect.x+self.style.stack.padding,
                                            self.absolute_rect.top-self.menu_cont.absolute_rect.h-self.style.stack.spacing+self.parent.scroll_offset.y))

    def on_event(self, event: pygame.Event):
        if not self.settings.close_when_click_outside or not self.get_open():
            return
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.menu_cont.absolute_rect.collidepoint(event.pos) and not self.absolute_rect.collidepoint(event.pos):
                self.close_menu()

class SelectionList(VStack):
    """An element with options the user can select or deselect"""

    def __init__(self,
                 options: list[str],
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.SelectionListSettings|None = None
                 ):
        if settings is None:
            settings = settings_.SelectionListSettings()
        super().__init__(relative_rect, element_id, style_id, parent, manager)
        self.settings: settings_.SelectionListSettings = settings
        self.set_options(options)
        self.add_element_types("menu", "selectionlist").deactivate(
        ).status.register_callbacks("on_option_select", "on_option_deselect")

    def set_selected(self, option: str) -> typing.Self:
        """Manually select one option"""
        for btn in self.option_buttons:
            if btn.text.text == option:
                btn.status.select()
            else:
                btn.status.deselect()
        return self

    def set_multi_selected(self, options: list[str]) -> typing.Self:
        """Manually select options from a list of strings"""
        for btn in self.option_buttons:
            if btn.text.text in options:
                btn.status.select()
            else:
                btn.status.deselect()
        return self

    def get_selected(self) -> str | list[str]:
        """Return the selected option or options depending on the settings's 'multi_select' flag"""
        selected = []
        for btn in self.option_buttons:
            if btn.status.selected:
                if self.settings.multi_select:
                    selected.append(btn.text.real_text)
                else:
                    return btn.text.real_text
        return selected if self.settings.multi_select else None

    def set_options(self, options: list[str]) -> typing.Self:
        """Set the options and rebuild the element"""
        self.options: list[str] = list(options)
        self.option_buttons: list[Button] = []
        self._build_options()
        return self

    def _on_option_select(self, btn: Button):
        if not self.settings.multi_select:
            for opt in self.option_buttons:
                if opt.text.text != btn.text.text:
                    opt.status.deselect()
        self.status.invoke_callback("on_option_select", btn.text.text)
        events._post_selectionlist_event("select", self, btn.text.text)

    def _on_option_deselect(self, btn: Button):
        self.status.invoke_callback("on_option_deselect", btn.text.text)
        events._post_selectionlist_event("deselect", self, btn.text.text)

    def _build_options(self):
        self.destroy_children()
        self._done = False
        for i, option in enumerate(self.options):
            btn = Button(option, pygame.Rect(0, 0, 0, self.settings.option_height),
                         self.element_id +
                         f"_option_{i}", common.style_id_or_copy(
                             self, self.settings.option_style_id),
                         True, self, self.manager).add_element_types("selectionlist_option").\
                status.add_multi_listeners(
                    on_select=self._on_option_select, on_deselect=self._on_option_deselect).element.set_attr("builtin", True)
            self.option_buttons.append(btn)
        self._done = True
        self._refresh_stack()
