import pygame
import typing

from .state import UIState
from .elements.root import UIRoot
from .interact import UIInteract
from .navigation import UINavigation
from .elements.element import UIElement
from .script import UIScript
from . import common


class UIManager:
    def __init__(self,
                 screen_surface: pygame.Surface,
                 current: bool = True,
                 gs_paths: list[str] | None = None,
                 gs_variables: dict[str] | None = None,
                 ):
        self.gs_variables = gs_variables
        if gs_variables is None:
            self.gs_variables: dict[str] = {}

        UIScript.parse_source(common.DEFAULT_STYLE_GSS, "default.gss", {
            "DARK_COLOR": (12,12,12)
        })
        if gs_paths is not None:
            for ssp in gs_paths:
                UIScript.parse_script(ssp, self.gs_variables)

        self.running: bool = False
        self.all_elements: list[UIElement] = []
        self.last_rendered: UIElement = None
        self.interact: UIInteract = UIInteract(self)
        self.navigation: UINavigation = UINavigation(self)
        self.scroll_multiplier: float = 12
        self.root: UIRoot = UIRoot(screen_surface)

        if current:
            self.set_current()

    def running_check(self):
        if not self.running:
            self.running = True
            for el in self.all_elements:
                el.first_frame()

    def event(self, event: pygame.Event):
        self.running_check()
        if event.type == pygame.MOUSEWHEEL:
            UIState.mouse_wheel = event.y
        self.root.event(event)
        self.interact.event(event)
        self.navigation.event(event)

    def logic(self, delta_time: float = 1):
        self.running_check()

        UIState.delta_time = delta_time
        UIState.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        UIState.mouse_rel = pygame.Vector2(pygame.mouse.get_rel())
        UIState.mouse_pressed = pygame.mouse.get_pressed()
        UIState.keys_pressed = pygame.key.get_pressed()
        UIState.space_pressed = UIState.keys_pressed[pygame.K_SPACE]
        if self is UIState.current_manager: UIState.frame_count += 1

        self.interact.logic()
        self.root.logic()

    def render(self):
        self.running_check()
        self.root.render()
        UIState.mouse_wheel = 0

    def set_current(self) -> typing.Self:
        UIState.current_manager = self
        return self

    def set_gs_vars(self, **names_values) -> typing.Self:
        for name, val in names_values.items():
            self.gs_variables[name] = val
        return self

    def load_gs_style(self, filepath: str):
        UIScript.parse_script(filepath, self.gs_variables)

    def get_with_element_id(self, element_id: str) -> UIElement:
        for el in self.all_elements:
            if el.element_id == element_id:
                return el

    def get_with_style_id(self, style_id: str) -> typing.Generator[UIElement, typing.Any, typing.Any]:
        for el in self.all_elements:
            if el.style_id == style_id or ";"+style_id+";" in el.style_id or el.style_id.endswith(";"+style_id) or el.style_id.startswith(style_id+";"):
                yield el

    def get_with_element_type(self, element_type: str) -> typing.Generator[UIElement, typing.Any, typing.Any]:
        for el in self.all_elements:
            if element_type in el.element_types:
                yield el
