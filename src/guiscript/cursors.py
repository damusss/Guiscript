import pygame
import typing
if typing.TYPE_CHECKING:
    from .manager import Manager
    
from . import common

class UICursors:
    """Keep settings and cursors for cursor change on interaction of a manager"""
    
    def __init__(self, manager: "Manager"):
        self.manager: "Manager" = manager
        self.do_override_cursor: bool = True
        self.default_cursor: common.CursorLike = pygame.SYSTEM_CURSOR_ARROW
        self.hover_cursor: common.CursorLike = pygame.SYSTEM_CURSOR_HAND
        
    def set_cursors(self, default: common.CursorLike = pygame.SYSTEM_CURSOR_ARROW,
                    hover: common.CursorLike = pygame.SYSTEM_CURSOR_HAND) -> typing.Self:
        """Set the default and hover cursors"""
        self.default_cursor = default
        self.hover_cursor = hover
        return self
    
    def set_do_override(self, do_override_cursor: bool) -> typing.Self:
        """If set False, the cursor won't change so the user can manage the cursor"""
        self.do_override_cursor = do_override_cursor
        return self
        