from . import animation
from . import error
from . import style
from . import components
from . import interact
from . import navigation
from . import status
from . import buffer
from .elements import root

AnimType = animation.UIAnimation
StyleAnimType = animation.UIStyleAnim
PropertyAnimType = animation.UIPropertyAnim

ErrorType = error.UIError
ScriptErrorType = error.UIScriptError

RootType = root.UIRoot
InteractType = interact.UIInteract
NavigationType = navigation.UINavigation

CompType = components.UIComponent
BGCompType = components.UIBackgroundComp
ImageCompType = components.UIImageComp
ShapeCompType = components.UIShapeComp
TextCompType = components.UITextComp
IconCompType = components.UIIconComp
OutlineCompType = components.UIOutlineComp

CompStyleType = style.UICompStyle
StackStyleType = style.UIStackStyle
BGStyleType = style.UIBGStyle
ImageStyleType = style.UIImageStyle
ShapeStyleType = style.UIShapeStyle
TextStyleType = style.UITextStyle
IconStyleType = style.UIIconStyle
OutlineStyleType = style.UIOutlineStyle
StyleObjType = style.UIStyle
StyleGroupType = style.UIStyleGroup
StyleHolderType = style.UIStyleHolder

StatusType = status.UIStatus
BuffersType = buffer.Buffers