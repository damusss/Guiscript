import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import Element

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
RESIZE = pygame.event.custom_type()
DRAG = pygame.event.custom_type()

SLIDESHOW_MOVE_LEFT = pygame.event.custom_type()
SLIDESHOW_MOVE_RIGHT = pygame.event.custom_type()

SLIDER_MOVE = pygame.event.custom_type()

SOUNDPLAYER_TOGGLE = pygame.event.custom_type()
SOUNDPLAYER_MUTE = pygame.event.custom_type()
SOUNDPLAYER_TRACK_MOVE = pygame.event.custom_type()
SOUNDPLAYER_VOLUME_MOVE = pygame.event.custom_type()
SOUNDPLAYER_END = pygame.event.custom_type()

VIDEOPLAYER_TOGGLE = pygame.event.custom_type()
VIDEOPLAYER_MUTE = pygame.event.custom_type()
VIDEOPLAYER_TRACK_MOVE = pygame.event.custom_type()
VIDEOPLAYER_VOLUME_MOVE = pygame.event.custom_type()
VIDEOPLAYER_END = pygame.event.custom_type()

DROPMENU_SELECT = pygame.event.custom_type()
DROPMENU_TOGGLE = pygame.event.custom_type()

SELECTIONLIST_SELECT = pygame.event.custom_type()
SELECTIONLIST_DESELECT = pygame.event.custom_type()

ANIMATION_END = pygame.event.custom_type()

ENTRY_CHANGE = pygame.event.custom_type()
ENTRY_FOCUS = pygame.event.custom_type()
ENTRY_UNFOCUS = pygame.event.custom_type()

TEXTBOX_CHANGE = pygame.event.custom_type()
TEXTBOX_FOCUS = pygame.event.custom_type()
TEXTBOX_UNFOCUS = pygame.event.custom_type()

WINDOW_CLOSE = pygame.event.custom_type()
WINDOW_DRAG = pygame.event.custom_type()
WINDOW_COLLAPSE = pygame.event.custom_type()

FILEDIALOG_CANCEL = pygame.event.custom_type()
FILEDIALOG_ENTER = pygame.event.custom_type()
FILEDIALOG_BACK = pygame.event.custom_type()
FILEDIALOG_OK = pygame.event.custom_type()
FILEDIALOG_CLOSE = pygame.event.custom_type()
FILEDIALOG_HOME = pygame.event.custom_type()

COLORPICKER_CHANGE = pygame.event.custom_type()


def _post_base_event(type_: int, element: "Element"):
    pygame.event.post(pygame.Event(type_, {
        "id": element.element_id,
        "element": element,
    }))


def _post_slideshow_event(mode: str, element: "Element"):
    pygame.event.post(pygame.Event(
        SLIDESHOW_MOVE_LEFT if mode == "left" else SLIDESHOW_MOVE_RIGHT,
        {
            "id": element.element_id,
            "element": element,
            "slideshow": element
        }
    ))


def _post_slider_event(old: float, new: float, element: "Element"):
    pygame.event.post(pygame.Event(SLIDER_MOVE, {
        "id": element.element_id,
        "element": element,
        "slider": element,
        "old_value": old,
        "old_percent": old*100,
        "value": new,
        "percent": new*100
    }))


def _post_sound_player_event(type_: int, element: "Element"):
    pygame.event.post(pygame.Event(type_, {
        "id": element.element_id,
        "element": element,
        "soundplayer": element,
        "playing": element.playing,
        "muted": element.muted,
        "paused": element.paused,
        "time_passed": element.get_time_passed(),
        "time_remaining": element.get_time_remaining(),
        "volume": element.get_volume()
    }))


def _post_video_player_event(type_: int, element: "Element"):
    pygame.event.post(pygame.Event(type_, {
        "id": element.element_id,
        "element": element,
        "videoplayer": element,
        "playing": element.playing,
        "muted": element.muted,
        "paused": element.paused,
        "time_passed": element.get_time_passed(),
        "time_remaining": element.get_time_remaining(),
        "volume": element.get_volume()
    }))


def _post_dropmenu_event(mode: str, element: "Element"):
    pygame.event.post(pygame.Event(
        DROPMENU_SELECT if mode == "select" else DROPMENU_TOGGLE,
        {
            "id": element.element_id,
            "element": element,
            "dropmenu": element,
            "selected_option": element.get_selected(),
            "selected": element.get_selected()
        }))


def _post_selectionlist_event(mode: str, element: "Element", option: str):
    pygame.event.post(pygame.Event(
        SELECTIONLIST_SELECT if mode == "select" else SELECTIONLIST_DESELECT,
        {
            "id": element.element_id,
            "element": element,
            "selectionlist": element,
            "selected": element.get_selected(),
            "option": option
        }))


def _post_animation_event(animation):
    pygame.event.post(pygame.Event(
        ANIMATION_END,
        {
            "animation": animation,
            "element": animation.element
        }
    ))
    

def _post_entry_event(mode:str, element: "Element"):
    pygame.event.post(pygame.Event(
        ENTRY_CHANGE if mode == "change" else ENTRY_FOCUS if mode == "focus" else ENTRY_UNFOCUS,
        {
            "id": element.element_id,
            "element": element,
            "entry": element,
            "text": element.get_text()
        }
    ))
    
def _post_textbox_event(mode:str, element: "Element"):
    pygame.event.post(pygame.Event(
        TEXTBOX_CHANGE if mode == "change" else TEXTBOX_FOCUS if mode == "focus" else TEXTBOX_UNFOCUS,
        {
            "id": element.element_id,
            "element": element,
            "textbox": element,
            "text": element.get_text()
        }
    ))
    
    
def _post_window_event(mode: str, element: "Element"):
    pygame.event.post(pygame.Event(
        WINDOW_CLOSE if mode == "close" else WINDOW_DRAG if mode == "drag" else WINDOW_COLLAPSE,
        {
            "id": element.element_id,
            "element": element,
            "window": element,
            "collapsed": element.collapsed
        }
    ))


def _post_filedialog_event(type: int, element: "Element"):
    pygame.event.post(pygame.Event(
        type,
        {
            "id": element.element_id,
            "element": element,
            "filedialog": element,
            "path": element.current_path,
            "selected": element.get_valid_selected()
        }
    ))
    

def _post_colorpicker_event(element: "Element"):
    pygame.event.post(pygame.Event(
        COLORPICKER_CHANGE,
        {
            "id": element.element_id,
            "element": element,
            "colorpicker": element,
            "color": element.color,
        }
    ))
