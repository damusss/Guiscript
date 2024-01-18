import pygame
import typing

from .state import UIState
from .elements.root import UIRoot
from .interact import UIInteract
from .navigation import UINavigation
from .elements.element import Element
from .script import UIScript
from .cursors import UICursors
from . import common


class Manager:
    """
    Manager of ui elements bound to it. A UIRoot is created automatically as well as interaction and keyboard navigation

    All paths provided by the gss_path argument and all sources provided by the gss_sources will be executed using gss_variables as variables
    """

    def __init__(self,
                 screen_surface: pygame.Surface,
                 is_current: bool = True,
                 gss_paths: list[str] | None = None,
                 gss_sources: list[str] | None = None,
                 gss_variables: dict[str] | None = None,
                 ):
        self.gss_variables = gss_variables
        if gss_variables is None:
            self.gss_variables: dict[str] = {}

        UIScript.parse_source(common.DEFAULT_STYLE_GSS, "default.gss", {
            "DARK_COLOR": (12, 12, 12)
        })
        if gss_paths is not None:
            for gss_path in gss_paths:
                UIScript.parse_script(gss_path, self.gss_variables)
        if gss_sources is not None:
            for i, gss_source in enumerate(gss_sources):
                UIScript.parse_source(gss_source, f"gss.source.idx:{UIState.num_managers},{i}", self.gss_variables)

        self._running: bool = False
        self._all_elements: list[Element] = []
        self._last_rendered: Element = None
        self._event_callbacks: list[Element] = []
        self.cursors: UICursors = UICursors(self)
        self.interact: UIInteract = UIInteract(self)
        self.navigation: UINavigation = UINavigation(self)
        self.scroll_multiplier: float = 12
        self.min_scroll_handle_size: int = 5
        self.root: UIRoot = UIRoot(screen_surface)

        if is_current:
            self.set_current()
        UIState.num_managers += 1

    def restart(self) -> typing.Self:
        """Set the running flag to False. Useful when recreating the UI elements tree, to avoid errors"""
        self._running = False
        return self

    def destroy(self) -> typing.Self:
        """Destroy all elements except the root and restart the manager"""
        self.root.destroy_children()
        self.restart()
        return self

    def set_screen_surface(self, screen_surface: pygame.Surface) -> typing.Self:
        """Set the screen surface to draw on"""
        self.root.set_screen_surface(screen_surface)
        return self

    def _running_check(self):
        if not self._running:
            self._running = True
            for el in list(self._all_elements):
                el._first_frame()

    def event(self, event: pygame.Event) -> typing.Self:
        """Pass events to elements and to interaction and keyboard navigation"""
        self._running_check()
        if event.type == pygame.MOUSEWHEEL:
            UIState.mouse_wheel = pygame.Vector2(event.x, event.y)
        elif event.type == pygame.KEYDOWN and not event.key == pygame.K_LCTRL:
            UIState.any_pressed = True
        elif event.type == pygame.KEYUP:
            UIState.any_pressed = False
        for el in self._event_callbacks:
            el.on_event(event)
        self.interact._event(event)
        self.navigation._event(event)
        return self

    def logic(self) -> typing.Self:
        """Update elements and their status"""
        self._running_check()
        self.interact._logic()
        self.root._logic()
        return self

    def render(self) -> typing.Self:
        """Render all elements to the screen surface"""
        self._running_check()
        self.root._render()
        UIState.mouse_wheel = pygame.Vector2()
        return self

    def set_current(self) -> typing.Self:
        """Set this manager as the current. All elements created after this call will use this as their manager, unless a different one is specified"""
        UIState.current_manager = self
        return self
    
    def is_current(self) -> bool:
        """Return whether this manager is set as current"""
        return self is UIState.current_manager

    def set_gss_vars(self, **names_values) -> typing.Self:
        """Update the variables used to execute style scripts"""
        for name, val in names_values.items():
            self.gss_variables[name] = val
        return self

    def load_gss_script(self, filepath: str) -> typing.Self:
        """Execute a style script from a file"""
        UIScript.parse_script(filepath, self.gss_variables)
        return self

    def load_gss_source(self, source: str, debug_filename: str) -> typing.Self:
        """Execute a style script from a string"""
        UIScript.parse_source(source, debug_filename, self.gss_variables)
        return self

    def get_with_element_id(self, element_id: str) -> Element | None:
        """Return the element with the given id"""
        for el in self._all_elements:
            if el.element_id == element_id:
                return el

    def get_with_style_id(self, style_id: str) -> typing.Generator[Element, typing.Any, typing.Any]:
        """Return (as a generator) all elements that match the given style id"""
        for el in self._all_elements:
            if el.style_id == style_id or ";"+style_id+";" in el.style_id or el.style_id.endswith(";"+style_id) or el.style_id.startswith(style_id+";"):
                yield el

    def get_with_element_type(self, element_type: str) -> typing.Generator[Element, typing.Any, typing.Any]:
        """Return (as a generator) all elements that have the given element type"""
        for el in self._all_elements:
            if element_type in el.element_types:
                yield el

    def get_all_elements(self) -> list[Element]:
        """Return all the elements as a list. Modifying it won't affect the manager's elements"""
        return list(self._all_elements)
