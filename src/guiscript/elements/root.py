import pygame
import typing

from ..error import UIError
from .element import Element


class UIRoot:
    """The root element for elements bound to a Manager. It's a simplified version of Element. Automatically created by Manager"""

    def __init__(self, screen_surface: pygame.Surface):
        self.set_screen_surface(screen_surface)

        self.parent: typing.Never = None
        self.active: bool = True
        self.visible: bool = True
        self.scroll_offset = pygame.Vector2()
        self.children: list[Element] = []
        self.ignore_raycast: bool = False

    def _refresh_stack(self):
        ...

    def _add_child(self, element: Element) -> typing.Self:
        self.children.append(element)
        return self

    def remove_child(self, element: Element) -> typing.Self:
        """Remove a child from the children, without destroying it"""
        if element in self.children:
            self.children.remove(element)
        return self

    def set_screen_surface(self, screen_surface: pygame.Surface) -> typing.Self:
        """Set the screen surface to draw on"""
        self.screen_surface: pygame.Surface = screen_surface
        self.element_surface: pygame.Surface = screen_surface
        self.relative_rect: pygame.Rect = pygame.Rect(
            (0, 0), screen_surface.get_size())
        self.absolute_rect: pygame.Rect = self.relative_rect.copy()
        return self

    def set_dirty(self):
        """Empty"""
        ...

    def __enter__(self):
        raise UIError(
            f"Cannot use context manager with UIRoot, it's alrady the default element parent")

    def _first_frame(self):
        ...

    def _event(self, event: pygame.Event):
        for child in self.children:
            child._event(event)

    def _logic(self):
        for child in self.children:
            child._logic()

    def _render(self):
        for child in self.children:
            child._render(0, True)

    def get_absolute_topleft(self) -> pygame.Vector2:
        """Return an empty pygame.Vector2"""
        return pygame.Vector2(0, 0)

    def is_stack(self) -> bool:
        """Always return False"""
        return False

    def can_navigate(self) -> typing.Literal[False]:
        """Return False"""
        return False

    def find_navigable_child(self) -> "Element":
        """Find a child that can be navigated between the element's children and their children"""
        for child in self.children:
            if child.can_navigate():
                return child
            else:
                their_child = child.find_navigable_child()
                if their_child is not None:
                    return their_child
        return None

    def has_navigable_child(self) -> bool:
        """Return whether at least one of the element's children can be navigated"""
        for child in self.children:
            if child.can_navigate():
                return True
        return False

    def navigable_children_count(self) -> bool:
        """Return how many of the element's children can be navigated"""
        count = 0
        for child in self.children:
            if child.can_navigate():
                count += 1
        return count

    def destroy_children(self) -> typing.Self:
        """Destroy all children of this element if the children have the 'can_destroy' flag set to True"""
        for child in list(self.children):
            child.destroy()
        return self
