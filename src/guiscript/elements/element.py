import pygame
import typing
if typing.TYPE_CHECKING:
    from ..manager import UIManager
    from .root import UIRoot

from ..state import UIState
from ..error import UIError
from ..status import UIStatus
from ..buffer import UIBuffers
from ..tooltip import UITooltips
from ..animation import UIPropertyAnim
from ..style import UIStyleGroup, UIStyles, UIStyle
from ..enums import AnimRepeatMode, AnimEaseFunc, AnimPropertyType
from .. import components as comps
from .. import common


class UIElement:
    """
    Base class for elements\n
    Use the generator syntax 'with element:...' to set it as the current parent

    relative_rect -> set the starting position and size\n
    element_id -> custom element identifier for styles and events\n
    style_id -> custom style group id to set the style\n
    element_types -> tuple of types the element is used for styles\n
    parent -> the element parent or optionally None if you are in a context manager\n
    ui_manager -> the manager the element is bound to or optionally None if there is a current manager\n
    """

    def __init__(self,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 element_types: str = ("element",),
                 parent: "UIElement" = None,
                 ui_manager: "UIManager" = None,
                 ):

        # parameters
        self.relative_rect: pygame.Rect = relative_rect
        self.ui_manager: "UIManager" = ui_manager or UIState.current_manager

        # None checking
        if self.ui_manager is None:
            raise UIError(
                f"Element ui manager can't be None. Make sure to give a valid ui_manager parameter or set the correct current manager")

        self.parent: UIElement | "UIRoot" = parent or UIState.current_parent or self.ui_manager.root
        self.ui_manager.all_elements.append(self)

        if self.relative_rect is None:
            raise UIError(
                f"Element relative rect can't be None. Make sure to give a valid relative_rect parameter")

        if self.parent is None:
            raise UIError(
                "Element parent can't be None. Make sure to give a valid parent parameter or set the corrent current parent")

        # str attrs
        self.element_id: str = element_id
        self.style_id: str = style_id
        self.element_types: tuple[str] = element_types
        self.update_types_override()

        # attrs
        self.children: list[UIElement] = []
        self.ghost_element: UIElement | None = None
        self.element_surface: pygame.Surface = pygame.Surface(
            self.relative_rect.size, pygame.SRCALPHA)
        self.absolute_rect: pygame.Rect = self.relative_rect.copy()
        self.static_rect: pygame.Rect = self.relative_rect.copy()
        self.ignore_stack: bool = False
        self.ignore_scroll: bool = False
        self.can_destroy: bool = True
        self.z_index: int = common.Z_INDEXES["element"]
        self.scroll_offset: pygame.Vector2 = pygame.Vector2()
        self.update_absolute_rect_pos()

        # obj attrs
        self.status: UIStatus = UIStatus(self)
        self.buffers: UIBuffers = UIBuffers(self)
        self.visible: bool = True
        self.active: bool = True
        self._last_style: UIStyle = None
        self.style_group: UIStyleGroup = UIStyles.get_style_group(self)
        self.style: UIStyle = self.style_group.style

        # components
        self.callback_component: comps.UIComponent = comps.UIComponent(
            self, self.style_changed)
        self.bg: comps.UIBackgroundComp = comps.UIBackgroundComp(self)
        self.image: comps.UIImageComp = comps.UIImageComp(self)
        self.shape: comps.UIShapeComp = comps.UIShapeComp(self)
        self.text: comps.UITextComp = comps.UITextComp(self)
        self.icon: comps.UIIconComp = comps.UIIconComp(self)
        self.outline: comps.UIOutlineComp = comps.UIOutlineComp(self)

        self.components: tuple[comps.UIComponent] = (
            self.bg, self.image, self.shape, self.text, self.icon, self.outline
        )

        # setup
        self.parent.add_child(self)
        self.init()

    # override
    def init(self):
        """Called at the end of '__init__', overridable"""
        ...

    def on_logic(self):
        """Called on 'logic', overridable"""
        ...

    def on_render(self):
        """Called on 'render', overridable"""
        ...

    def on_event(self, event: pygame.Event):
        """Called on 'event', overridable"""
        ...

    def refresh_stack(self):
        """Used by the stack to organize children, overridable"""
        ...

    def size_changed(self):
        """Called when the size changes, overridable"""
        ...

    def style_changed(self):
        """Called when the style changes, overridable"""
        ...
        
    def position_changed(self):
        """Called when the position changes, overridable"""
        ...

    def build(self):
        """Called when the size or style changes, overridable"""
        ...

    # children
    def add_child(self, element: "UIElement") -> typing.Self:
        """[Internal] Add a child element. Automated when creating the child"""
        if element not in self.children:
            self.children.append(element)
        self.refresh_stack()
        return self

    def remove_child(self, element: "UIElement") -> typing.Self:
        """Remove a child from the children, without destroying it"""
        if element in self.children:
            self.children.remove(element)
        self.refresh_stack()
        return self

    def destroy(self):
        """Destroy the element and all its children if the 'can_destroy' flag is True"""
        if not self.can_destroy:
            return
        self.parent.remove_child(self)
        for child in list(self.children):
            child.destroy()
        self.children.clear()
        if self in self.ui_manager.all_elements:
            self.ui_manager.all_elements.remove(self)
        del self
        
    def destroy_children(self) -> typing.Self:
        """Destroy all children of this element if the children have the 'can_destroy' flag set to True"""
        for child in list(self.children):
            child.destroy()
        self.children.clear()
        return self

    # flags
    def activate(self) -> typing.Self:
        """Activate the element (style will change on hover/press)"""
        self.active = True
        return self

    def deactivate(self) -> typing.Self:
        """Deactivate the element (style won't change on hover/press)"""
        self.active = False
        return self

    def show(self) -> typing.Self:
        """Set the visible flag to True, refresh the stack"""
        self.visible = True
        if not self.ignore_stack:
            self.parent.refresh_stack()
        return self

    def hide(self) -> typing.Self:
        """Set the visible flag to False, refresh the stack"""
        self.visible = False
        if self is self.ui_manager.navigation.tabbed_element:
            self.ui_manager.navigation.stop_navigating()
        if not self.ignore_stack:
            self.parent.refresh_stack()
        return self

    # runtime
    def first_frame(self):
        """[Internal] called on the first frame, refresh the stack"""
        self.refresh_stack()

    def logic(self):
        """[Internal] Called every frame to update children, style and ghost"""
        if self.ghost_element is not None:
            self.set_relative_pos((self.ghost_element.relative_rect.centerx-self.relative_rect.w //
                                  2, self.ghost_element.relative_rect.centery-self.relative_rect.h//2))
        for child in sorted(self.children, key=lambda el: el.z_index):
            child.logic()
        self.calc_style()
        self.style.logic()
        if self.style.dirty:
            for comp in self.components:
                comp.build(self.style)
            self.style.dirty = False

        self.on_logic()

    def render(self):
        """[Internal] Called every frame to render children and components"""
        if not self.visible:
            return
        if not self.absolute_rect.colliderect(self.parent.absolute_rect):
            return
        self.ui_manager.last_rendered = self
        self.element_surface.fill(0)

        for i, comp in enumerate(self.components):
            if i == len(self.components)-1:
                for child in sorted(self.children, key=lambda el: el.z_index):
                    child.render()
            if comp.enabled:
                comp.render()

        self.on_render()
        self.parent.element_surface.blit(
            self.element_surface, self.relative_rect.topleft-(self.ui_manager.root.scroll_offset if self.ignore_scroll else self.parent.scroll_offset))

    def event(self, event: pygame.Event):
        """[Internal] Called for every event"""
        for child in self.children:
            child.event(event)
        self.on_event(event)

    # dunder
    def __enter__(self) -> typing.Self:
        self._previous_parent = UIState.current_parent
        UIState.current_parent = self
        return self

    def __exit__(self, *args, **kwargs):
        UIState.current_parent = self._previous_parent

    # get
    def get_absolute_topleft(self) -> pygame.Vector2:
        """Return the topleft position from the origin of the window"""
        return pygame.Vector2(self.parent.get_absolute_topleft()+self.relative_rect.topleft)-(self.ui_manager.root.scroll_offset if self.ignore_scroll else self.parent.scroll_offset)

    def calc_style(self) -> typing.Self:
        """[Internal] Set the current style based on status"""
        style: UIStyle = None
        if not self.active:
            style = self.style_group.style
        elif self.status.pressed or self.status.selected:
            style = self.style_group.press_style
        elif self.status.hovered:
            style = self.style_group.hover_style
        else:
            style = self.style_group.style
        if style is not self._last_style:
            self.style = style
            self.update_style()
            for comp in self.components:
                comp.build(style)
            self._last_style = style
        return self

    # navigation
    def can_navigate(self) -> bool:
        """Return whether the element can be navigated"""
        return self.status.can_navigate and self.visible

    def find_navigable_child(self) -> "UIElement":
        """Find a child that can be navigated between the element's children and their children"""
        if not self.can_navigate():
            return None
        for child in self.children:
            if child.can_navigate():
                return child
            else:
                their_child = child.find_navigable_child()
                if their_child is not None:
                    return their_child
        return None

    def has_navigable_child(self) -> bool:
        """Return whether at least one of the element's children can be navigated"""
        for child in self.children:
            if child.can_navigate():
                return True
        return False

    def navigable_children_count(self) -> bool:
        """Return how many of the element's children can be navigated"""
        count = 0
        for child in self.children:
            if child.can_navigate():
                count += 1
        return count

    # set
    def set_ignore(self, ignore_stack: bool = False, ignore_scroll: bool = False) -> typing.Self:
        """Set the 'ignore_stack' and 'ignore_scroll' flags"""
        self.ignore_stack = ignore_stack
        self.ignore_scroll = ignore_scroll
        return self
    
    def set_can_destroy(self, can_destroy: bool) -> typing.Self:
        """Set the 'can_destroy' flag. If it is False, destroy() won't work"""
        self.can_destroy = can_destroy
        return self

    def set_z_index(self, z_index: int) -> typing.Self:
        """Set the Z index used for interaction and rendering"""
        self.z_index = z_index
        return self

    def set_absolute_pos(self, position: common.Coordinate) -> typing.Self:
        """Set the topleft position from the origin of the window"""
        old = self.relative_rect.topleft
        self.relative_rect.topleft = position-self.parent.get_absolute_topleft()
        if old == self.relative_rect.topleft:
            return self

        self.update_absolute_rect_pos()
        for comp in self.components:
            comp.position_changed()
        self.position_changed()
        return self

    def set_relative_pos(self, position: common.Coordinate) -> typing.Self:
        """Set the relative position to the parent"""
        if self.relative_rect.topleft == position:
            return self

        self.relative_rect.topleft = position
        self.update_absolute_rect_pos()
        for comp in self.components:
            comp.position_changed()
        self.position_changed()
        return self

    def set_size(self, size: common.Coordinate, propagate_up: bool = False) -> typing.Self:
        """Set the element's size"""
        if self.relative_rect.size == size:
            return self

        self.relative_rect.size = (max(1, size[0]), max(1, size[1]))
        self.update_absolute_rect_size(propagate_up)
        self.update_surface_size()
        for comp in self.components:
            comp.size_changed()
        self.size_changed()
        self.build()

        return self

    def set_width(self, width: int) -> typing.Self:
        """Set the element's width"""
        return self.set_size((width, self.relative_rect.h))

    def set_height(self, height: int) -> typing.Self:
        """Set the element's height"""
        return self.set_size((self.relative_rect.w, height))

    def set_relative_size(self, relative_size: common.Coordinate) -> typing.Self:
        """Set the element's size multiplying the parent's one with the provided values in range 0-1"""
        return self.set_size((self.parent.relative_rect.w*relative_size[0], self.parent.relative_rect.h*relative_size[1]))

    def set_relative_width(self, relative_width: float) -> typing.Self:
        """Set the element's width multiplying the parent's one with the provided value in range 0-1"""
        return self.set_size((self.parent.relative_rect.w*relative_width, self.relative_rect.h))

    def set_relative_height(self, relative_height: float) -> typing.Self:
        """Set the element's height multiplying the parent's one with the provided value in range 0-1"""
        return self.set_size((self.relative_rect.w, self.parent.relative_rect.h*relative_height))

    def set_style_group(self, style_group: UIStyleGroup) -> typing.Self:
        """Manually set the style group of the element (not recommended)"""
        self.style_group = style_group
        self.style = self.style_group.style
        for comp in self.components:
            comp.style_changed()
        self.style_changed()
        self.build()

        return self

    def set_style_id(self, style_id: str) -> typing.Self:
        """Set the style id of the element and build a new style group"""
        self.style_id = style_id
        self.set_style_group(UIStyles.get_style_group(self))
        return self

    def set_element_types(self, element_types: tuple[str]) -> typing.Self:
        """Set the element types of the element and build a new style group"""
        self.element_types = element_types
        self.update_types_override()
        self.set_style_group(UIStyles.get_style_group(self))
        return self

    def set_parent(self, parent: "UIElement") -> typing.Self:
        """Set the element's parent """
        if parent is self.parent:
            return self
        self.parent.remove_child(self)
        self.parent = parent
        self.parent.add_child(self)
        return self

    def set_tooltip(self, title: str, description: str, width: int = 200, height: int = 200, title_h: int = 40) -> "UIElement":
        """Build a new tooltip object with the provided settings and register it"""
        tooltip_cont = UIElement(pygame.Rect(0, 0, width, height),
                                 self.element_id+"tooltip_container",
                                 "default",
                                 ("element", "tooltip", "tooltip_container"),
                                 self.ui_manager.root, self.ui_manager).set_z_index(common.Z_INDEXES["tooltip"])
        if title:
            UIElement(pygame.Rect(0, 0, width, title_h),
                      self.element_id+"tooltip_title",
                      "default",
                      ("element", "tooltip", "label",
                       "tooltip_label", "tooltip_title"),
                      tooltip_cont, self.ui_manager).text.set_text(title).element
        UIElement(pygame.Rect(0, title_h if title else 0, width, height-title_h if title else height),
                  self.element_id+"tooltip_description",
                  "default",
                  ("element", "tooltip", "label",
                   "tooltip_label", "tooltip_description"),
                  tooltip_cont, self.ui_manager).text.set_text(description).element
        tooltip_cont.hide()
        UITooltips.register(tooltip_cont, self)
        return tooltip_cont
    
    def set_custom_tooltip(self, tooltip: "UIElement") -> typing.Self:
        """Register a given tooltip object to appear when hovering this element"""
        if tooltip.z_index < common.Z_INDEXES["tooltip"]:
            tooltip.set_z_index(common.Z_INDEXES["tooltip"])
        tooltip.hide()
        UITooltips.register(tooltip, self)
        return self

    def set_ghost(self, relative_rect: pygame.Rect) -> typing.Self:
        """Create an element that will be invisible that this element will follow while also setting the 'ignore_stack' flag to True"""
        if self.ghost_element is not None:
            self.ghost_element.destroy()
            self.ghost_element = None
        self.set_ignore(True, self.ignore_scroll)
        self.ghost_element = UIElement(relative_rect, self.element_id+"_ghost", "invis_cont",
                                       ("element", "ghost"), self.parent, self.ui_manager).set_z_index(common.Z_INDEXES["ghost"])
        return self

    # add
    def add_element_type(self, element_type: str) -> typing.Self:
        """Add one element type to the tuple and build a new style group"""
        self.element_types = (*self.element_types, element_type)
        self.update_types_override()
        self.set_style_group(UIStyles.get_style_group(self))
        return self

    def add_element_types(self, *element_types: str) -> typing.Self:
        """Add multiple element types to the tuple and build a new style group"""
        for et in element_types:
            self.add_element_type(et)
        return self

    # animation
    def animate_x(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                  ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the x coordinate"""
        UIPropertyAnim(self, AnimPropertyType.x, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_y(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                  ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the y coordinate"""
        UIPropertyAnim(self, AnimPropertyType.y, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_xy(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                   ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the x and y coordinates"""
        UIPropertyAnim(self, AnimPropertyType.x, increase,
                       duration_ms, repeat_mode, ease_func_name)
        UIPropertyAnim(self, AnimPropertyType.y, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_w(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                  ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the width"""
        UIPropertyAnim(self, AnimPropertyType.width, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_h(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                  ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the height"""
        UIPropertyAnim(self, AnimPropertyType.height, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_wh(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                   ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the width and height"""
        UIPropertyAnim(self, AnimPropertyType.width, increase,
                       duration_ms, repeat_mode, ease_func_name)
        UIPropertyAnim(self, AnimPropertyType.height, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_x_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                     ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the x coordinate setting the increase relative to the current value and end value"""
        return self.animate_x(value-self.relative_rect.x, duration_ms, repeat_mode, ease_func_name)

    def animate_y_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                     ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the y coordinate setting the increase relative to the current value and end value"""
        return self.animate_y(value-self.relative_rect.y, duration_ms, repeat_mode, ease_func_name)

    def animate_xy_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                      ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the x and y coordinates setting the increase relative to the current value and end value"""
        self.animate_x(value-self.relative_rect.x, duration_ms,
                       repeat_mode, ease_func_name)
        self.animate_y(value-self.relative_rect.y, duration_ms,
                       repeat_mode, ease_func_name)
        return self

    def animate_w_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                     ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the width setting the increase relative to the current value and end value"""
        return self.animate_w(value-self.relative_rect.w, duration_ms, repeat_mode, ease_func_name)

    def animate_h_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                     ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the height setting the increase relative to the current value and end value"""
        return self.animate_h(value-self.relative_rect.h, duration_ms, repeat_mode, ease_func_name)

    def animate_wh_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                      ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        """Create a new property animation for the width and height setting the increase relative to the current value and end value"""
        self.animate_w(value-self.relative_rect.w, duration_ms,
                       repeat_mode, ease_func_name)
        self.animate_h(value-self.relative_rect.h, duration_ms,
                       repeat_mode, ease_func_name)
        return self

    # update
    def update_absolute_rect_pos(self):
        """[Internal]"""
        self.absolute_rect.topleft = self.get_absolute_topleft()
        self.static_rect.topleft = (0, 0)
        for child in self.children:
            child.update_absolute_rect_pos()

    def update_absolute_rect_size(self, propagate_up: bool = True):
        """[Internal]"""
        self.absolute_rect.size = self.relative_rect.size
        self.static_rect.size = self.relative_rect.size
        if propagate_up:
            self.parent.refresh_stack()
        self.refresh_stack()

    def update_surface_size(self):
        """[Internal]"""
        if self.element_surface.get_size() != self.relative_rect.size:
            self.element_surface = pygame.Surface(
                (max(self.relative_rect.w, 1), max(self.relative_rect.h, 1)), pygame.SRCALPHA)
            
    def update_style(self):
        """[Internal]"""
        self.refresh_stack()
        self.size_changed()
        self.style_changed()
        self.build()
        self.parent.refresh_stack()
        for comp in self.components:
            comp.build(self.style)
        self.style.enter()
        
    def update_types_override(self):
        """[Internal]"""
        new_types = []
        for el_type in self.element_types:
            if not "_override" in el_type:
                new_types.append(el_type)
        self.element_types = ()
        for el_type in new_types:
            self.element_types = (*self.element_types, el_type)
            self.element_types = (*self.element_types, el_type+"_override")
