import typing
from .  import common

def help_element_types() -> typing.LiteralString:
    """Provide a help string about the element types structure for built in elements"""
    return """
    Element: (element, )
    Text: (element, text)
    Image: (element, image)
    Icon: (element, icon)
    Button: (element, text, button)
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
        
    SoundPlayer(HStack): (*HStack, player, soundplayer)
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
            
    SelectionList(VStack): (*VStack, menu, selectionlist)
        SelectionList.*: (*Button, selectionlist_option)
    
    Entry(VStack): (*VStack, entry)
        Entry.text_element: (*Text, entry_text)
        
    Textbox(VStack): (*VStack, textbox)
        Textbox.text_element: (*Text, entry_text)
        
    Window: (element, window)
        Window.title_bar: (*HStack, window_title_bar)
            Window.title: (*Button, window_title)
            ?Window.close_button: (*Button, window_close_button)
            ?Window.collapse_button: (*Button, window_collapse_button)
        Window.content: (*VStack, window_content)
        
    FileDialog(Window): (*Window, filedialog)
        FileDialog.top_row_cont: (*HStack, filedialog_row, filedialog_top_row)
            FileDialog.home_button: (*Button, filedialog_button, filedialog_home_button)
            FileDialog.back_button: (*Button, filedialog_button, filedialog_back_button)
            FileDialog.path_entry: (*Entry, filedialog_path_entry)
        FileDialog.selectionlist: (*SelectionList, filedialog_selectionlist)
        FileDialog.bottom_row_cont: (*HStack, filedialog_row, filedialog_bottom_row)
            FileDialog.enter_button: (*Button, filedialog_button, filedialog_enter_button)
            FileDialog.cancel_button: (*Button, filedialog_button, filedialog_cancel_button)
            FileDialog.ok_button: (*Button, filedialog_button, filedialog_ok_button)
        
    ModalContainer(VStack): (*VStack, modal_container)
        ModalContainer.modal_element: any
        
    ColorPicker(VStack): (*VStack, colorpicker)
        ?ColorPicker.preview_image: (*Image, colorpicker_preview, colorpicker_preview_image)
        ColorPicker.row_r: (*HStack, colorpicker_row, colorpicker_row_r)
            ColorPicker.slider_r: (*Slider, colorpicker_slider, colorpicker_slider_r)
            ColorPicker.entry_r: (*Entry, colorpicker_entry, colorpicker_entry_r)
            ColorPicker.preview_r: (*Image, colorpicker_preview, colorpicker_preview_r)
        ColorPicker.row_g: (*HStack, colorpicker_row, colorpicker_row_g)
            ColorPicker.slider_g: (*Slider, colorpicker_slider, colorpicker_slider_g)
            ColorPicker.entry_g: (*Entry, colorpicker_entry, colorpicker_entry_g)
            ColorPicker.preview_g: (*Image, colorpicker_preview, colorpicker_preview_g)
        ColorPicker.row_b: (*HStack, colorpicker_row, colorpicker_row_b)
            ColorPicker.slider_b: (*Slider, colorpicker_slider, colorpicker_slider_b)
            ColorPicker.entry_b: (*Entry, colorpicker_entry, colorpicker_entry_b)
            ColorPicker.preview_b: (*Image, colorpicker_preview, colorpicker_preview_b)
        ?ColorPicker.row_a: (*HStack, colorpicker_row, colorpicker_row_a)
            ?ColorPicker.slider_a: (*Slider, colorpicker_slider, colorpicker_slider_a)
            ?ColorPicker.entry_a: (*Entry, colorpicker_entry, colorpicker_entry_a)
            ?ColorPicker.preview_a: (*Image, colorpicker_preview, colorpicker_preview_a)
        ?ColorPicker.hex_entry: (*Entry, colorpicker_entry, colorpicker_hex_entry)
        
    row -> (*HStack, row)
    column -> (*VStack, column)
    invis_element -> (element, invisible_element)
    hline -> (element, line, hline)
    vline -> (element, line, vline)
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
    The image's image can also be a string like 'builtin.X' where X is a built in image. To check weather a builtin image exists
    run the get_builtin_image function (will also say all the available on error).
    
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
        fill_color: Color Fill all pixels with the specified color
        alpha: number 0-255 Extra alpha modifier

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
        rich_modifiers: bool Extension of rich text not to automatically parse html tags but to use modifiers. It's preferred to avoid this setting as it's complex to use

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
        resize, resize_x, resize_y: apply both grow and shrink stack properties for the specified axis
    
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
            
    Textbox:
        TEXTBOX_CHANGE
        TEXTBOX_FOCUS
        TEXTBOX_UNFOCUS
        extra properties:
            textbox: Textbox
            text: str
            
    Window:
        WINDOW_CLOSE
        WINDOW_DRAG
        WINDOW_COLLAPSE
        extra properties:
            window: Window
            collapsed: bool
            
    FileDialog(Window)
        FILEDIALOG_CLOSE
        FILEDIALOG_HOME
        FILEDIALOG_BACK
        FILEDIALOG_ENTER
        FILEDIALOG_CANCEL
        FILEDIALOG_OK
        extra properties:
            filedialog: FileDialog
            path: pathlib.Path
            selected: list[pathlib.Path]
            
    ColorPicker:
        COLORPICKER_CHANGE
        extra properties:
            colorpicker: ColorPicker
            color: Color
        
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
            
    Textbox:
        on_change
        on_focus
        on_unfocus
        extra args:
            text: str
            
    Window:
        on_close
        on_collapse
        
    FileDialog(Window):
        on_back
        on_home
        on_enter
        on_cancel
        on_ok
        extra args:
            selected: list[pathlib.Path]
            
    ColorPicker:
        on_change
        extra args:
            color: Color
    """


def help_buffers() -> typing.LiteralString:
    """Provide a help string with buffers for each element"""
    return """
    Element: selected (sync with Element.status.selected)
    Slider: value (sync with Slider.get_value())
    Entry: text (sync with Entry.get_text())
    Textbox: text (sync with Textbox.get_text())
    ColorPicker: color (sync with ColorPicker.color)
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
