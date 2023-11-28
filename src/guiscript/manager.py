import pygame
import typing

from .state import UIState
from .elements.root import UIRoot
from .interact import UIInteract
from .navigation import UINavigation
from .elements.element import UIElement
from .script import UIScript
from .style import UIStyles
from . import common


class UIManager:
    """
    Manager of ui elements bound to it. A UIRoot is created automatically as well as interaction and keyboard navigation

    All paths provided by the gs_path argument and all sources provided by the gs_sources will be executed using gs_variables as variables
    """

    def __init__(self,
                 screen_surface: pygame.Surface,
                 current: bool = True,
                 gs_paths: list[str] | None = None,
                 gs_sources: list[str] | None = None,
                 gs_variables: dict[str] | None = None,
                 ):
        self.gs_variables = gs_variables
        if gs_variables is None:
            self.gs_variables: dict[str] = {}

        UIScript.parse_source(common.DEFAULT_STYLE_GSS, "default.gss", {
            "DARK_COLOR": (12, 12, 12)
        })
        if gs_paths is not None:
            for gs_path in gs_paths:
                UIScript.parse_script(gs_path, self.gs_variables)
        if gs_sources is not None:
            for i, gs_source in enumerate(gs_sources):
                UIScript.parse_source(gs_source, f"gss.source.idx:{i}", self.gs_variables)
                
        self.running: bool = False
        self.all_elements: list[UIElement] = []
        self.last_rendered: UIElement = None
        self.interact: UIInteract = UIInteract(self)
        self.navigation: UINavigation = UINavigation(self)
        self.scroll_multiplier: float = 12
        self.root: UIRoot = UIRoot(screen_surface)

        if current:
            self.set_current()
            
    def restart(self) -> typing.Self:
        """Set the running flag to False. Useful when recreating the UI elements tree, to avoid errors"""
        self.running = False
        return self
            
    def set_screen_surface(self, screen_surface: pygame.Surface) -> typing.Self:
        """Set the screen surface to draw on"""
        self.root.set_screen_surface(screen_surface)
        return self

    def running_check(self):
        """[Internal] check the running flag and call first_frame on all elements"""
        if not self.running:
            self.running = True
            for el in self.all_elements:
                el.first_frame()

    def event(self, event: pygame.Event):
        """Pass events to elements and to interaction and keyboard navigation"""
        self.running_check()
        if event.type == pygame.MOUSEWHEEL:
            UIState.mouse_wheel = event.y
        self.root.event(event)
        self.interact.event(event)
        self.navigation.event(event)

    def logic(self):
        """Update elements and their status"""
        self.running_check()
        self.interact.logic()
        self.root.logic()

    def render(self):
        """Render all elements to the screen surface"""
        self.running_check()
        self.root.render()
        UIState.mouse_wheel = 0

    def set_current(self) -> typing.Self:
        """Set this manager as the current. All elements created after this call will use this as their manager, unless a different one is specified"""
        UIState.current_manager = self
        return self

    def set_gs_vars(self, **names_values) -> typing.Self:
        """Update the variables used to execute style scripts"""
        for name, val in names_values.items():
            self.gs_variables[name] = val
        return self

    def load_gs_style(self, filepath: str):
        """Execute a style script"""
        UIScript.parse_script(filepath, self.gs_variables)

    def get_with_element_id(self, element_id: str) -> UIElement | None:
        """Return the element with the given id"""
        for el in self.all_elements:
            if el.element_id == element_id:
                return el

    def get_with_style_id(self, style_id: str) -> typing.Generator[UIElement, typing.Any, typing.Any]:
        """Return (as a generator) all elements that match the given style id"""
        for el in self.all_elements:
            if el.style_id == style_id or ";"+style_id+";" in el.style_id or el.style_id.endswith(";"+style_id) or el.style_id.startswith(style_id+";"):
                yield el

    def get_with_element_type(self, element_type: str) -> typing.Generator[UIElement, typing.Any, typing.Any]:
        """Return (as a generator) all elements that have the given element type"""
        for el in self.all_elements:
            if element_type in el.element_types:
                yield el
