import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import UIElement

from .style import UIStyleGroup, UIStyle
from .error import UIError
from .icon import UIIcons
from .state import UIState
from . import common


class UIComponent:
    def __init__(self, element: "UIElement", style_change_callback=None):
        self.element: "UIElement" = element
        self.enabled: bool = True
        self.force_visibility: bool = False
        self.style_group: UIStyleGroup = self.element.style_group
        self._last_style: UIStyle = None
        self._style_change_callback = style_change_callback
        self.init()

    def init(self):
        ...

    def render(self):
        ...

    def style_changed(self):
        self.style_group = self.element.style_group
        self.build(self.element.style)

    def position_changed(self):
        ...

    def size_changed(self):
        ...

    def force_enable(self) -> typing.Self:
        self.enabled = True
        self.force_visibility = True
        return self

    def force_disable(self) -> typing.Self:
        self.enabled = False
        return self

    def dont_force(self) -> typing.Self:
        self.force_visibility = False
        return self

    def build(self, style: UIStyle):
        ...


class UIBackgroundComp(UIComponent):
    def render(self):
        if not self.element.style.bg.enabled and not self.force_visibility:
            return
        pygame.draw.rect(self.element.element_surface,
                         self.element.style.bg.color,
                         self.element.static_rect,
                         0,
                         self.element.style.bg.border_radius)


class UIImageComp(UIComponent):
    def init(self):
        self.image_surf: pygame.Surface = None
        self.original_surface: pygame.Surface | None = None
        self.set_surface(None)

    def get_active_surface(self) -> pygame.Surface:
        return self.image_surf

    def get_original_surface(self) -> pygame.Surface:
        return self.original_surface if self.original_surface else self.element.style.image.image

    def set_surface(self, surface: pygame.Surface, force_update: bool = False) -> typing.Self:
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

        iw, ih = original_surface.get_size()
        tw, th = max(self.element.relative_rect.w-style.image.padding*2, 5),\
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
                                                      style.image.border_size)

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

    def render(self):
        original_surface = self.original_surface if self.original_surface else self.element.style.image.image
        if not original_surface:
            return

        if not self.element.style.image.enabled and not self.force_visibility:
            return
        self.element.element_surface.blit(self.image_surf, self.image_rect)
        if self.element.style.image.outline_width > 0:
            pygame.draw.rect(self.element.element_surface, self.element.style.image.outline_color,
                             self.image_rect, self.element.style.image.outline_width, self.element.style.image.border_radius)


class UIShapeComp(UIComponent):
    def init(self):
        self.custom_rect = None

    def set_custom_rect(self, rect: pygame.Rect | None) -> typing.Self:
        self.custom_rect = rect
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
    def init(self):
        self.text: str = None
        self.selection_rects: list[pygame.Rect] = []
        self.can_select: bool = True
        self.set_text("")

    def render(self):
        if not self.element.style.text.enabled and not self.force_visibility:
            return
        for rect in self.selection_rects:
            pygame.draw.rect(self.element.element_surface, self.element.style.text.selection_color, rect)
        self.element.element_surface.blit(self.text_surf, self.text_rect)

    def size_changed(self):
        self.build(self.element.style)

    def get_active_text(self) -> str:
        return self.element.style.text.text if self.element.style.text.text else self.text

    def build(self, style):
        text = style.text.text if style.text.text else self.text
        style.text.apply_mods()
        self.text_surf: pygame.Surface = style.text.font.render(text,
                                                                style.text.antialas,
                                                                style.text.color,
                                                                style.text.bg_color,
                                                                self.element.relative_rect.w)
        self.text_rect: pygame.Rect = common.align_text(self.text_surf.get_rect(),
                                                  self.element.static_rect,
                                                  style.text.padding,
                                                  style.text.y_padding,
                                                  style.text.align)

    def set_text(self, text) -> typing.Self:
        if text == self.text:
            return self
        self.text: str = text
        self.build(self.element.style)
        return self
    
    def enable_selection(self) -> typing.Self:
        self.can_select = True
        return self
    
    def disable_selection(self) -> typing.Self:
        self.can_select = False
        return self


class UIIconComp(UIComponent):
    def init(self):
        self.icon_name = ""
        self.set_icon(None)

    def get_active_name(self) -> str:
        self.icon_name or self.element.style.icon.name

    def get_icon_surface(self) -> pygame.Surface:
        return UIIcons.get(self.icon_name or self.element.style.icon.name)

    def get_active_surface(self) -> pygame.Surface:
        return self.icon_surf

    def set_icon(self, name: str) -> typing.Self:
        if name == self.icon_name:
            return self
        self.icon_name = name
        self.build(self.element.style)
        return self

    def build(self, style: UIStyle):
        icon_name = self.icon_name or style.icon.name
        self.icon_surf: pygame.Surface = pygame.transform.scale_by(
            UIIcons.get(icon_name, self), style.icon.scale)
        self.icon_rect: pygame.Rect = common.align_text(self.icon_surf.get_rect(),
                                                  self.element.static_rect,
                                                  style.icon.padding,
                                                  style.icon.padding,
                                                  style.icon.align)

    def render(self):
        if not self.element.style.icon.enabled and not self.force_visibility:
            return
        self.element.element_surface.blit(self.icon_surf, self.icon_rect)


class UIOutlineComp(UIComponent):
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
        if self.element.ui_manager.navigation.tabbed_element is self.element:
            pygame.draw.rect(self.element.element_surface,
                             style.outline.navigation_color,
                             self.element.static_rect,
                             style.outline.width,
                             style.outline.border_radius)
