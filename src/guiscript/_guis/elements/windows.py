import pygame
import typing
import pathlib
import os

from .element import Element
from .stacks import HStack, VStack
from .factories import Button
from .menus import SelectionList
from .entries import Entry
from ..manager import Manager
from ..state import UIState
from .. import settings as settings_
from .. import common
from .. import events


class Modal(VStack):
    """A helper container that covers all the screen containing a specified element. Default styling will darken the sorrounding and starts hidden"""
    need_event = True

    def __init__(self,
                 modal_element: Element,
                 element_id: str = "none",
                 style_id: str = "",
                 manager: Manager | None = None,
                 settings: settings_.ModalSettings|None = None
                 ):
        if settings is None:
            settings = settings_.ModalSettings()
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

class _WinStackHolder:
    window_stack: list["Window"] = []
    
    
class Window(Element):
    """A floating element with a title bar, a close button and a content container that can be dragged and resized"""

    def __init__(self,
                 relative_rect: pygame.Rect,
                 title: str = "Guiscript Window",
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.WindowSettings|None = None
                 ):
        if settings is None:
            settings = settings_.WindowSettings()
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "window",), parent, manager)
        self.set_ignore(True, True).set_z_index(common.Z_INDEXES["window-start"]+len(
            _WinStackHolder.window_stack)).status.register_callbacks("on_close", "on_collapse").set_drag(True)
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
            self.collapse_button: Button | None = Button(settings.collapse_down_txt, pygame.Rect(0, 0, settings.title_bar_height, settings.title_bar_height),
                                                      self.element_id+"_collapse_button", common.style_id_or_copy(self, settings.collapse_button_style_id), False, self.title_bar, self.manager)\
                .add_element_type("window_collapse_button").status.add_listener("on_click", self._on_collapse_click).element.set_attr("builtin", True)
        else:
            self.collapse_button: Button | None = None
        if settings.have_close_button:
            self.close_button: Button | None = Button(settings.close_button_txt, pygame.Rect(0, 0, settings.title_bar_height, settings.title_bar_height),
                                                   self.element_id+"_close_button", common.style_id_or_copy(self, settings.close_button_style_id), False, self.title_bar, self.manager)\
                .add_element_type("window_close_button").status.add_listener("on_click", self._on_close_click).element.set_attr("builtin", True)
        else:
            self.close_button: Button | None = None
        self._before_collapse_h: int = self.relative_rect.h
        self.content: VStack = VStack(pygame.Rect(0, 0, 1, 1), self.element_id+"_content", common.style_id_or_copy(self, settings.content_style_id),
                                      self, self.manager, settings.scrollbars_style_id).add_element_type("window_content")\
            .set_anchor("parent", "left", "left")\
            .set_anchor("parent", "right", "right")\
            .set_anchor(self.title_bar, "top", "bottom")\
            .set_anchor("parent", "bottom", "bottom").set_attr("builtin", True)
        _WinStackHolder.window_stack.append(self)
        self.collapsed: bool = False
        self.move_on_top()
        self.build()
        
    @staticmethod
    def get_window_stack() -> list["Window"]:
        """Return the window stack"""
        return _WinStackHolder.window_stack

    def _on_close_click(self):
        self.status.invoke_callback("on_close")
        events._post_window_event("close", self)
        self.close()

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
        
    def close(self) -> typing.Self|None:
        """Close the window based on the settings (hide or destroy)"""
        if self.settings.hide_on_close:
            self.hide()
            return self
        if self.settings.destroy_on_close:
            self.destroy()

    def collapse(self) -> typing.Self:
        """Toggle the collapse status of the window"""
        if self.collapsed:
            self.set_size((self.relative_rect.w, self._before_collapse_h))
            if self.settings.have_collapse_button:
                self.collapse_button.text.set_text(
                    self.settings.collapse_down_txt)
            self.collapsed = False
        else:
            self._before_collapse_h = self.relative_rect.h
            self.set_size(
                (self.relative_rect.w, self.settings.title_bar_height+self.style.stack.padding*2))
            if self.settings.have_collapse_button:
                self.collapse_button.text.set_text(self.settings.collapse_up_txt)
            self.collapsed = True
        self.move_on_top()
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
        new_idx = common.Z_INDEXES["window-start"]+len(_WinStackHolder.window_stack)
        if previous_idx == new_idx:
            return self
        if new_idx > common.Z_INDEXES["window-end"]:
            return self
        self.set_z_index(new_idx)
        for win in _WinStackHolder.window_stack:
            if win is not self and win.z_index > previous_idx:
                win.set_z_index(win.z_index-1)
        return self

    def on_destroy(self):
        if self in _WinStackHolder.window_stack:
            _WinStackHolder.window_stack.remove(self)

    def build(self):
        self.title_bar.set_size(
            (self.relative_rect.w-self.style.stack.padding*2, self.settings.title_bar_height))
        self.title_bar.anchors_padding(self.style.stack.padding)
        self.content.anchors_padding(self.style.stack.padding, "top")
        self.content._anchors["top"].offset = self.style.stack.spacing


class FileDialog(Window):
    """Builtin window able to select paths with lots of customization in the settings. Extra interaction is: ctrl + select to enter, entry + enter to set path"""
    
    def __init__(self,
                 start_path: str|pathlib.Path,
                 relative_rect: pygame.Rect,
                 title: str = "Choose a file or a folder",
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.FileDialogSettings|None = None
                 ):
        if settings is None:
            settings = settings_.FileDialogSettings()
        self._done = False
        if settings.window_settings is None:
            settings.window_settings = settings_.WindowSettings()
        if settings.selectionlist_settings is None:
            settings.selectionlist_settings = settings_.SelectionListSettings(option_style_id="fildialog_selectionlist_option")
        else:
            if settings.selectionlist_settings.option_style_id == "copy":
                settings.selectionlist_settings.option_style_id = "fildialog_selectionlist_option"
            else:
                settings.selectionlist_settings.option_style_id += ";fildialog_selectionlist_option"
        if settings.entry_settings is None:
            settings.entry_settings = settings_.EntrySettings()
        super().__init__(relative_rect, title, element_id, style_id, parent, manager, settings.window_settings)
        self.fdsettings: settings_.FileDialogSettings = settings
        self.add_element_type("filedialog").status.register_callbacks("on_back", "on_cancel", "on_ok", "on_enter", "on_home")
        self.content.add_element_type("filedialog_content")
        
        self.current_path: pathlib.Path = pathlib.Path(start_path)
        if not self.current_path.exists():
            self.current_path = pathlib.Path(os.getcwd())
        self._options_selected: list[str] = []
        buttons_style_id = common.style_id_or_copy(self, settings.buttons_style_id)
        
        self.top_row_cont: HStack = HStack(pygame.Rect(0,0,0,settings.entry_buttons_h), self.element_id+"_top_row_cont", "invis_cont", self.content, self.manager)\
                        .add_element_types("filedialog_row", "filedialog_top_row").set_attr("builtin", True)
        self.home_button: Button = Button(settings.home_btn_txt, pygame.Rect(0,0,settings.top_btns_w,0), self.element_id+"_home_button", buttons_style_id, False, self.top_row_cont, self.manager)\
                        .add_element_types("filedialog_button", "filedialog_home_button")\
                        .set_tooltip("Home", "", height=40, width=100).set_attr("builtin", True)\
                        .status.add_listener("on_click", self._on_home_click).element
        self.back_button: Button = Button(settings.back_btn_txt, pygame.Rect(0,0,settings.top_btns_w,0), self.element_id+"_back_button", buttons_style_id, False, self.top_row_cont, self.manager)\
                        .add_element_types("filedialog_button", "filedialog_back_button")\
                        .set_tooltip("Back", "", height=40, width=100).set_attr("builtin", True)\
                        .status.add_listener("on_click", self._on_back_click).element
        self.path_entry: Entry = Entry(pygame.Rect(0,0,0,0),
                                       start_path, self.element_id+"_path_entry", common.style_id_or_copy(self, settings.entry_style_id),
                                       self.top_row_cont, self.manager, settings.entry_settings)\
                        .add_element_type("filedialog_path_entry").set_attr("builtin", True)
        self.selectionlist: SelectionList = SelectionList([], pygame.Rect(0,0,0,0), self.element_id+"_selectionlist", common.style_id_or_copy(self, settings.selectionlist_style_id),
                                                          self.content, self.manager, settings.selectionlist_settings)\
                        .add_element_type("filedialog_selectionlist").set_attr("builtin", True)\
                        .status.add_multi_listeners(on_option_select=self._on_selectionlist_select, on_option_deselect=self._on_selectionlist_deselect).element
        self.bottom_row_cont: HStack = HStack(pygame.Rect(0,0,0,settings.entry_buttons_h), self.element_id+"_bottom_row_cont", "invis_cont", self.content, self.manager)\
                        .add_element_types("filedialog_row", "filedialog_bottom_row").set_attr("builtin", True)
        self.enter_button: Button = Button("Enter", pygame.Rect(0,0,0,0), self.element_id+"_enter_button", buttons_style_id, False, self.bottom_row_cont, self.manager)\
                        .add_element_types("filedialog_button", "filedialog_enter_button")\
                        .set_tooltip("Enter", "Can also ctrl+select, can only enter if only one folder is selected", width=300, height=100).set_attr("builtin", True)\
                        .status.add_listener("on_click", self._on_enter_click).element
        self.cancel_button: Button = Button("Cancel", pygame.Rect(0,0,0,0), self.element_id+"_cancel_button", buttons_style_id, False, self.bottom_row_cont, self.manager)\
                        .add_element_types("filedialog_button", "filedialog_cancel_button").set_attr("builtin", True)\
                        .status.add_listener("on_click", self._on_cancel_click).element
        self.ok_button: Button = Button("Ok", pygame.Rect(0,0,0,0), self.element_id+"_ok_button", buttons_style_id, False, self.bottom_row_cont, self.manager)\
                        .add_element_types("filedialog_button", "filedialog_ok_button").set_attr("builtin", True)\
                        .set_tooltip("Ok", "If nothing valid is selected the current folder might be selected", width=300, height=100)\
                        .status.add_listener("on_click", self._on_ok_click).element
        self._done = True
        self._gen_options()
                        
    def _on_back_click(self, user=True):
        self.current_path = self.current_path.parent
        self._path_updated()
        if user:
            self.status.invoke_callback("on_back")
            events._post_filedialog_event(events.FILEDIALOG_BACK, self)
        
    def _on_home_click(self, user=True):
        self.current_path = self.current_path.home()
        self._path_updated()
        if user:
            self.status.invoke_callback("on_home")
            events._post_filedialog_event(events.FILEDIALOG_HOME, self)
        
    def _on_selectionlist_select(self, sl, option):
        if not self.selectionlist.settings.multi_select:
            self._options_selected = []
        self._options_selected.append(option)
        if UIState.keys_pressed[pygame.K_LCTRL] or UIState.keys_pressed[pygame.K_RCTRL]:
            self._on_enter_click()
        
    def _on_selectionlist_deselect(self, sl, option):
        if option in self._options_selected:
            self._options_selected.remove(option)
        
    def _on_cancel_click(self):
        self.status.invoke_callback("on_cancel")
        events._post_filedialog_event(events.FILEDIALOG_CANCEL, self)
        self.status.invoke_callback("on_close")
        events._post_filedialog_event(events.FILEDIALOG_CLOSE, self)
        self.close()
        
    def _on_ok_click(self):
        paths = self.get_valid_selected()
        if len(paths) > 0:
            self.status.invoke_callback("on_ok", paths)
            events._post_filedialog_event(events.FILEDIALOG_OK, self)
            self.status.invoke_callback("on_close")
            events._post_filedialog_event(events.FILEDIALOG_CLOSE, self)
            self.close()
        
    def _on_enter_click(self):
        if len(self._options_selected) > 1:
            return
        sel_path = self._options_selected[0]
        sel_path: pathlib.Path = self.current_path/sel_path
        if not sel_path.is_dir():
            return
        self.current_path = sel_path
        self._path_updated()
        self.status.invoke_callback("on_enter")
        events._post_filedialog_event(events.FILEDIALOG_ENTER, self)
        
    def _path_valid(self, path: str|pathlib.Path) -> bool:
        path = pathlib.Path(path)
        name, ext, full = path.stem, path.suffix, path.name
        if (lst:=self.fdsettings.extension_whitelist) is not None:
            if ext not in lst:
                return False
        if (lst:=self.fdsettings.extension_blacklist) is not None:
            if ext in lst:
                return False
        if (lst:=self.fdsettings.name_whitelist) is not None:
            if name not in lst:
                return False
        if (lst:=self.fdsettings.name_blacklist) is not None:
            if name in lst:
                return False
        if (lst:=self.fdsettings.full_name_whitelist) is not None:
            if full not in lst:
                return False
        if (lst:=self.fdsettings.full_name_blacklist) is not None:
            if full in lst:
                return False
        if (lst:=self.fdsettings.path_whitelist) is not None:
            if str(path) not in lst:
                return False
        if (lst:=self.fdsettings.path_blacklist) is not None:
            if str(path) in lst:
                return False
        return True
    
    def _sort_options(self, options) -> list[str]:
        folders, files = [], []
        for opt in options:
            if (self.current_path/opt).is_dir():
                folders.append(opt)
            else:
                files.append(opt)
        return folders+files
        
    def _path_updated(self):
        self._gen_options()
        self.path_entry.set_text(self.current_path.absolute())
    
    def _gen_options(self):
        self._options_selected = []
        try:
            options = os.listdir(self.current_path.absolute())
            options = [opt for opt in options if self._path_valid(self.current_path/opt)]
            options = self._sort_options(options)
        except:
            options = ["Error while getting folder content"]
        self.selectionlist.set_options(options)
    
    def build(self):
        super().build()
        if not self._done:
            return
        for button in [self.enter_button, self.cancel_button, self.ok_button]:
            button.set_size((self.relative_rect.w*self.fdsettings.bottom_btns_rel_w,0), True)
            
    def set_path(self, path: str|pathlib.Path) -> typing.Self:
        """Manually set the current path if it is valid"""
        path = pathlib.Path(path)
        if not path.exists():
            return self
        self.current_path = path
        self._path_updated()
        return self
        
    def get_paths_selected(self) -> list[pathlib.Path]:
        """Get the paths currently selected"""
        paths = [self.current_path/opt for opt in self._on_selectionlist_select]
        if len(paths) <= 0:
            paths = [self.current_path]
        return paths
    
    def get_valid_selected(self) -> list[pathlib.Path]:
        """Get the paths selected excluding folders if allow_folder is set to False"""
        paths = []
        for p in self._options_selected:
            isdir = (self.current_path/p).is_dir()
            if  isdir and self.fdsettings.allow_folder or not isdir:
                paths.append(self.current_path/p)
        if len(paths) <= 0 and self.fdsettings.allow_folder:
            paths = [self.current_path]
        return paths
        
    def back(self) -> typing.Self:
        """Manually go back to the folder parent"""
        self._on_back_click(False)
        return self
    
    def home(self) -> typing.Self:
        """Manually go to the home directory"""
        self._on_home_click(False)
        return self
        
    def path_valid(self, path: str|pathlib.Path) -> bool:
        """Return whether the specified path would be valid using the settings whitelists and blacklists"""
        return self._path_valid(path)
    
    def on_logic(self):
        if not self.path_entry.is_focused():
            return
        if UIState.just_pressed[pygame.K_RETURN]:
            path = pathlib.Path(self.path_entry.get_text())
            if path.exists() and path.is_dir():
                self.current_path = path
                self._path_updated()
