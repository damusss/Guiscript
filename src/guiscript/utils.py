import pygame
import typing
import random
import string
import warnings
if typing.TYPE_CHECKING:
    from .elements.element import Element

from .animation import UIAnimUpdater
from .tooltip import Tooltips
from .state import UIState
from .error import UIError
from .script import UIScript
from . import common
from . import strimages
from . import enums

VERSION: str = "WIP"
ALL_RESIZERS: tuple[enums.Resizer] = (enums.Resizer.top,
                                      enums.Resizer.bottom,
                                      enums.Resizer.left,
                                      enums.Resizer.right,
                                      enums.Resizer.topleft,
                                      enums.Resizer.topright,
                                      enums.Resizer.bottomleft,
                                      enums.Resizer.bottomright)
ANCHOR_PARENT: str = "parent"

def static_dock(root: "Element", ids_elements: list[tuple[int, "Element"]], ids_root_anchors: list[tuple[int, enums.DockAnchor]], ids_connection_ids: list[tuple[int, enums.DockConn, int]]):
    """
    Automatically sets up anchors for static docking.\n
    root is the background panel element of the docking\n
    ids_elements should look like this: [(1, element_1), (2, element_2), (3, element_3)...] when you use '1' or '2'.. the corrisponding object will be used\n
    ids_root_anchors tells how the elements are anchored to the root for example [(1, "topleft"), (3, "bottomright")...] (you don't need to specify for all) use the DockAnchor enum for the available anchors\n
    ids_connection_ids tells how the elements are connected between each other. it should looks like this [(1, connection, 2), (2, connection, 3)...] (you don't need to specify for all)\n
    The possible connections are the following (available with the DockConn enum):\n
    - <x> (DockConn.l_x_r) element 1 is anchored to element 2 and element 2 is anchored to element 1, where element 1 is on the left and element 2 on the right\n
    - <y> (DockConn.t_y_b) element 1 is anchored to element 2 and element 2 is anchored to element 1, where element 1 is on the top and element 2 on the bottom\n
    - x> (DockConn.x_r) only element 1 is anchored to element 2 where element 1 is on the left and element 2 on the right\n
    - <x (DockConn.l_x) only element 2 is anchored to element 1 where element 1 is on the left and element 2 on the right\n
    - y> (DockConn.y_b) only element 1 is anchored to element 2 where element 1 is on the top and element 2 on the bottom\n
    - <y (DockConn.t_y) only element 2 is anchored to element 1 where element 1 is on the top and element 2 on the bottom\n
    """
    id_els = {id_:el for id_, el in ids_elements}
    for id_, an in ids_root_anchors:
        if id_ not in id_els:
            raise UIError(f"Docking failed. Element with id '{id_}' was not registered in the elements '{ids_elements}'")
        element = id_els[id_]
        if an in ["left", "right"]:
            element.set_anchor(root, an, an)
        elif an in ["top", "bottom"]:
            element.set_anchor(root, an, an)
        elif an.startswith("top"):
            element.set_anchors((root, "top", "top"), (root, an.replace("top", ""), an.replace("top", "")))
        elif an.startswith("bottom"):
            element.set_anchors((root, "bottom", "bottom"), (root, an.replace("bottom", ""), an.replace("bottom", "")))
        elif an.startswith("left"):
            element.set_anchors((root, "left", "left"), (root, an.replace("left", ""), an.replace("left", "")))
        elif an.startswith("right"):
            element.set_anchors((root, "right", "right"), (root, an.replace("right", ""), an.replace("right", "")))
        else:
            common.warn(f"Skipping invalid dock anchor '{an}'")
    for id1, conn, id2 in ids_connection_ids:
        if id1 not in id_els:
            raise UIError(f"Docking failed. Element with id '{id_}' was not registered in the elements '{ids_elements}'")
        if id2 not in id_els:
            raise UIError(f"Docking failed. Element with id '{id_}' was not registered in the elements '{ids_elements}'")
        e1 = id_els[id1]
        e2 = id_els[id2]
        if conn == "<x>":
            e1.set_anchor(e2, "right", "left")
            e2.set_anchor(e1, "left", "right")
        elif conn == "<y>":
            e1.set_anchor(e2, "bottom", "top")
            e2.set_anchor(e1, "top", "bottom")
        elif conn == "x>":
            e1.set_anchor(e2, "right", "left")
        elif conn == "<x":
            e2.set_anchor(e1, "left", "right")
        elif conn == "y>":
            e1.set_anchor(e2, "bottom", "top")
        elif conn == "<y":
            e2.set_anchor(e1, "top","bottom")
        else:
            common.warn(f"Skipping invalid dock connection '{conn}'")

def dragging_mouse() -> bool:
    """Return whether the mouse is being dragged"""
    return UIState.mouse_rel.length() > 0


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
    Tooltips._logic()


def quick_style(style_source: str, gss_variables: dict = None) -> str:
    """Parse a style source replacing 'ID' with a new random id and return it to assign to an element. If no variables are provided the current manager ones will be used"""
    if gss_variables is None:
        if UIState.current_manager is not None:
            gss_variables = UIState.current_manager.gss_variables
        else:
            gss_variables = {}
    ID: str = ""
    for i in range(30):
        ID += random.choice(string.ascii_lowercase+string.ascii_uppercase+"_")
    if not "ID" in style_source:
        raise UIError(
            f"Source of quick style should include 'ID' for the style name, that will be later replaced with the actual id (in this case '{ID}')")
    style_source = style_source.replace("ID", ID)
    UIScript.parse_source(style_source, f"quickstyle.ID:{ID}.gss", gss_variables)
    return ID


def set_default_style_id(style_id: str | None):
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
        self.previous_style_id: str | None = UIState.current_style_id

    def __enter__(self, *args):
        self.previous_style_id: str = UIState.current_style_id
        UIState.current_style_id = self.style_id
        return self

    def __exit__(self, *args):
        UIState.current_style_id = self.previous_style_id


def get_builtin_image(name: str) -> pygame.Surface:
    """Return the surface of a builtin image for UI, or raise an error if it doesnt exist."""
    if name not in strimages.STRING_IMAGES_SURFACES.keys():
        raise UIError(f"Builtin image '{name}' does not exist. Available are {list(strimages.STRING_IMAGES_SURFACES.keys())}")
    return strimages.STRING_IMAGES_SURFACES[name]


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
    
    Entry: (*HStack, entry)
        Entry.text_element: (*Label, entry_text)
        
    Window: (element, window)
        Window.title_bar: (*HStack, window_title_bar)
            Window.title: (*Button, window_title)
            ?Window.close_btn: (*Button, window_close_button)
            ?Window.collapse_btn: (*Button, window_collapse_button)
        Window.content: (*VStack, window_content)
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
    A special font with icons is available with font name 'googleicons'
    
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
        cursor_color: Color
        cursor_width: number
        cursor_rel_h: number
        cursor_enabled: bool
        rich: bool Enable rich text. Use html tags for localized styling while the text style properties will act as defaults. More with guiscript.help_rich_text()

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

    There is also a few built in style ids:
        entry_disabled_text: used by the entry to change style for the placeholder
        active_cont: make a default-disabled-style element active again in terms of style
        invis_cont/invisible_container: simple way to make stacks invisible and without padding
        invisible: extends invis_cont to make any style invisible
        icons_font: set the font name to the special 'googleicons' and font size to 30
        no_scroll: quick way to set both scroll_x and scroll_y to false
        no padding: set all the component paddings to 0
        fill, fill_x, fill_y: shortcuts for space filling elements as they are used a lot
        inactive: default dark bg color
    
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
        DRAG
        RESIZE
        properties:
            id: str
            element: Element
    
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
            
    Entry:
        ENTRY_CHANGE
        ENTRY_FOCUS
        ENTRY_UNFOCUS
        extra properties:
            entry: Entry
            text: str
            
    Window:
        WINDOW_CLOSE
        WINDOW_DRAG
        WINDOW_COLLAPSE
        extra properties:
            window: Window
            collapsed: bool
        
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
        on_text_selection_change
        on_position_change
        on_style_change
        on_size_change
        on_build
        on_resize
        on_drag
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
            
    Entry:
        on_change
        on_focus
        on_unfocus
        extra args:
            text: str
            
    Window:
        on_close
        on_collapse
    """


def help_buffers() -> typing.LiteralString:
    """Provide a help string with buffers for each element"""
    return """
    Element: selected (sync with Element.status.selected)
    Slider: value (sync with Slider.get_value())
    Entry: text (sync with Entry.get_text())
    """


def help_navigation() -> typing.LiteralString:
    """Provide a help string with keyboard navigation keybinds"""
    return """
    Exit: ESC
    Start: TAB
    Next Element: TAB
    Previous Element: LSHIFT+TAB
    First Child: ENTER
    Parent: UP
    Interact: SPACE
    """
    
def help_rich_text() -> typing.LiteralString:
    """Provide a help string with rich text tags"""
    return """
    The other text style properties will act as defaults.
    Rich text (html-like string) tags: (case unsensitive, shorter alias)
    - <b / bold> -> bold
    - <i / italic> -> italic
    - <u / underline> -> underline
    - <s / strike / striketrough> -> striketrough
    - <a / antialas / antialiasing> -> antialiasing
    - <f / font size=FontSize> -> font size, where FontSize is a number
    - <f / font name=FontName> -> font name, where FontName is a string
    - <c / color fg=ColorValue> -> fg color, where ColorValue is a value supported by pygame
    - <c / color bg=ColorValue> -> bg color, where ColorValue is a value supported by pygame
    """
