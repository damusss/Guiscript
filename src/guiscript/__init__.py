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
import pygame
from pygame import Rect as rect
pygame.init()

from .elements.element import UIElement
from .manager import UIManager
from .elements.root import UIRoot
from .script import UIScript
from .icon import UIIcons
from .buffer import UIBuffer
from .tooltip import UITooltips
from .animation import (
    UIPropertyAnim
)
from .components import (
    UIBackgroundComp, 
    UIShapeComp, 
    UITextComp, 
    UIOutlineComp, 
    UIComponent
)
from .error import (
    UIError, 
    UIScriptError
)
from .style import (
    UICompStyle,
    UIBGStyle,
    UIImageStyle,
    UIShapeStyle,
    UITextStyle,
    UIOutlineStyle,
    UIStyle,
    UIStyleGroup
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
from .elements.stacks import (
    VStack,
    HStack
)
from .elements.players import (
    SoundPlayer,
    VideoPlayer
)
from .elements.menus import (
    DropMenu, 
    SelectionList
)
# from .elements.windows import (Window, FileDialog)
# from .elements.entries import (EntryLine, TextBox)
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
from .utils import (
    VERSION,
    element,
    static_logic,
    ZeroRect,
    SizeRect,
    PosRect,
    help_element_types,
    help_style_script,
    help_z_index,
    ZeroRect as ZeroR,
    SizeRect as SizeR,
    PosRect as PosR
)
from .events import *
print(f"Guiscript {VERSION}")
