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
        self.resize_cursors: dict[str, common.CursorLike] = {}
        self.set_cursors()

    def set_cursors(self,
                    default: common.CursorLike = pygame.SYSTEM_CURSOR_ARROW,
                    hover: common.CursorLike = pygame.SYSTEM_CURSOR_HAND,
                    resize_top_bottom: common.CursorLike = pygame.SYSTEM_CURSOR_SIZENS,
                    resize_left_right: common.CursorLike = pygame.SYSTEM_CURSOR_SIZEWE,
                    resize_tl_br: common.CursorLike = pygame.SYSTEM_CURSOR_SIZENWSE,
                    resize_tr_bl: common.CursorLike = pygame.SYSTEM_CURSOR_SIZENESW,) -> typing.Self:
        """Set the default and hover cursors"""
        self.default_cursor = default
        self.hover_cursor = hover
        self.resize_cursors["top"] = self.resize_cursors["bottom"] = resize_top_bottom
        self.resize_cursors["left"] = self.resize_cursors["right"] = resize_left_right
        self.resize_cursors["topleft"] = self.resize_cursors["bottomright"] = resize_tl_br
        self.resize_cursors["topright"] = self.resize_cursors["bottomleft"] = resize_tr_bl
        return self

    def set_do_override(self, do_override_cursor: bool) -> typing.Self:
        """If set False, the cursor won't change so the user can manage the cursor"""
        self.do_override_cursor = do_override_cursor
        return self
