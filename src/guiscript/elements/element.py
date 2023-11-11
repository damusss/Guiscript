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

        # attrs and setup
        self.children: list[UIElement] = []
        self.ghost_element: UIElement|None = None
        self.element_surface: pygame.Surface = pygame.Surface(
            self.relative_rect.size, pygame.SRCALPHA)
        self.absolute_rect: pygame.Rect = self.relative_rect.copy()
        self.static_rect: pygame.Rect = self.relative_rect.copy()
        self.ignore_stack: bool = False
        self.ignore_scroll: bool = False
        self.z_index: int = 0
        self.scroll_offset: pygame.Vector2 = pygame.Vector2()
        self.update_absolute_rect_pos()

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

        self.parent.add_child(self)
        self.init()

    # override
    def init(self):
        ...

    def on_logic(self):
        ...

    def on_render(self):
        ...

    def on_event(self, event: pygame.Event):
        ...

    def update_size_positions(self):
        ...

    def size_changed(self):
        ...

    def style_changed(self):
        self.update_size_positions()
        self.size_changed()
        self.parent.update_size_positions()
        for comp in self.components:
            comp.build(self.style)
        self.style.enter()

    def build(self):
        self.update_size_positions()
        self.size_changed()

    # children
    def add_child(self, element: "UIElement") -> typing.Self:
        if element not in self.children:
            self.children.append(element)
        self.update_size_positions()
        return self

    def remove_child(self, element: "UIElement") -> typing.Self:
        if element in self.children:
            self.children.remove(element)
        self.update_size_positions()
        return self
    
    def destroy(self):
        ...

    # flags
    def activate(self) -> typing.Self:
        self.active = True
        return self

    def deactivate(self) -> typing.Self:
        self.active = False
        return self

    def show(self) -> typing.Self:
        self.visible = True
        self.parent.update_size_positions()
        return self

    def hide(self) -> typing.Self:
        self.visible = False
        if self is self.ui_manager.navigation.tabbed_element:
            self.ui_manager.navigation.stop_navigating()
        self.parent.update_size_positions()
        return self

    # runtime
    def first_frame(self):
        self.update_size_positions()

    def logic(self):
        if self.ghost_element is not None:
            self.set_relative_pos((self.ghost_element.relative_rect.centerx-self.relative_rect.w//2, self.ghost_element.relative_rect.centery-self.relative_rect.h//2))
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
        return pygame.Vector2(self.parent.get_absolute_topleft()+self.relative_rect.topleft)-(self.ui_manager.root.scroll_offset if self.ignore_scroll else self.parent.scroll_offset)

    def calc_style(self) -> typing.Self:
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
            self.style_changed()
            for comp in self.components:
                comp.build(style)
            self._last_style = style
        return self

    # navigation
    def can_navigate(self) -> bool:
        return self.status.can_navigate and self.visible

    def find_navigable_child(self) -> "UIElement":
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
        for child in self.children:
            if child.can_navigate():
                return True
        return False

    def navigable_children_count(self) -> bool:
        count = 0
        for child in self.children:
            if child.can_navigate():
                count += 1
        return count

    # set
    def set_ignore(self, ignore_stack: bool = False, ignore_scroll: bool = False) -> typing.Self:
        self.ignore_stack = ignore_stack
        self.ignore_scroll = ignore_scroll
        return self

    def set_z_index(self, z_index: int) -> typing.Self:
        self.z_index = z_index
        self.parent.update_size_positions()
        return self

    def set_absolute_pos(self, position: common.Coordinate) -> typing.Self:
        old = self.relative_rect.topleft
        self.relative_rect.topleft = position-self.parent.get_absolute_topleft()
        if old == self.relative_rect.topleft:
            return self

        self.update_absolute_rect_pos()
        for comp in self.components:
            comp.position_changed()

        return self

    def set_relative_pos(self, position: common.Coordinate) -> typing.Self:
        if self.relative_rect.topleft == position:
            return self

        self.relative_rect.topleft = position
        self.update_absolute_rect_pos()
        for comp in self.components:
            comp.position_changed()

        return self

    def set_size(self, size: common.Coordinate, propagate_up: bool = False) -> typing.Self:
        if self.relative_rect.size == size:
            return self

        self.relative_rect.size = (max(1, size[0]), max(1, size[1]))
        self.update_absolute_rect_size(propagate_up)
        self.update_surface_size()
        for comp in self.components:
            comp.size_changed()
        self.size_changed()

        return self

    def set_width(self, width: int) -> typing.Self:
        return self.set_size((width, self.relative_rect.h))

    def set_height(self, height: int) -> typing.Self:
        return self.set_size((self.relative_rect.w, height))

    def set_relative_size(self, relative_size: common.Coordinate) -> typing.Self:
        return self.set_size((self.parent.relative_rect.w*relative_size[0], self.parent.relative_rect.h*relative_size[1]))

    def set_relative_width(self, relative_width: float) -> typing.Self:
        return self.set_size((self.parent.relative_rect.w*relative_width, self.relative_rect.h))

    def set_relative_height(self, relative_height: float) -> typing.Self:
        return self.set_size((self.relative_rect.w, self.parent.relative_rect.h*relative_height))

    def set_style_group(self, style_group: UIStyleGroup) -> typing.Self:
        self.style_group = style_group
        for comp in self.components:
            comp.style_changed()

        return self

    def set_style_id(self, style_id: str) -> typing.Self:
        self.style_id = style_id
        self.style_group: UIStyleGroup = UIStyles.get_style_group(self)
        for comp in self.components:
            comp.style_changed()

        return self

    def set_element_types(self, element_types: tuple[str]) -> typing.Self:
        self.element_types = element_types
        self.update_types_override()
        self.style_group: UIStyleGroup = UIStyles.get_style_group(self)
        for comp in self.components:
            comp.style_changed()

        return self

    def set_parent(self, parent: "UIElement") -> typing.Self:
        if parent is self.parent:
            return self
        self.parent.remove_child(self)
        self.parent = parent
        self.parent.add_child(self)
        return self
    
    def set_tooltip(self, title: str, description: str, width: int = 200, height: int = 200, title_h: int = 40) -> "UIElement":
        tooltip_cont = UIElement(pygame.Rect(0, 0, width, height),
                                 self.element_id+"tooltip_container",
                                 "default",
                                 ("element", "tooltip", "tooltip_container"),
                                 self.ui_manager.root, self.ui_manager).set_z_index(200)
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
    
    def set_ghost(self, relative_rect: pygame.Rect) -> typing.Self:
        if self.ghost_element is not None:
            self.ghost_element.destroy()
            self.ghost_element = None
        self.set_ignore(True, self.ignore_scroll)
        self.ghost_element = UIElement(relative_rect, self.element_id+"_ghost", "invis_cont", ("element", "ghost_element"), self.parent, self.ui_manager).set_z_index(-100)
        return self

    # add
    def add_element_type(self, element_type: str) -> typing.Self:
        self.element_types = (*self.element_types, element_type)
        self.update_types_override()
        self.style_group: UIStyleGroup = UIStyles.get_style_group(self)
        for comp in self.components:
            comp.style_changed()

        return self

    def add_element_types(self, *element_types: str) -> typing.Self:
        for et in element_types:
            self.add_element_type(et)
        return self

    # animation
    def animate_x(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                  ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        UIPropertyAnim(self, AnimPropertyType.x, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_y(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                  ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        UIPropertyAnim(self, AnimPropertyType.y, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self
    
    def animate_xy(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                  ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        UIPropertyAnim(self, AnimPropertyType.x, increase,
                       duration_ms, repeat_mode, ease_func_name)
        UIPropertyAnim(self, AnimPropertyType.y, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_w(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                      ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        UIPropertyAnim(self, AnimPropertyType.width, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_h(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                       ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        UIPropertyAnim(self, AnimPropertyType.height, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self
    
    def animate_wh(self, increase: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                      ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        UIPropertyAnim(self, AnimPropertyType.width, increase,
                       duration_ms, repeat_mode, ease_func_name)
        UIPropertyAnim(self, AnimPropertyType.height, increase,
                       duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_x_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                        ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        return self.animate_x(value-self.relative_rect.x, duration_ms, repeat_mode, ease_func_name)

    def animate_y_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                        ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        return self.animate_y(value-self.relative_rect.y, duration_ms, repeat_mode, ease_func_name)
    
    def animate_xy_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                        ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        self.animate_x(value-self.relative_rect.x, duration_ms, repeat_mode, ease_func_name)
        self.animate_y(value-self.relative_rect.y, duration_ms, repeat_mode, ease_func_name)
        return self

    def animate_w_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                        ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        return self.animate_w(value-self.relative_rect.w, duration_ms, repeat_mode, ease_func_name)

    def animate_h_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                        ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        return self.animate_h(value-self.relative_rect.h, duration_ms, repeat_mode, ease_func_name)
    
    def animate_wh_to(self, value: float, duration_ms: int, repeat_mode: AnimRepeatMode = AnimRepeatMode.repeat,
                        ease_func_name: AnimEaseFunc = AnimEaseFunc.ease_in) -> typing.Self:
        self.animate_w(value-self.relative_rect.w, duration_ms, repeat_mode, ease_func_name)
        self.animate_h(value-self.relative_rect.h, duration_ms, repeat_mode, ease_func_name)
        return self

    # update
    def update_absolute_rect_pos(self):
        self.absolute_rect.topleft = self.get_absolute_topleft()
        self.static_rect.topleft = (0, 0)
        for child in self.children:
            child.update_absolute_rect_pos()

    def update_absolute_rect_size(self, propagate_up: bool = True):
        self.absolute_rect.size = self.relative_rect.size
        self.static_rect.size = self.relative_rect.size
        if propagate_up:
            self.parent.update_size_positions()
        self.update_size_positions()

    def update_surface_size(self):
        if self.element_surface.get_size() != self.relative_rect.size:
            self.element_surface = pygame.Surface(
                (max(self.relative_rect.w, 1), max(self.relative_rect.h, 1)), pygame.SRCALPHA)

    def update_types_override(self):
        new_types = []
        for el_type in self.element_types:
            if not "_override" in el_type:
                new_types.append(el_type)
        self.element_types = ()
        for el_type in new_types:
            self.element_types = (*self.element_types, el_type)
            self.element_types = (*self.element_types, el_type+"_override")
