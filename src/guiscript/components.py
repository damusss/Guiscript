import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import Element

from .style import UIStyleGroup, UIStyle
from .error import UIError
from .icon import Icons
from . import common


class UIComponent:
    """Base class for element components"""

    def __init__(self, element: "Element", style_change_callback=None):
        self.element: "Element" = element
        self.enabled: bool = True
        self.force_visibility: bool = False
        self.style_group: UIStyleGroup = self.element.style_group
        self._last_style: UIStyle = None
        self._style_change_callback = style_change_callback
        self.init()

    def init(self):
        """[Internal] Called by the base class after initialization"""
        ...

    def render(self):
        """[Internal] Render the component"""
        ...

    def style_changed(self):
        """[Internal] Rebuild the component"""
        self.style_group = self.element.style_group
        self.build(self.element.style)

    def position_changed(self):
        """[Internal] Overridable by subclasses"""
        ...

    def size_changed(self):
        """[Internal] Overridable by subclasses"""
        ...

    def force_enable(self) -> typing.Self:
        """Force the component to stay enabled"""
        self.enabled = True
        self.force_visibility = True
        return self

    def force_disable(self) -> typing.Self:
        """Force the component to stay disabled"""
        self.enabled = False
        return self

    def dont_force(self) -> typing.Self:
        """Don't force visibility over the component"""
        self.force_visibility = False
        return self

    def build(self, style: UIStyle):
        """[Internal] Overridable by subclasses"""
        ...


class UIBackgroundComp(UIComponent):
    """Element component that renders a background"""

    def render(self):
        if not self.element.style.bg.enabled and not self.force_visibility:
            return
        pygame.draw.rect(self.element.element_surface,
                         self.element.style.bg.color,
                         self.element.static_rect,
                         0,
                         self.element.style.bg.border_radius)


class UIImageComp(UIComponent):
    """Element component that renders an image"""

    def init(self):
        self.image_surf: pygame.Surface = None
        self.image_rect: pygame.Rect = None
        self.original_surface: pygame.Surface | None = None
        self.set_surface(None)

    def get_active_surface(self) -> pygame.Surface:
        """Return the surface the component is blitting"""
        return self.image_surf

    def get_original_surface(self) -> pygame.Surface:
        """Return the surface the component uses before scaling it"""
        return self.original_surface if self.original_surface else self.element.style.image.image

    def set_surface(self, surface: pygame.Surface, force_update: bool = False) -> typing.Self:
        """Manually set the surface. This will override the style's image.image property"""
        if surface == self.original_surface and not force_update:
            return self
        self.original_surface: pygame.Surface = surface
        self.build(self.element.style)
        return self

    def size_changed(self):
        self.build(self.element.style)

    def build(self, style: UIStyle):
        original_surface = self.original_surface if self.original_surface else style.image.image
        if not original_surface:
            return
        original_surface = pygame.transform.scale_by(
            original_surface, style.image.border_scale)

        iw, ih = original_surface.get_size()
        tw, th = max(self.element.relative_rect.w-style.image.padding*2, 5), \
            max(self.element.relative_rect.h-style.image.padding*2, 5)

        if style.image.border_size <= 0:
            if not style.image.fill:
                w = tw
                h = int(ih*(w/iw))
                if h > th:
                    h = th
                    w = int(iw*(h/ih))
                if w < tw and style.image.stretch_x:
                    w = tw
                if h < th and style.image.stretch_y:
                    h = th
            else:
                if tw >= th:
                    w = tw
                    h = int(ih*(w/iw))
                else:
                    h = th
                    w = int(iw*(h/ih))
        else:
            w, h = tw, th
            original_surface = common.generate_menu_surface(original_surface,
                                                            w-(style.image.padding)*2,
                                                            h-(style.image.padding)*2,
                                                            int(style.image.border_size*style.image.border_scale))

        w, h = max(w, 1), max(h, 1)
        if style.image.border_size <= 0:
            self.image_surf: pygame.Surface = pygame.transform.scale(
                original_surface, (w, h)).convert_alpha()
            if style.image.fill:
                self.image_surf = self.image_surf.subsurface(
                    (w//2-tw//2, h//2-th//2, tw, th))
            w, h = self.image_surf.get_size()
        else:
            self.image_surf = original_surface
        self.image_rect: pygame.Rect = pygame.Rect(0, 0, w, h)
        self.image_rect.center = self.element.static_rect.center
        if style.image.border_radius > 0:
            mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            mask_surf.fill(0)
            pygame.draw.rect(mask_surf, (255, 255, 255, 255),
                             (0, 0, w, h), 0, style.image.border_radius)
            mask = pygame.mask.from_surface(mask_surf)
            self.image_surf = mask.to_surface(
                None, self.image_surf, None, None, (0, 0, 0, 0))
        self.element.set_dirty()

    def render(self):
        original_surface = self.original_surface if self.original_surface else self.element.style.image.image
        if not original_surface or not self.image_surf or not self.image_rect:
            return
        if not self.element.style.image.enabled and not self.force_visibility:
            return
        self.element.element_surface.blit(self.image_surf, self.image_rect)
        if self.element.style.image.outline_width > 0:
            pygame.draw.rect(self.element.element_surface, self.element.style.image.outline_color,
                             self.image_rect, self.element.style.image.outline_width, self.element.style.image.border_radius)


class UIShapeComp(UIComponent):
    """Element component that renders a shape"""

    def init(self):
        self.custom_rect = None

    def set_custom_rect(self, rect: pygame.Rect | None) -> typing.Self:
        """If the shape type is 'rect', draw the given rect instead of the automated one"""
        self.custom_rect = rect
        self.element.set_dirty()
        return self

    def render(self):
        if not self.element.style.shape.enabled and not self.force_visibility:
            return
        style = self.element.style
        match style.shape.type:
            case "rect":
                rect = (
                    (style.shape.padding, style.shape.padding),
                    (self.element.relative_rect.w-style.shape.padding*2,
                     self.element.relative_rect.h-style.shape.padding*2)) if not self.custom_rect else \
                    self.custom_rect
                pygame.draw.rect(self.element.element_surface,
                                 style.shape.color,
                                 rect,
                                 style.shape.outline_width,
                                 style.shape.rect_border_radius)
            case "circle":
                pygame.draw.circle(self.element.element_surface,
                                   style.shape.color,
                                   self.element.static_rect.center,
                                   ((self.element.relative_rect.w +
                                    self.element.relative_rect.h)/2-style.shape.padding*2)/2,
                                   style.shape.outline_width)
            case "ellipse":
                pygame.draw.ellipse(self.element.element_surface,
                                    style.shape.color,
                                    (style.shape.ellipse_padding_x,
                                     style.shape.ellipse_padding_y,
                                     self.element.relative_rect.w-style.shape.ellipse_padding_x*2,
                                     self.element.relative_rect.h-style.shape.ellipse_padding_y*2),
                                    style.shape.outline_width)
            case "polygon":
                points = []
                for p in style.shape.polygon_points:
                    points.append(pygame.Vector2(
                        p)+self.element.static_rect.center)
                pygame.draw.polygon(self.element.element_surface,
                                    style.shape.color,
                                    points,
                                    style.shape.outline_width)
            case "_":
                raise UIError(
                    f"Unsupported shape type '{style.shape.type}'. Supported are rect, circle, ellipse, polygon")


class UITextComp(UIComponent):
    """Element component that renders text"""

    def init(self):
        self.text: str = None
        self.selection_rects: list[pygame.Rect] = []
        self.can_select: bool = True
        self.set_text("")

    def render(self):
        if not self.element.style.text.enabled and not self.force_visibility:
            return
        for rect in self.selection_rects:
            pygame.draw.rect(self.element.element_surface,
                             self.element.style.text.selection_color, rect)
        self.element.element_surface.blit(self.text_surf, self.text_rect)

    def size_changed(self):
        self.build(self.element.style)

    def get_active_text(self) -> str:
        """Return the text the component is rendering as a string"""
        return self.element.style.text.text if self.element.style.text.text else self.text

    def build(self, style):
        text = style.text.text if style.text.text else self.text
        style.text.apply_mods()
        self.text_surf: pygame.Surface = style.text.font.render(text,
                                                                style.text.antialas,
                                                                style.text.color,
                                                                style.text.bg_color,
                                                                self.element.relative_rect.w if style.text.do_wrap else 0)
        self.text_rect: pygame.Rect = common.align_text(self.text_surf.get_rect(),
                                                        self.element.static_rect,
                                                        style.text.padding,
                                                        style.text.y_padding,
                                                        style.text.align)
        if not style.text.do_wrap and style.text.grow_x:
            self.element.set_size((self.text_surf.get_width()+style.text.padding*2,
                                   self.element.relative_rect.h if not style.text.grow_y else self.text_surf.get_height()+style.text.y_padding*2))
        elif style.text.grow_y:
            self.element.set_size(
                (self.element.relative_rect.w, self.text_surf.get_height()+style.text.y_padding*2))
        self.element.set_dirty()

    def minimum_text_height(self, text, max_w: int | None = None) -> float:
        """Return the minimum height necessary to fit some text with the current style and width, useful for dynamic-sizing text elements. A custom width can be provided as argument"""
        style = self.element.style.text
        style.apply_mods()
        return style.font.render(text,
                                 style.antialas,
                                 style.color,
                                 style.bg_color,
                                 (self.element.relative_rect.w if style.do_wrap else 0) if not max_w else max_w).get_height()+style.y_padding*2

    def set_text(self, text) -> typing.Self:
        """Manually set the text. This will not override the style's text.text"""
        text = str(text)
        if text == self.text:
            return self
        self.text: str = text
        self.build(self.element.style)
        return self

    def enable_selection(self) -> typing.Self:
        """Let the user select and copy text on the element"""
        self.can_select = True
        return self

    def disable_selection(self) -> typing.Self:
        """Prevent the user from selecting or copying text on the element"""
        self.can_select = False
        self.selection_rects = []
        self.element.set_dirty()
        return self


class UIIconComp(UIComponent):
    """Element component that renders icon surfaces"""

    def init(self):
        self.icon_name = ""
        self.set_icon(None)

    def get_active_name(self) -> str:
        """Return the icon name the component is using"""
        self.icon_name or self.element.style.icon.name

    def get_icon_surface(self) -> pygame.Surface:
        """Return the icon surface the component is rendering before scaling it"""
        return Icons.get(self.icon_name or self.element.style.icon.name)

    def get_active_surface(self) -> pygame.Surface:
        """Return the icon surface the component is blitting"""
        return self.icon_surf

    def set_icon(self, name: str) -> typing.Self:
        """Manually set the icon name. This will override the style's icon.name"""
        if name == self.icon_name:
            return self
        self.icon_name = name
        self.build(self.element.style)
        return self

    def build(self, style: UIStyle):
        icon_name = self.icon_name or style.icon.name
        self.icon_surf: pygame.Surface = pygame.transform.scale_by(
            Icons.get(icon_name, self), style.icon.scale)
        self.icon_rect: pygame.Rect = common.align_text(self.icon_surf.get_rect(),
                                                        self.element.static_rect,
                                                        style.icon.padding,
                                                        style.icon.padding,
                                                        style.icon.align)
        self.element.set_dirty()

    def render(self):
        if not self.element.style.icon.enabled and not self.force_visibility:
            return
        self.element.element_surface.blit(self.icon_surf, self.icon_rect)


class UIOutlineComp(UIComponent):
    """Element component that renders an outline"""

    def render(self):
        style = self.element.style
        if not style.outline.enabled and not self.force_visibility:
            self.render_tabbed(style)
            return
        pygame.draw.rect(self.element.element_surface,
                         style.outline.color,
                         self.element.static_rect,
                         style.outline.width,
                         style.outline.border_radius)

        self.render_tabbed(style)

    def render_tabbed(self, style: UIStyle):
        """[Internal] Render the keyboard navigation outline if the element is tabbed"""
        if self.element.ui_manager.navigation.tabbed_element is self.element:
            pygame.draw.rect(self.element.element_surface,
                             style.outline.navigation_color,
                             self.element.static_rect,
                             style.outline.width,
                             style.outline.border_radius)
