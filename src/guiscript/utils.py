import pygame
import typing

from .elements.element import UIElement

element: typing.TypeAlias = UIElement


def ZeroRect() -> pygame.Rect:
    return pygame.Rect(0, 0, 0, 0)


def SizeRect(width: int, height: int) -> pygame.Rect:
    return pygame.Rect(0, 0, width, height)


def PosRect(x: int, y: int) -> pygame.Rect:
    return pygame.Rect(x, y, 0, 0)
