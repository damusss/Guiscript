import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import Element

from .style import UIStyleGroup, UIStyle
from .error import UIError
from .icon import Icons
from . import common
from . import richtext


class UIComponent:
    """Base class for element components"""

    def __init__(self, element: "Element", style_change_callback=None):
        self.element: "Element" = element
        self.enabled: bool = True
        self.force_visibility: bool = False
        self.style_group: UIStyleGroup = self.element.style_group
        self._last_style: UIStyle = None
        self._style_change_callback = style_change_callback
        self._init()

    def _init(self):
        ...

    def _render(self):
        ...

    def _style_changed(self):
        self.style_group = self.element.style_group
        self._build(self.element.style)

    def _position_changed(self):
        ...

    def _size_changed(self):
        ...

    def _build(self, style: UIStyle):
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


class UIBackgroundComp(UIComponent):
    """Element component that renders a background"""

    def _render(self):
        if not self.element.style.bg.enabled and not self.force_visibility:
            return
        pygame.draw.rect(self.element.element_surface,
                         self.element.style.bg.color,
                         self.element.static_rect,
                         0,
                         self.element.style.bg.border_radius)


class UIImageComp(UIComponent):
    """Element component that renders an image"""

    def _init(self):
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
        self._build(self.element.style)
        return self

    def _size_changed(self):
        self._build(self.element.style)

    def _build(self, style: UIStyle):
        original_surface = self.original_surface if self.original_surface else style.image.image
        if not original_surface:
            return
        original_surface = original_surface.copy()
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
                original_surface, (w, h))
            if style.image.fill:
                self.image_surf = self.image_surf.subsurface(
                    (w//2-tw//2, h//2-th//2, tw, th))
            w, h = self.image_surf.get_size()
        else:
            self.image_surf = original_surface
        if style.image.fill_color is not None:
            self.image_surf.fill(style.image.fill_color)
        self.image_rect: pygame.Rect = pygame.Rect(0, 0, w, h)
        self.image_rect.center = self.element.static_rect.center
        if style.image.border_radius > 0:
            mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            mask_surf.fill(0)
            pygame.draw.rect(mask_surf, (255, 255, 255, 255),
                             (0, 0, w, h), 0, style.image.border_radius)
            mask = pygame.mask.from_surface(mask_surf)
            self.image_surf = mask.to_surface(
                None, self.image_surf, None, (255, 255, 255, 255), (0, 0, 0, 0))
        if style.image.alpha != 255:
                self.image_surf.set_alpha(style.image.alpha)
        self.element.set_dirty()

    def _render(self):
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

    def _init(self):
        self.custom_rect = None

    def set_custom_rect(self, rect: pygame.Rect | None) -> typing.Self:
        """If the shape type is 'rect', draw the given rect instead of the automated one"""
        self.custom_rect = rect
        self.element.set_dirty()
        return self

    def _render(self):
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

    def _init(self):
        self.text: str = None
        self.real_text: str = None
        self.selection_rects: list[pygame.Rect] = []
        self.can_select: bool = True
        self.cursor_x: int = -1
        self.cursor_y: int = 0
        self.rich_modifiers = None
        self._selection_start_idxs: list[int] = None
        self._selection_end_idxs: list[int] = None
        self._cursor_draw_pos: pygame.Vector2 = pygame.Vector2()
        self._show_cursor: bool = False
        self.set_text("")

    def _render(self):
        style = self.element.style.text
        if not style.enabled and not self.force_visibility:
            return
        for rect in self.selection_rects:
            pygame.draw.rect(self.element.element_surface,
                             style.selection_color, rect)
        self.element.element_surface.blit(self.text_surf, self.text_rect)
        if self._show_cursor and style.cursor_enabled:
            self._render_cursor(style)
        
    def _render_cursor(self, style):
        line = self.real_text.split("\n")[self.cursor_y]
        y = self.cursor_y*style.font.get_height()+self.text_rect.y
        x = self.text_rect.x
        width = common.line_size_x(style.font, line[0:self.cursor_x])
        x = self.text_rect.x+width
        match style.font_align:
            case pygame.FONT_CENTER:
                x = x+self.text_rect.w//2-common.line_size_x(style.font, line)//2
            case pygame.FONT_RIGHT:
                x = self.text_rect.right-common.line_size_x(style.font, line)+width
        pygame.draw.rect(self.element.element_surface, style.cursor_color,
                         (x, y, style.cursor_width, style.font.get_height()))
        self._cursor_draw_pos = pygame.Vector2(x, y)

    def _size_changed(self):
        self._build(self.element.style)

    def _build(self, style):
        text = style.text.text if style.text.text else self.text
        if text.strip() and text[-1] == "\n":
            text += " "
        elif not text.strip():
            text = " "
        if not style.text.rich:
            self.real_text = text
            style.text.apply_mods()
            self.text_surf: pygame.Surface = style.text.font.render(text,
                                                                    style.text.antialas,
                                                                    style.text.color,
                                                                    style.text.bg_color,
                                                                    self.element.relative_rect.w if style.text.do_wrap else 0)
        else:
            default_modifiers = {
                richtext.ModifierName.font_name: style.text.font_name if style.text.font_name != "googleicons" else None,
                richtext.ModifierName.font_size: style.text.font_size,
                richtext.ModifierName.fg_color: style.text.color,
                richtext.ModifierName.bg_color: style.text.bg_color,
                richtext.ModifierName.antialiasing: style.text.antialas,
                richtext.ModifierName.bold: style.text.bold,
                richtext.ModifierName.underline: style.text.underline,
                richtext.ModifierName.italic: style.text.italic,
                richtext.ModifierName.strikethrough: style.text.strikethrough,
            }
            if style.text.rich_modifiers and self.rich_modifiers is not None:
                output_text, modifiers = text, self.rich_modifiers
            else:
                output_text, modifiers = richtext.global_rich_text_parser.parse_text(text)
            self.real_text = output_text
            self.text_surf: pygame.Surface = richtext.render(output_text,
                                                             modifiers,
                                                             default_modifiers,
                                                             richtext.global_font_cache,
                                                             "left" if style.text.font_align == 0 else "right" if style.text.font_align == 2 else "middle",
                                                             -1 if not style.text.do_wrap else self.element.relative_rect.w,
                                                             0, -1, None, False)
        self.text_rect: pygame.Rect = common.align_text(self.text_surf.get_rect(),
                                                        self.element.static_rect,
                                                        style.text.padding,
                                                        style.text.y_padding,
                                                        style.text.align)
        if not style.text.do_wrap and style.text.grow_x:
            self.element.set_size((self.text_surf.get_width()+style.text.padding*2,
                                   self.element.relative_rect.h if not style.text.grow_y else self.text_surf.get_height()+style.text.y_padding*2), True)
        elif style.text.grow_y:
            self.element.set_size(
                (self.element.relative_rect.w, self.text_surf.get_height()+style.text.y_padding*2), True)
        self.element.set_dirty()

    def minimum_text_height(self, text: str, max_w: int | None = None) -> float:
        """Return the minimum height necessary to fit some text with the current style and width, useful for dynamic-sizing text elements. A custom width can be provided as argument"""
        style = self.element.style.text
        style.apply_mods()
        return style.font.render(text,
                                 style.antialas,
                                 style.color,
                                 style.bg_color,
                                 (self.element.relative_rect.w if style.do_wrap else 0) if not max_w else max_w).get_height()+style.y_padding*2

    def text_size(self, text: str) -> tuple[float, float]:
        """Return the size some text would be if rendered"""
        style = self.element.style.text
        style.apply_mods()
        return style.font.size(text)

    def set_text(self, text) -> typing.Self:
        """Manually set the text. This will not override the style's text.text"""
        text = str(text)
        if text == self.text:
            return self
        self.text: str = text
        self._build(self.element.style)
        return self

    def set_cursor_index(self, x: int=0, y=0, show: bool = None) -> typing.Self:
        """Set the cursor index. A bar will be drawn at the said index. -1 or lower means no cursor (default)"""
        if show is None:
            show = self._show_cursor
        if self._show_cursor != show:
            self._show_cursor = show
            self.element.set_dirty()
        if self.cursor_x != x:
            self.cursor_x = x
            self.element.set_dirty()
        if self.cursor_y != y:
            self.cursor_y = y
            self.element.set_dirty()
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

    def _get_selection(self, _2D=False) -> tuple[int]:
        if self._selection_end_idxs is None or self._selection_start_idxs is None:
            return None
        if len(self._selection_start_idxs) < 3 or len(self._selection_end_idxs) < 3:
            return None
        if not _2D:
            selection = (min(self._selection_start_idxs[-1], self._selection_end_idxs[-1]), max(
                self._selection_start_idxs[-1], self._selection_end_idxs[-1]))
            if selection[1]-selection[0] == 0:
                return None
        else:
            selection = (min(self._selection_start_idxs[-3], self._selection_end_idxs[-3]), max(
                self._selection_start_idxs[-3], self._selection_end_idxs[-3]),
                         min(self._selection_start_idxs[-2], self._selection_end_idxs[-2]), max(
                self._selection_start_idxs[-2], self._selection_end_idxs[-2]))
            if selection[3]-selection[2] == 0 and selection[1]-selection[0] == 0:
                return None
        return selection


class UIIconComp(UIComponent):
    """Element component that renders icon surfaces"""

    def _init(self):
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
        self._build(self.element.style)
        return self

    def _build(self, style: UIStyle):
        icon_name = self.icon_name or style.icon.name
        self.icon_surf: pygame.Surface = pygame.transform.scale_by(
            Icons.get(icon_name, self), style.icon.scale)
        self.icon_rect: pygame.Rect = common.align_text(self.icon_surf.get_rect(),
                                                        self.element.static_rect,
                                                        style.icon.padding,
                                                        style.icon.padding,
                                                        style.icon.align)
        self.element.set_dirty()

    def _size_changed(self):
        self._build(self.element.style)

    def _render(self):
        if not self.element.style.icon.enabled and not self.force_visibility:
            return
        self.element.element_surface.blit(self.icon_surf, self.icon_rect)


class UIOutlineComp(UIComponent):
    """Element component that renders an outline"""

    def _render(self):
        style = self.element.style
        if not style.outline.enabled and not self.force_visibility:
            self._render_tabbed(style)
            return
        pygame.draw.rect(self.element.element_surface,
                         style.outline.color,
                         self.element.static_rect,
                         style.outline.width,
                         style.outline.border_radius)

        self._render_tabbed(style)

    def _render_tabbed(self, style: UIStyle):
        if self.element.manager.navigation.tabbed_element is self.element:
            pygame.draw.rect(self.element.element_surface,
                             style.outline.navigation_color,
                             self.element.static_rect,
                             style.outline.width,
                             style.outline.border_radius)
