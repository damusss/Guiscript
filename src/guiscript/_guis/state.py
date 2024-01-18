import pygame
import typing
if typing.TYPE_CHECKING:
    from .manager import Manager
    from .elements.element import Element


class UIState:
    """[Internal] Hold global UI information"""
    current_manager: "Manager" = None
    current_parent: "Element" = None
    current_style_id: str | None = None

    delta_time: float = 1
    mouse_wheel: pygame.Vector2 = pygame.Vector2()
    mouse_pos: pygame.Vector2 = pygame.Vector2()
    mouse_rel: pygame.Vector2 = pygame.Vector2()
    mouse_pressed: tuple[bool, bool, bool] = pygame.mouse.get_pressed()
    keys_pressed = pygame.key.get_pressed()
    just_pressed = pygame.key.get_just_pressed()
    frame_count: int = 0
    space_pressed: bool = False
    num_managers: int = 0
    any_pressed: bool = False
