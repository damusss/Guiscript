from . import animation
from . import error
from . import style
from . import components
from . import interact
from . import navigation
from . import status
from . import buffer
from . import cursors
from .elements import stacks
from .elements import scrollbars
from .elements import root

type AnimType = animation.UIAnimation
type StyleAnimType = animation.UIStyleAnim
type PropertyAnimType = animation.UIPropertyAnim

type ErrorType = error.UIError
type ScriptErrorType = error.UIScriptError

type RootType = root.UIRoot
type InteractType = interact.UIInteract
type NavigationType = navigation.UINavigation
type CursorsType = cursors.UICursors

type CompType = components.UIComponent
type BGCompType = components.UIBackgroundComp
type ImageCompType = components.UIImageComp
type ShapeCompType = components.UIShapeComp
type TextCompType = components.UITextComp
type IconCompType = components.UIIconComp
type OutlineCompType = components.UIOutlineComp

type CompStyleType = style.UICompStyle
type StackStyleType = style.UIStackStyle
type BGStyleType = style.UIBGStyle
type ImageStyleType = style.UIImageStyle
type ShapeStyleType = style.UIShapeStyle
type TextStyleType = style.UITextStyle
type IconStyleType = style.UIIconStyle
type OutlineStyleType = style.UIOutlineStyle
type StyleObjType = style.UIStyle
type StyleGroupType = style.UIStyleGroup
type StyleHolderType = style.UIStyleHolder

type StatusType = status.UIStatus
type BuffersType = buffer.Buffers

type StackType = stacks.UIStack
type ScrollbarType = scrollbars.UIScrollbar
type VScrollbarType = scrollbars.UIVScrollbar
type HScrollbarType = scrollbars.UIHScrollbar
