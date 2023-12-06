"""
User friendly, script based UI library for pygame graphical user interfaces.
The scripting is similar to CSS, the syntax is simple and the UI can be used for both applications and games.
The library offers lots of customization and helpful tools like callbacks, buffers, pygame events and built in animations.
The library comes with lots of default elements and styles that are easily expandable by the user.
It aims to be easy to use and pygame friendly with freedom of game loop.
It revolves around user responsible changes and good performance for games.
The elements structure is easy to follow thanks to the use of context managers.
Customization is easily accessible thanks to the styling and style priority and inheritance system.
"""
from .events import *
from .types import (
    AnimType,
    StyleAnimType,
    PropertyAnimType,
    ErrorType,
    ScriptErrorType,
    RootType,
    InteractType,
    NavigationType,
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
    StackType,
    ScrollbarType,
    VScrollbarType,
    HScrollbarType
)
from .utils import (
    VERSION,
    static_logic,
    ZeroRect,
    SizeRect,
    PosRect,
    quick_style,
    set_default_style_id,
    DefaultStyleID,
    help_element_types,
    help_style_script,
    help_z_index,
    ZeroRect as ZeroR,
    SizeRect as SizeR,
    PosRect as PosR
)
from .settings import (
    SlideshowSettings,
    SlideshowDefaultSettings,
    SliderSettings,
    SliderDefaultSettings,
    SoundPlayerSettings,
    SoundPlayerDefaultSettings,
    VideoPlayerSettings,
    VideoPlayerDefaultSettings,
    ProgressBarSettings,
    ProgressBarDefaultSettings,
    DropMenuSettings,
    DropMenuDefaultSettings,
    SelectionListSettings,
    SelectionListDefaultSettings
)
from .elements.menus import (
    DropMenu,
    SelectionList
)
from .elements.players import (
    SoundPlayer,
    VideoPlayer
)
from .elements.stacks import (
    VStack,
    HStack
)
from .elements.factories import (
    Label,
    Icon,
    Image,
    Button,
    ImageButton,
    IconButton,
    Checkbox,
    Slideshow,
    GIF,
    Slider,
    ProgressBar,
    InvisElement,
    HLine,
    VLine
)
from .enums import (
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
    StyleAnimPropertyType
)
from .tooltip import Tooltips
from .buffer import Buffer
from .icon import Icons
from .manager import Manager
from .elements.element import Element
import pygame
from pygame import Rect as rect
pygame.init()

# from .elements.windows import (Window, FileDialog)
# from .elements.entries import (EntryLine, TextBox)
print(f"Guiscript {VERSION}")
