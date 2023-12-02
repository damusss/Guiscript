import pygame
import typing

from ..error import UIError
from .element import UIElement


class UIRoot:
    """The root element for elements bound to a UIManager. It's a simplified version of UIElement. Automatically created by UIManager"""

    def __init__(self, screen_surface: pygame.Surface):
        self.set_screen_surface(screen_surface)

        self.parent: typing.Never = None
        self.active: bool = True
        self.visible: bool = True
        self.scroll_offset = pygame.Vector2()
        self.children: list[UIElement] = []
        self.ignore_raycast: bool = False

    def refresh_stack(self):
        """[Internal] Empty"""
        ...

    def add_child(self, element: UIElement) -> typing.Self:
        """Add a child to the children"""
        self.children.append(element)
        return self
    
    def remove_child(self, element: UIElement) -> typing.Self:
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
        """[Internal] Empty"""
        ...

    def __enter__(self):
        raise UIError(
            f"Cannot use context manager with UIRoot, it's alrady the default element parent")

    def first_frame(self):
        """[Internal] Empty"""
        ...

    def event(self, event: pygame.Event):
        """[Internal] Called for every event"""
        for child in self.children:
            child.event(event)

    def logic(self):
        """[Internal] Called every frame, update children"""
        for child in self.children:
            child.logic()

    def render(self):
        """[Internal] Called every frame, render children"""
        for child in self.children:
            child.render(0, True)

    def get_absolute_topleft(self) -> pygame.Vector2:
        """Return an empty pygame.Vector2"""
        return pygame.Vector2(0, 0)
    
    def is_stack(self) -> bool:
        """Always return False"""
        return False

    def can_navigate(self) -> typing.Literal[False]:
        """Return False"""
        return False

    def find_navigable_child(self) -> "UIElement":
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
