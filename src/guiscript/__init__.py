"""
User friendly, script based UI library for pygame graphical user interfaces.
The scripting is similar to CSS, the syntax is simple and the UI can be used for both applications and games.
The library offers lots of customization and helpful tools like callbacks, buffers, pygame events and built in animations.
The library comes with lots of default elements and styles that are easily expandable by the user.
It aims to be easy to use and pygame friendly with freedom of game loop.
It revolves around user responsible changes and good performance for games.
The elements structure is easy to follow thanks to the use of context managers.
Customization is easily accessible thanks to the styling, style priority and inheritance system.
"""
import pygame
from pygame import Rect as rect
pygame.init()

from ._guis.elements.element import Element
from ._guis.manager import Manager
from ._guis.icon import Icons
from ._guis.buffer import Buffer
from ._guis.tooltip import Tooltips

from ._guis.enums import (
    TextAlign, 
    FontAlign, 
    ShapeType,
    StyleType,
    ElementAlign,
    StackAnchor,
    SliderAxis,
    DropMenuDirection,
    ProgressBarDirection,
    AnimPropertyType,
    AnimRepeatMode,
    AnimEaseFunc,
    StyleAnimPropertyType,
    Resizer,
    Anchor
)

from ._guis.elements.factories import (
    Text, 
    Icon,
    Image,
    Button,
    ImageButton,
    IconButton,
    Checkbox,
    Slideshow,
    GIF,
    Slider,
    ProgressBar
)

from ._guis.elements.stacks import (VStack, HStack, Box)
from ._guis.elements.players import (SoundPlayer, VideoPlayer)
from ._guis.elements.menus import (DropMenu, SelectionList)
from ._guis.elements.windows import (Window, Modal, FileDialog)
from ._guis.elements.entries import (Entry, Textbox)
from ._guis.elements.extra import (ColorPicker, )

from ._guis.settings import (
    SlideshowSettings, 
    SliderSettings,
    SoundPlayerSettings,
    VideoPlayerSettings,
    ProgressBarSettings,
    DropMenuSettings,
    SelectionListSettings,
    EntrySettings,
    TextboxSettings,
    WindowSettings,
    FileDialogSettings,
    ModalSettings,
    ColorPickerSettings
)

from ._guis.utils import (
    VERSION,
    ALL_RESIZERS,
    ANCHOR_PARENT,
    NO_SOUND,
    EXTENSION_FOLDER,
    bind_one_selected_only,
    custom_hscrollbar,
    custom_vscrollbar,
    row,
    column,
    invis_element,
    hline,
    vline,
    static_dock,
    dragging_mouse,
    static_logic,
    ZeroRect,
    SizeRect,
    PosRect,
    quick_style,
    set_default_style_id,
    DefaultStyleID,
    get_builtin_image,
    get_current_manager,
    get_current_parent,
    ZeroRect as ZeroR,
    SizeRect as SizeR,
    PosRect as PosR
)

from ._guis.help import (
    help_element_types,
    help_style_script,
    help_z_index,
    help_navigation,
    help_buffers,
    help_rich_text,
    help_events,
    help_callbacks
)

from ._guis.types import (
    AnimType,
    StyleAnimType,
    PropertyAnimType,
    ErrorType,
    ScriptErrorType,
    RootType,
    InteractType,
    NavigationType,
    CursorsType,
    CompType,
    BGCompType,
    ImageCompType,
    ShapeCompType,
    TextCompType,
    IconCompType,
    OutlineCompType,
    CompStyleType,
    StackStyleType,
    BGStyleType,
    ImageStyleType,
    ShapeStyleType,
    TextStyleType,
    IconStyleType,
    OutlineStyleType,
    StyleObjType,
    StyleGroupType,
    StyleHolderType,
    StatusType,
    BuffersType,
    SoundsType,
    StackType,
    ScrollbarType,
    VScrollbarType,
    HScrollbarType
)

from ._guis.events import *

print(f"Guiscript {VERSION}")
_guis = None
