import pygame
import typing

from ..manager import UIManager
from .element import UIElement
from .factories import Button
from .stacks import VStack
from .. import settings as settings_
from ..common import style_id_or_copy, Z_INDEXES
from ..events import _post_dropmenu_event, _post_selectionlist_event


class DropMenu(UIElement):
    """An element with a menu that can open and closes with options to choose from"""

    def __init__(self,
                 options: list[str],
                 start_option: str,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 settings: settings_.DropMenuSettings = settings_.DropMenuDefaultSettings,
                 ):
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "menu", "dropmenu"), parent, ui_manager)
        self.deactivate().status.register_callbacks(
            "on_option_select", "on_menu_toggle")
        self.settings: settings_.DropMenuSettings = settings
        self.__done = False
        self.options: list[str] = options
        self.option_button: Button = Button(start_option,
                                            pygame.Rect(0, 0, 0, 0),
                                            self.element_id+"_selected_option",
                                            style_id_or_copy(
                                                self, self.settings.inner_buttons_style_id),
                                            False, self, self.ui_manager).status.add_listener("on_click", self.on_arrow_click).element\
            .add_element_types("dropmenu_button", "dropmenu_selected_option")
        self.arrow_button: Button = Button(self.settings.down_arrow_txt if self.settings.direction == "down" else self.settings.up_arrow_txt,
                                           pygame.Rect(0, 0, 0, 0),
                                           self.element_id+"_arrow",
                                           style_id_or_copy(
                                               self, self.settings.inner_buttons_style_id),
                                           False, self, self.ui_manager).status.add_listener("on_click", self.on_arrow_click).element\
            .add_element_types("dropmenu_button", "dropmenu_arrow")
        self.menu_cont: VStack = VStack(pygame.Rect(0, 0, 0, 0),
                                        self.element_id+"_menu",
                                        style_id_or_copy(
                                            self, self.settings.menu_style_id),
                                        self.parent, self.ui_manager).set_ignore(stack=True).hide().set_z_index(Z_INDEXES["menu"]).add_element_type("dropmenu_menu")
        self.__done = True
        self.build()
        self.position_changed()

    def set_options(self, options: list[str], selected_option: str) -> typing.Self:
        """Set the options and the selected option"""
        self.options = list(options)
        self.option_button.set_text(selected_option)
        self.build()
        return self

    def get_selected(self) -> str:
        """Return the selected option as a string"""
        return self.option_button.text.get_active_text()

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
        if self.menu_cont.visible:
            self.close_menu()
        else:
            self.open_menu()
        return self

    def on_option_click(self, btn: Button):
        """[Internal] Child callback"""
        self.close_menu()
        self.select(btn.text.get_active_text())
        self.status.invoke_callback(
            "on_option_select", btn.text.get_active_text())
        _post_dropmenu_event("select", self)
        _post_dropmenu_event("toggle", self)

    def on_arrow_click(self):
        """[Internal] Child callback"""
        self.toggle_menu()
        self.status.invoke_callback("on_menu_toggle")
        _post_dropmenu_event("toggle", self)

    def build(self):
        if not self.ui_manager.running:
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
        self.menu_cont.destroy_children()
        for i, opt in enumerate(self.options):
            Button(opt, pygame.Rect(0, 0, 0, self.settings.option_height),
                   self.element_id +
                   f"_option_{i}", style_id_or_copy(
                self.menu_cont, self.settings.option_style_id),
                False, self.menu_cont, self.ui_manager).status.add_listener("on_click", self.on_option_click).element.add_element_type("dropmenu_option")
        self.menu_cont.refresh_stack()

    def position_changed(self):
        if not self.ui_manager.running:
            return
        if self.settings.direction == "down":
            self.menu_cont.set_relative_pos(
                (self.relative_rect.x+self.style.stack.padding, self.relative_rect.bottom+self.style.stack.spacing))
        else:
            self.menu_cont.set_relative_pos((self.relative_rect.x+self.style.stack.padding,
                                            self.relative_rect.top-self.menu_cont.relative_rect.h-self.style.stack.spacing))


class SelectionList(VStack):
    """An element with options the user can select or deselect"""

    def __init__(self,
                 options: list[str],
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 settings: settings_.SelectionListSettings = settings_.SelectionListDefaultSettings,
                 ):
        super().__init__(relative_rect, element_id, style_id, parent, ui_manager)
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
                    selected.append(btn.text.get_active_text())
                else:
                    return btn.text.get_active_text()
        return selected if self.settings.multi_select else None

    def set_options(self, options: list[str]) -> typing.Self:
        """Set the options and rebuild the element"""
        self.options: list[str] = list(options)
        self.option_buttons: list[Button] = []
        self.build()
        return self

    def on_option_select(self, btn: Button):
        """[Internal] Child callback"""
        if not self.settings.multi_select:
            for opt in self.option_buttons:
                if opt.text.text != btn.text.text:
                    opt.status.deselect()
        self.status.invoke_callback("on_option_select", btn.text.text)
        _post_selectionlist_event("select", self, btn.text.text)

    def on_option_deselect(self, btn: Button):
        """[Internal] Child callback"""
        self.status.invoke_callback("on_option_deselect", btn.text.text)
        _post_selectionlist_event("deselect", self, btn.text.text)

    def build(self):
        if not self.ui_manager.running:
            return
        self.destroy_children()
        for i, option in enumerate(self.options):
            btn = Button(option, pygame.Rect(0, 0, 0, self.settings.option_height),
                         self.element_id +
                         f"_option_{i}", style_id_or_copy(
                             self, self.settings.option_style_id),
                         True, self, self.ui_manager).add_element_types("selectionlist_option").\
                status.add_multi_listeners(
                    on_select=self.on_option_select, on_deselect=self.on_option_deselect).element
            self.option_buttons.append(btn)
