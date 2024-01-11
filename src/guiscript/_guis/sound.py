import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import Element


class UISounds:
    """
    Hold custom interaction sounds for an element\n
    Available sounds are click, immediate_click, hover, leave_hover
    """

    def __init__(self, element):
        self.element: "Element" = element
        self.sounds: dict[str, pygame.mixer.Sound | None] = {}

    def set(self, name: str, sound: pygame.mixer.Sound | str) -> typing.Self:
        """Bind a sound name to a sound. If the string 'nosound' is provided, The sound will never be played"""
        self.sounds[name] = sound
        return self

    def sets(self, **names_sounds: pygame.mixer.Sound | str) -> typing.Self:
        """Bind sound names to sounds with kwargs. If the string 'nosound' is provided, The sound will never be played"""
        for n, s in names_sounds.items():
            self.set(n, s)
        return self

    def play(self, name: str, force: bool = False) -> typing.Self:
        """Try to play a sound. If no custom sound is set, the manager's interact default sound will be used unless 'nosound' was set as the sound"""
        if not force and (not self.element.status.visible or not self.element.status.active):
            return self
        s = self.sounds.get(name, None)
        if s == "nosound":
            return self
        if s is not None:
            s.play()
            return self
        interact = self.element.manager.interact
        if not hasattr(interact, f"{name}_sound"):
            return self
        s: pygame.mixer.Sound | None = getattr(interact, f"{name}_sound")
        if s is not None:
            s.play()
        return self
