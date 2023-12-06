import pygame
import typing
import random
import string

from .elements.element import Element
from .animation import UIAnimUpdater
from .tooltip import Tooltips
from .state import UIState
from .error import UIError
from .script import UIScript
from . import common

VERSION = "WIP"


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
    """Update animations, tooltips and UIState which are static classes that can't be updated by Manager"""
    UIState.delta_time = delta_time
    UIState.mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    UIState.mouse_rel = pygame.Vector2(pygame.mouse.get_rel())
    UIState.mouse_pressed = pygame.mouse.get_pressed()
    UIState.keys_pressed = pygame.key.get_pressed()
    UIState.space_pressed = UIState.keys_pressed[pygame.K_SPACE]
    UIState.frame_count += 1
    UIAnimUpdater.logic()
    Tooltips.logic()


def quick_style(style_source: str, gs_variables: dict = None) -> str:
    """Parse a style source replacing 'ID' with a new random id and return it to assign to an element. If no variables are provided the current manager ones will be used"""
    if gs_variables is None:
        if UIState.current_manager is not None:
            gs_variables = UIState.current_manager.gs_variables
        else:
            gs_variables = {}
    ID: str = ""
    for i in range(30):
        ID += random.choice(string.ascii_lowercase+string.ascii_uppercase+"_")
    if not "ID" in style_source:
        raise UIError(
            f"Source of quick style should include 'ID' for the style name, that will be later replaced with the actual id (in this case '{ID}')")
    style_source = style_source.replace("ID", ID)
    UIScript.parse_source(style_source, f"quickstyle.ID:{ID}.gss", gs_variables)
    return ID


def default_style_id(style_id: str|None):
    """
    Set the default style id for the next elements. NOTE: exiting the DefaultStyleID context manager might override this call
    
    Next elements will add their style id to this default one
    """
    UIState.current_style_id = style_id
    
    
class DefaultStyleID:
    """
    Context manager to set a default style id for the next elements. Will go back to the previous one on exit
    
    Next elements will add their style id to this default one
    """
    def __init__(self, style_id: str):
        self.style_id: str = style_id
        self.previous_style_id: str|None = UIState.current_style_id
        
    def __enter__(self, *args):
        self.previous_style_id: str = UIState.current_style_id
        UIState.current_style_id = self.style_id
        return self
    
    def __exit__(self, *args):
        UIState.current_style_id = self.previous_style_id


def help_element_types() -> typing.LiteralString:
    """Provide a help string about the element types structure for built in elements"""
    return """
    Element: (element, )
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
    A gss (short for gui script style) can be a file or a python string
    A gss is composed of 1 or more "style blocks"
    The style blocks get parsed and for each one a style holder python object will be created
    When an element "asks" for the style group, the style manager will find all the style holders/blocks that match the element signature and apply them
    
    Applying them means that the "first" style will be overrided with all the matching style holders, in order of creation and importance
    The importance follows the following rules:
        first the style holders pointing at the element types
        then the style holders pointing at the element style ID
        and lastly the style holders pointing at the element ID
    
    At the start of the style block you need to specify if it's for an element type, a style ID or an element ID
    '.' indicates it's for style ID
    '#' indicates it's for element ID
    no symbol means it's for an element type
    then you need to specify the names of the target, 1 or more, separated by a comma
    example: '.style_id_1, style_id_2'
    after the target name, you need to specify if it's for normal style, hover style or press style
    ':press' means it's for press
    ':hover' means it's for hover
    ':hover:press/:press:hover' means both press and both hover
    no style type specification indicates it's for normal style
    '::' means it's for both normal, hover and press style
    
    After this syntax you need to put curly braces '{...}' inside which you put the style instructions. ';' separates style instructions
    A style instruction can be a static property or an animation.
    A style property is written like so:
        COMP_NAME.PROPERTY_NAME VALUE;
    A style animation is written like so:
        % COMP_NAME.PROPERTY_NAME VALUE, DURATION, EASE_FUNCTION_NAME;
        where the ease function name is optional
        important: not all property names support animations, only numbers and colors do!
    
    The value must match the expected value (should be understandable from the name, otherwise check the end of this guide) otherwise pygame errors will be raised
    A value can be:
        a string: either a concatenation of word (lime green) or any text sorrounded by single quotes 'example.png'
        a number (1, 2.5)
        an hex number (#AABBCC where a, b, c must be letters A->F or numbers 0->9)
        a variable: written like $VAR_NAME, will use the variable passed to the manager when parsing the style
        a list: a collection of other values sorrounded by parenthesis ('ciao', 12)
        a python expression: any valid python expression sorrounded by ||, you can use variables. Example: |3*VAR_NAME|
    Properties that expect surfaces or fonts will try to load them if a string is provided
    
    AVAILABLE COMPONENTS AND PROPERTIES
    
    stack:
        spacing: number
        padding: number
        scroll_x: bool Scrolling enabled on X
        scroll_y: bool Scrolling enabled on Y
        grow_x: bool Grow to the content size on X
        grow_y: bool Grow to the content size on Y
        shrink_x: bool Shrink to the content size on X
        shrink_y: bool Shrink to the content size on Y
        fill_x: bool Resize itself to be as big as possible inside a stack on X
        fill_y: bool Resize itself to be as big as possible inside a stack on Y
        floating_scrollbars: bool Scrollbars will occupy physical space
        anchor: StackAnchor(string enum) How to align elements on the axis of the stack when the content size is smaller than the stack size on the stack axis
        align: ElementAlign(string enum) How to align itself in the opposite axis of the parent stack
        scrollbar_size: number
        mask_padding: number Padding around the element borders where children won't be visible

    bg:
        color: Color
        border_radius: number

    image:
        image: Surface|path|None
        padding: number
        border_radius: number
        stretch_x: bool Sacrifice the image ratio to fit on the X
        stretch_y: bool Sacrifice the image ratio to fit on the Y
        fill: bool Occupy all the space possible keeping the aspect ratio
        border_size: number Size of the border to preserve while scaling the inside of the image to fit all the space on any aspect ratio
        border_scale: number When border_size > 0, the scale to multiply said border
        outline_width: number Outline outlinining the image
        outline_color: Color

    shape:
        color: Color
        outline_width: number If 0, fill the shape
        type: ShapeType(string enum) rect, circle, ellips, polygon
        padding: number
        rect_border_radius: number Only for rect
        polygon_points: list[list[number, number]] Points relative to the element center, only for polygon
        ellipse_padding_x: number Only for ellipse
        ellipse_padding_y: number Only for ellipse

    text:
        text: string Will override the text given in code
        color: Color
        selection_color: Color
        bg_color: Color|None
        padding: number
        y_padding: number
        align: TextAlign(string enum) Anchor of the text relative to the element
        antialas: bool
        font_name: string|path|None String for sysfont, path|None for normal font. Special font: googleicons for easy to use icons
        font_size: number
        sysfont: bool System font or font from memory
        font_align: int Pygame constant for aligning when wrapping, check FONT_LEFT, FONT_RIGHT, FONT_CENTER
        bold: bool
        italic: bool
        underline: bool
        strikethrough: bool
        do_wrap: bool Wrap the font to fit in the element width
        grow_x: bool Increase the element width if necessary
        grow_y: bool Increase the element height if necessary

    icon:
        name: string
        scale: number
        padding: number
        align: TextAlign(string enum) Anchor of the icon relative to the element

    outline:
        color: Color
        width: number
        border_radius: number
        navigation_color: Color Outline color when the element is keyboard-navigated

    
    Have fun styling your elements!
    """


def help_events() -> typing.LiteralString:
    """Provide a help string with events for each element"""
    return """
    ANIMATION_END
        properties:
            animation: UIPropertyAnimation
            element: Element

    Element:
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
            element: Element
            obj: Element
    
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
    Element:
        when_hovered
        when_pressed
        when_right_pressed
        on_start_hover
        on_start_press
        on_start_right_press
        on_stop_hover
        on_stop_press
        on_stop_right_press
        on_select
        on_deselect
        on_click
        on_right_click
        on_frame_start
        on_animation_end (property animation)
        on_move (used by few)
        args:
            [Optional] element: Element
            
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
    Element: selected (sync with Element.status.selected)
    Slider: value (sync with Slider.get_value())
    """
