import pygame
import typing
import random
import string

from .manager import Manager
from .animation import UIAnimUpdater
from .tooltip import Tooltips
from .state import UIState
from .error import UIError
from .script import UIScript
from .elements.scrollbars import UIVScrollbar, UIHScrollbar
from .elements.stacks import UIStack, VStack, HStack
from .elements.element import Element
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
NO_SOUND: str = "nosound"


def invis_element(relative_rect: pygame.Rect, element_id: str = "none", extra_style_id: str = "invisible",
                 parent: Element | None = None, manager: Manager | None = None) -> Element:
    """Return an element with invisible styling and 'invisible_element' extra element type"""
    return Element(relative_rect, element_id, "invisible"+(f";{extra_style_id}" if extra_style_id else ""), ("element", "invisible_element"), parent, manager).deactivate()


def hline(relative_rect: pygame.Rect, element_id: str = "none", style_id: str = "fill_x", parent: Element | None = None, manager: Manager | None = None) -> Element:
    """Return an element with default styling for filling x and for uniform colors with extra 'line' and 'hline' element types"""
    return Element(relative_rect, element_id, style_id, ("element", "line", "hline"), parent, manager)


def vline(relative_rect: pygame.Rect, element_id: str = "none", style_id: str = "fill_y", parent: Element | None = None, manager: Manager | None = None) -> Element:
    """Return an element with default styling for filling y and for uniform colors with extra 'line' and 'vline' element types"""
    return Element(relative_rect, element_id, style_id, ("element", "line", "vline"), parent, manager)


def column(size: common.Coordinate, fill_y: bool = True,
           extra_style_id: str = "", element_id: str = "none", parent: Element|None = None, manager: Manager|None = None) -> VStack:
    """Return an invisible vertical container with easier settings, commonly used for columns. Extra element type added is 'column'"""
    style_str = "invisible"+(";fill_y" if fill_y else "")+(f";{extra_style_id}"if extra_style_id else "")
    return VStack(pygame.Rect((0, 0), size), element_id, style_str, parent, manager).add_element_type("column")


def row(size: common.Coordinate, fill_x: bool = True,
        extra_style_id: str = "", element_id: str = "none", parent: Element|None = None, manager: Manager|None = None) -> HStack:
    """Return an invisible horizontal container with easier settings, commonly used for rows. Extra element type added is 'row'"""
    style_str = "invisible"+(";fill_x" if fill_x else "")+(f";{extra_style_id}"if extra_style_id else "")
    return HStack(pygame.Rect((0, 0), size), element_id, style_str, parent, manager).add_element_type("row")


def custom_hscrollbar(stack: UIStack, element_id: str = "none", style_id: str = "") -> UIHScrollbar:
    """Make a custom horizontal scrollbar to use on a stack. The user must bound it to the stack manually. The scrollbar won't be auto positioned and sized to give freedom to the user"""
    sbar = UIHScrollbar(stack, style_id)
    sbar.set_element_id(element_id)
    sbar._is_custom = True
    return sbar


def custom_vscrollbar(stack: UIStack, element_id: str = "none", style_id: str = "") -> UIVScrollbar:
    """Make a custom vertical scrollbar to use on a stack. The user must bound it to the stack manually. The scrollbar won't be auto positioned and sized to give freedom to the user"""
    sbar = UIVScrollbar(stack, style_id)
    sbar.set_element_id(element_id)
    sbar._is_custom = True
    return sbar


def bind_one_selected_only(selectable_elements: list[Element], can_deselect: bool = False):
    """Bind listeners so that when one of the given elements is selected, all the other ones are deselected. Useful for example for layouts when the user must only choose one option in a checkbox list"""
    def _on_select(el):
        for e in selectable_elements:
            if e is not el:
                e.status.deselect()
        
    def _on_deselect(el):
        el.status.select()
    
    for el in selectable_elements:
        el.status.deselect()
        if not can_deselect:
            el.status.add_multi_listeners(on_select=_on_select, on_deselect=_on_deselect)
        else:
            el.status.add_listener("on_select", _on_select)
            

def static_dock(root: Element, ids_elements: list[tuple[int, Element]], ids_root_anchors: list[tuple[int, enums.DockAnchor]], ids_connection_ids: list[tuple[int, enums.DockConn, int]]):
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
    if name == "1x1":
        return strimages._1X1SURF
    if name not in strimages.STRING_IMAGES_SURFACES.keys():
        raise UIError(f"Builtin image '{name}' does not exist. Available are {list(strimages.STRING_IMAGES_SURFACES.keys())} + '1x1'")
    return strimages.STRING_IMAGES_SURFACES[name]


def get_current_manager() -> Manager:
    """Return the manager set as current"""
    return UIState.current_manager


def get_current_parent() -> Element:
    """Return the element which is currently set as the default parent for the next elements in its context manager"""
    return UIState.current_parent
