import pygame
import typing

from .elements.element import UIElement
from .animation import UIAnimUpdater
from .tooltip import UITooltips
from .state import UIState
from . import common

VERSION = "WIP"


element: typing.TypeAlias = UIElement


def ZeroRect() -> pygame.Rect:
    """Return pygame.Rect(0, 0, 0, 0)"""
    return pygame.Rect(0, 0, 0, 0)


def SizeRect(width: int, height: int) -> pygame.Rect:
    """Return pygame.Rect(0, 0, width, height)"""
    return pygame.Rect(0, 0, width, height)


def PosRect(x: int, y: int) -> pygame.Rect:
    """Return pygame.Rect(x, y, 0, 0)"""
    return pygame.Rect(x, y, 0, 0)


def static_logic(delta_time: float = 1):
    """Update animations, tooltips and UIState which are static classes that can't be updated by UIManager"""
    UIState.delta_time = delta_time
    UIState.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    UIState.mouse_rel = pygame.Vector2(pygame.mouse.get_rel())
    UIState.mouse_pressed = pygame.mouse.get_pressed()
    UIState.keys_pressed = pygame.key.get_pressed()
    UIState.space_pressed = UIState.keys_pressed[pygame.K_SPACE]
    UIState.frame_count += 1
    UIAnimUpdater.logic()
    UITooltips.logic()
    

def help_element_types() -> typing.LiteralString:
    """Provide a help string about the element types structure for built in elements"""
    return """
    UIElement: (element, )
    Label: (element, label)
    Image: (element, image)
    Icon: (element, icon)
    Button: (element, label, button)
    ImageButton: (element, image, button, imagebutton)
    IconButton: (element, icon, button, iconbutton)
    Checkbox: (element, button, checkbox)
    HStack: (element, stack, hstack)
    VStack: (element, stack, vstack)
        HStack/VStack.vscrollbar: (element, scrollbar, vscrollbar)
            HStack/VStack.vscrollbar.handle: (element, handle, scrollbar_handle, vscrollbar_handle)
        HStack/VStack.hscrollbar: (element, scrollbar, hscrollbar)
            HStack/VStack.hscrollbar.handle: (element, handle, scrollbar_handle, hscrollbar_handle)
    Slider: (element, slider)
        Slider.bar: (element, slider_bar)
        Slider.handle: (element, handle, slider_handle)
    ProgressBar: (element, progressbar)
    GIF: (element, image, gif)
    Slideshow: (element, image, slideshow)
        Slideshow.left_arrow: (*Button, slideshow_arrow, slideshow_left_arrow)
        Slideshow.right_arrow: (*Button, slideshow_arrow, slideshow_right_arrow)
    SoundPlayer: (*HStack, player, soundplayer)
        SoundPlayer.track_slider: (*Slider, soundplayer_slider, soundplayer_track_slider)
        SoundPlayer.volume_slider: (*Slider, soundplayer_slider, soundplayer_volume_slider)
        SoundPlayer.play_button: (*Button, soundplayer_button, soundplayer_play_button)
        SoundPlayer.volume_button: (*Button, soundplayer_button, soundplayer_volume_button)
    VideoPlayer: (element, player, videoplayer)
        VideoPlayer.video_image: (*Image, videoplayer_video)
        VideoPlayer.control_stack: (*HStack, videoplayer_control_stack)
        VideoPlayer.track_slider: (*Slider, videoplayer_slider, videoplayer_track_slider)
        VideoPlayer.volume_slider: (*Slider, videoplayer_slider, videoplayer_volume_slider)
        VideoPlayer.play_button: (*Button, videoplayer_button, videoplayer_play_button)
        VideoPlayer.volume_button: (*Button, videoplayer_button, videoplayer_volume_button)
    DropMenu: (element, menu, dropmenu)
        DropMenu.option_button: (*Button, dropmenu_button, dropmenu_selected_option)
        DropMenu.arrow_button: (*Button, dropmenu_button, dropmenu_arrow)
        DropMenu.menu_cont: (*VStack, dropmenu_menu)
            DropMenu.menu_cont.*: (*Button, dropmenu_option)
    SelectionList: (*VStack, menu, selectionlist)
        SelectionList.*: (*Button, selectionlist_option)
    InvisElement: (element, invisible_element)
    HLine: (element, line, hline)
    VLine: (element, line, vline)
    """
    
    
def help_z_index() -> dict[str, int]:
    """Provide a help dictionary with default z index value for built in elements"""
    return common.Z_INDEXES
    
    
def help_style_script() -> typing.LiteralString:
    """Provide a help string with a guide for using the style scripring language"""
    return """

    """
    
def help_events() -> typing.LiteralString:
    """Provide a help string with events for each element"""
    return """
    UIElement:
        HOVERED
        PRESSED
        RIGHT_PRESSED
        START_HOVER
        START_PRESS
        START_RIGHT_PRESS
        STOP_HOVER
        STOP_RIGHT_PRESS
        SELECT
        DESELECT
        CLICK
        RIGHT_CLICK
        properties:
            id: str
            element_id: str
            element: UIElement
            obj: UIElement
    
    Slideshow:
        SLIDESHOW_MOVE_LEFT
        SLIDESHOW_MOVE_RIGHT
        extra properties:
            slideshow: Slideshow
            
    Slider:
        SLIDER_MOVE
        extra properties:
            slider: Slider
            old_value: float
            old_percent: float
            value: float
            percent: float
            
    SoundPlayer:
        SOUNDPLAYER_TOGGLE
        SOUNDPLAYER_MUTE
        SOUNDPLAYER_TRACK_MOVE
        SOUNDPLAYER_VOLUME_MOVE
        SOUNDPLAYER_END
        extra properties:
            soundplayer: SoundPlayer
            playing: bool
            muted: bool
            paused: bool
            time_passed: float
            time_remaining: float
            volume: float
            
    VideoPlayer:
        VIDEOPLAYER_TOGGLE
        VIDEOPLAYER_MUTE
        VIDEOPLAYER_TRACK_MOVE
        VIDEOPLAYER_VOLUME_MOVE
        VIDEOPLAYER_END
        extra properties:
            videoplayer: VideoPlayer
            playing: bool
            muted: bool
            paused: bool
            time_passed: float
            time_remaining: float
            volume: float
            
    DropMenu:
        DROPMENU_SELET
        DROPMENU_TOGGLE
        extra properties:
            dropmenu: DropMenu
            selected_option: str
            selected: str
            
    SelectionList:
        SELECTIONLIST_SELECT
        SELECTIONLIST_DESELECT
        extra properties:
            selectionlist: SelectionList
            selected: str|list[str]
            option: str
        
    """
    
def help_callbacks() -> typing.LiteralString:
    """Provide a help string with callbacks for each element"""
    return """
    UIElement:
        when_hovered
        when_pressed
        when_right_pressed
        on_start_hover
        on_start_press",
        on_start_right_press
        on_stop_hover
        on_stop_press
        on_stop_right_press
        on_select
        on_deselect
        on_click
        on_right_click
        on_move (used by few)
        args:
            [Optional] element: UIElement
            
    SoundPlayer|VideoPlayer:
        on_toggle
        on_mute
        on_volume_move
        on_track_move
    
    DropMenu:
        on_option_select
        on_menu_toggle
        extra args:
            option: str
        
    SelectionList:
        on_option_select
        on_option_deselect
        extra args:
            option: str
    """
    
def help_buffers() -> typing.LiteralString:
    """Provide a help string with buffers for each element"""
    return """
    UIElement: selected (sync with UIElement.status.selected)
    Slider: value (sync with Slider.get_value())
    """
