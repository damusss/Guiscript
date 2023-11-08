import pygame
from .elements.element import UIElement

HOVERED = pygame.event.custom_type()
PRESSED = pygame.event.custom_type()
RIGHT_PRESSED = pygame.event.custom_type()
START_HOVER = pygame.event.custom_type()
START_PRESS = pygame.event.custom_type()
START_RIGHT_PRESS = pygame.event.custom_type()
STOP_HOVER = pygame.event.custom_type()
STOP_PRESS = pygame.event.custom_type()
STOP_RIGHT_PRESS = pygame.event.custom_type()
SELECT = pygame.event.custom_type()
DESELECT = pygame.event.custom_type()
CLICK = pygame.event.custom_type()
RIGHT_CLICK = pygame.event.custom_type()

SLIDESHOW_MOVE_LEFT = pygame.event.custom_type()
SLIDESHOW_MOVE_RIGHT = pygame.event.custom_type()

SLIDER_MOVE = pygame.event.custom_type()

SOUND_PLAYER_TOGGLE = pygame.event.custom_type()
SOUND_PLAYER_MUTE = pygame.event.custom_type()
SOUND_PLAYER_TRACK_MOVE = pygame.event.custom_type()
SOUND_PLAYER_VOLUME_MOVE = pygame.event.custom_type()
SOUND_PLAYER_END = pygame.event.custom_type()

VIDEO_PLAYER_TOGGLE = pygame.event.custom_type()
VIDEO_PLAYER_MUTE = pygame.event.custom_type()
VIDEO_PLAYER_TRACK_MOVE = pygame.event.custom_type()
VIDEO_PLAYER_VOLUME_MOVE = pygame.event.custom_type()
VIDEO_PLAYER_END = pygame.event.custom_type()


def _post_base_event(type_: int, element: UIElement):
    pygame.event.post(pygame.Event(type_, {
        "id": element.element_id,
        "element_id": element.element_id,
        "element": element,
        "obj": element,
    }))


def _post_slideshow_event(mode: str, element: UIElement):
    pygame.event.post(pygame.Event(
        SLIDESHOW_MOVE_LEFT if mode == "left" else SLIDESHOW_MOVE_RIGHT,
        {
            "id": element.element_id,
            "element_id": element.element_id,
            "element": element,
            "obj": element,
            "slideshow": element
        }
    ))


def _post_slider_event(old: float, new: float, element: UIElement):
    pygame.event.post(pygame.Event(SLIDER_MOVE, {
        "id": element.element_id,
        "element_id": element.element_id,
        "element": element,
        "obj": element,
        "slider": element,
        "old_value": old,
        "old_percent": old*100,
        "value": new,
        "percent": new*100
    }))


def _post_sound_player_event(type_: int, element: UIElement):
    pygame.event.post(pygame.Event(type_, {
        "id": element.element_id,
        "element_id": element.element_id,
        "element": element,
        "obj": element,
        "sound_player": element,
        "playing": element.playing,
        "muted": element.muted,
        "paused": element.paused,
        "time_passed": element.get_time_passed(),
        "time_remaining": element.get_time_remaining(),
        "volume": element.get_volume()
    }))


def _post_video_player_event(type_: int, element: UIElement):
    pygame.event.post(pygame.Event(type_, {
        "id": element.element_id,
        "element_id": element.element_id,
        "element": element,
        "obj": element,
        "video_player": element,
        "playing": element.playing,
        "muted": element.muted,
        "paused": element.paused,
        "time_passed": element.get_time_passed(),
        "time_remaining": element.get_time_remaining(),
        "volume": element.get_volume()
    }))
