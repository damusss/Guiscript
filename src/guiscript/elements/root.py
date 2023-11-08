import pygame
import typing

from ..error import UIError
from .element import UIElement


class UIRoot:
    def __init__(self, screen_surface: pygame.Surface):
        self.set_screen_surface(screen_surface)

        self.parent: typing.Never = None
        self.active: bool = True
        self.visible: bool = True
        self.scroll_offset = pygame.Vector2()
        self.children: list[UIElement] = []
        
    def update_size_positions(self):
        ...

    def add_child(self, element: UIElement) -> typing.Self:
        self.children.append(element)
        return self

    def set_screen_surface(self, screen_surface: pygame.Surface) -> typing.Self:
        self.screen_surface: pygame.Surface = screen_surface
        self.element_surface: pygame.Surface = screen_surface
        self.relative_rect: pygame.Rect = pygame.Rect(
            (0, 0), screen_surface.get_size())
        self.absolute_rect: pygame.Rect = self.relative_rect.copy()
        return self

    def __enter__(self):
        raise UIError(
            f"Cannot use context manager with UIRoot, it's alrady the default element parent")
        
    def first_frame(self):
        ...
        
    def event(self, event: pygame.Event):
        for child in self.children:
            child.event(event)

    def logic(self):
        for child in self.children:
            child.logic()

    def render(self):
        for child in self.children:
            child.render()

    def get_absolute_topleft(self) -> pygame.Vector2:
        return pygame.Vector2(0, 0)
    
    def can_navigate(self) -> bool:
        return False
    
    def find_navigable_child(self) -> "UIElement":
        for child in self.children:
            if child.can_navigate():
                return child
            else:
                their_child = child.find_navigable_child()
                if their_child is not None:
                    return their_child
        return None
    
    def has_navigable_child(self) -> bool:
        for child in self.children:
            if child.can_navigate():
                return True
        return False
    
    def navigable_children_count(self) -> bool:
        count = 0
        for child in self.children:
            if child.can_navigate():
                count += 1
        return count
