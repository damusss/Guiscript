import pygame
import typing
if typing.TYPE_CHECKING:
    from .manager import UIManager
    from .elements.element import UIElement


class UIState:
    current_manager: "UIManager" = None
    current_parent: "UIElement" = None

    delta_time: float = 1
    mouse_wheel: float = 0
    mouse_pos: pygame.Vector2 = pygame.Vector2()
    mouse_rel: pygame.Vector2 = pygame.Vector2()
    mouse_pressed: tuple[bool, bool, bool] = pygame.mouse.get_pressed()
    keys_pressed = pygame.key.get_pressed()
    frame_count: int = 0
