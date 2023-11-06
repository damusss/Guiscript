import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import UIElement

from .style import UIStyleGroup, UIStyle
from .error import UIError
from .icon import UIIcons


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
        self.build(self.get_style())

    def position_changed(self):
        ...

    def size_changed(self):
        ...

    def get_style(self) -> UIStyle:
        style = None
        if self.element.status.pressed or self.element.status.selected:
            style = self.style_group.press_style
        elif self.element.status.hovered:
            style = self.style_group.hover_style
        else:
            style = self.style_group.style
        if style is not self._last_style:
            self._last_style = style
            if self._style_change_callback:
                self._style_change_callback()
            self.build(style)
        return style

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
        style = self.get_style()
        if not style.bg.enabled and not self.force_visibility:
            return
        pygame.draw.rect(self.element.element_surface,
                         style.bg.color,
                         self.element.static_rect,
                         0,
                         style.bg.border_radius)


class UIImageComp(UIComponent):
    def init(self):
        self.image_surf: pygame.Surface = None
        self.original_surface: pygame.Surface|None = None
        self.set_surface(None)

    def get_active_surface(self) -> pygame.Surface:
        return self.image_surf

    def get_original_surface(self) -> pygame.Surface:
        return self.original_surface if self.original_surface else self.get_style().image.image

    def set_surface(self, surface: pygame.Surface, force_update: bool = False) -> typing.Self:
        if surface == self.original_surface and not force_update: return self
        self.original_surface: pygame.Surface = surface
        self.build(self.get_style())
        return self

    def size_changed(self):
        self.build(self.get_style())

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
            original_surface = _generate_menu_surface(original_surface,
                                                      w-(style.image.padding)*2,
                                                      h-(style.image.padding)*2,
                                                      style.image.border_size)

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
        style = self.get_style()
        original_surface = self.original_surface if self.original_surface else style.image.image
        if not original_surface:
            return

        if not style.image.enabled and not self.force_visibility:
            return
        self.element.element_surface.blit(self.image_surf, self.image_rect)
        if style.image.outline_width > 0:
            pygame.draw.rect(self.element.element_surface, style.image.outline_color,
                             self.image_rect, style.image.outline_width, style.image.border_radius)


class UIShapeComp(UIComponent):
    def init(self):
        self.custom_rect = None

    def set_custom_rect(self, rect: pygame.Rect | None) -> typing.Self:
        self.custom_rect = rect
        return self

    def render(self):
        style = self.get_style()
        if not style.shape.enabled and not self.force_visibility:
            return
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
        self.text = None
        self.set_text("")

    def render(self):
        style = self.get_style()
        if not style.text.enabled and not self.force_visibility:
            return
        style.text.apply_mods()
        self.element.element_surface.blit(self.text_surf, self.text_rect)

    def size_changed(self):
        self.build(self.get_style())

    def get_active_text(self) -> str:
        style = self.get_style()
        return style.text.text if style.text.text else self.text

    def build(self, style):
        text = style.text.text if style.text.text else self.text
        self.text_surf: pygame.Surface = style.text.font.render(text,
                                                                style.text.antialas,
                                                                style.text.color,
                                                                style.text.bg_color,
                                                                self.element.relative_rect.w)
        self.text_rect: pygame.Rect = _align_text(self.text_surf.get_rect(),
                                                  self.element.static_rect,
                                                  style.text.padding,
                                                  style.text.y_padding,
                                                  style.text.align)

    def set_text(self, text) -> typing.Self:
        if text == self.text: return self
        self.text: str = text
        self.build(self.get_style())
        return self


class UIIconComp(UIComponent):
    def init(self):
        self.icon_name = ""
        self.set_icon(None)

    def get_active_name(self) -> str:
        self.icon_name or self.get_style().icon.name

    def get_icon_surface(self) -> pygame.Surface:
        return UIIcons.get(self.icon_name or self.get_style().icon.name)

    def get_active_surface(self) -> pygame.Surface:
        return self.icon_surf

    def set_icon(self, name: str) -> typing.Self:
        if name == self.icon_name: return self
        self.icon_name = name
        self.build(self.get_style())
        return self

    def build(self, style: UIStyle):
        icon_name = self.icon_name or style.icon.name
        self.icon_surf: pygame.Surface = pygame.transform.scale_by(
            UIIcons.get(icon_name, self), style.icon.scale)
        self.icon_rect: pygame.Rect = _align_text(self.icon_surf.get_rect(),
                                                  self.element.static_rect,
                                                  style.icon.padding,
                                                  style.icon.padding,
                                                  style.icon.align)

    def render(self):
        style = self.get_style()
        if not style.icon.enabled and not self.force_visibility:
            return
        self.element.element_surface.blit(self.icon_surf, self.icon_rect)

class UIOutlineComp(UIComponent):
    def render(self):
        style = self.get_style()
        if not style.outline.enabled and not self.force_visibility:
            return
        pygame.draw.rect(self.element.element_surface,
                         style.outline.color,
                         self.element.static_rect,
                         style.outline.width,
                         style.outline.border_radius)


def _align_text(t_rect, el_rect, padding, y_padding, align):
    match align:
        case "center":
            t_rect.center = el_rect.center
        case "topleft":
            t_rect.topleft = (el_rect.left+padding, el_rect.top+y_padding)
        case "topright":
            t_rect.topright = (el_rect.right-padding, el_rect.top+y_padding)
        case "bottomleft":
            t_rect.bottomleft = (el_rect.left+padding,
                                 el_rect.bottom-y_padding)
        case "bottomright":
            t_rect.bottomright = (el_rect.right-padding,
                                  el_rect.bottom-y_padding)
        case "midleft" | "left":
            t_rect.midleft = (el_rect.left+padding, el_rect.centery)
        case "midright" | "right":
            t_rect.midright = (el_rect.right-padding, el_rect.centery)
        case "midtop" | "top":
            t_rect.midtop = (el_rect.centerx, el_rect.top+y_padding)
        case "midbottom" | "bottom":
            t_rect.midbottom = (el_rect.centerx, el_rect.bottom-y_padding)
        case _:
            raise UIError(f"Unsupported text align: '{align}'")
    return t_rect


def _generate_menu_surface(original_image: pygame.Surface, width: int, height: int, border: int) -> pygame.Surface:
    if border < 1:
        return original_image
    # setup
    s, s2 = border, border*2
    width, height = int(width), int(height)
    menu_surf: pygame.Surface = original_image
    mw, mh = menu_surf.get_width(), menu_surf.get_height()
    # main surfs
    try:
        big_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    except pygame.error:
        return original_image
    big_surf.fill(0)
    inner_surf = pygame.transform.scale(menu_surf.subsurface(
        (s, s, mw-s2, mh-s2)), (max(width-s2, 1), max(height-s2, 1)))
    # corners
    topleft = menu_surf.subsurface((0, 0, s, s))
    topright = menu_surf.subsurface((mw-s, 0, s, s))
    bottomleft = menu_surf.subsurface((0, mh-s, s, s))
    bottomright = menu_surf.subsurface((mw-s, mh-s, s, s))
    # sides
    top = pygame.transform.scale(menu_surf.subsurface(
        (s, 0, mw-s2, s)), (max(width-s2, 1), s))
    bottom = pygame.transform.scale(menu_surf.subsurface(
        (s, mh-s, mw-s2, s)), (max(width-s2, 1), s))
    left = pygame.transform.scale(menu_surf.subsurface(
        (0, s, s, mh-s2)), (s, max(height-s2, 1)))
    right = pygame.transform.scale(menu_surf.subsurface(
        (mw-s, s, s, mh-s2)), (s, max(height-s2, 1)))
    # blitting
    big_surf.blit(inner_surf, (s, s))
    big_surf.blit(topleft, (0, 0))
    big_surf.blit(topright, (width-s, 0))
    big_surf.blit(bottomleft, (0, height-s))
    big_surf.blit(bottomright, (width-s, height-s))
    big_surf.blit(top, (s, 0))
    big_surf.blit(bottom, (s, height-s))
    big_surf.blit(left, (0, s))
    big_surf.blit(right, (width-s, s))
    # return
    return big_surf
