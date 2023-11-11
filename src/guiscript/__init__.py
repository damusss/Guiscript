import pygame
from pygame import Rect as rect
pygame.init()

from .common import VERSION
from .elements.element import UIElement
from .manager import UIManager
from .elements.root import UIRoot
from .state import UIState
from .script import UIScript
from .icon import UIIcons
from .buffer import UIBuffer
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
    UIStyleHolder,
    UIStyleGroup,
    UIStyles
)
from .enums import (
    TextAlign, 
    FontAlign, 
    ShapeType,
    StyleType,
    StyleTarget,
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
    #ProgressBar
)
from .elements.stacks import (
    VStack,
    HStack
)
from .elements.players import (
    SoundPlayer,
    VideoPlayer
)
# from .elements.menus import (DropMenu, SelectionList)
# from .elements.windows import (Window, FileDialog)
# from .elements.entries import (EntryLine, TextBox)
# from .animation import ()
from .settings import (
    SlideshowSettings, 
    SlideshowDefaultSettings,
    SliderSettings,
    SliderDefaultSettings,
    SoundPlayerSettings,
    SoundPlayerDefaultSettings,
    VideoPlayerSettings,
    VideoPlayerDefaultSettings
)
from .utils import (
    element,
    ZeroRect,
    SizeRect,
    PosRect,
    ZeroRect as ZeroR,
    SizeRect as SizeR,
    PosRect as PosR
)
from .events import *
