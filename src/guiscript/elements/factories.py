import pygame
import typing
import warnings

from .element import UIElement
from ..manager import UIManager
from ..enums import ElementAlign
from ..error import UIError
from ..state import UIState
from ..events import _post_slideshow_event, _post_slider_event
from ..common import StatusCallback
from .. import settings

element: typing.TypeAlias = UIElement

# PROGRESS BAR

class Slider(UIElement):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 settings: settings.SliderSettings = settings.SliderDefaultSettings,
                 ):
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "slider"), parent, ui_manager)
        self.settings = settings
        if not self.settings.axis in ["horizontal", "vertical"]:
            warnings.warn(
                f"Slider axis '{self.settings.axis}' is not supported", category=UserWarning)
        self.bar = UIElement(
            (pygame.Rect(0, 0, self.relative_rect.w-self.settings.handle_size*2, self.settings.bar_size)
             if self.settings.axis == "horizontal" else
             pygame.Rect(0, 0, self.settings.bar_size, self.relative_rect.h-self.settings.handle_size*2)),
            self.element_id+"_bar",
            (self.style_id if self.settings.bar_style_id ==
             "copy" else self.settings.bar_style_id),
            ("element", "slider_bar"),
            self,
            self.ui_manager
        )
        self.handle = UIElement(
            pygame.Rect(0, 0, self.settings.handle_size,
                        self.settings.handle_size),
            self.element_id+"_handle",
            (self.style_id if self.settings.handle_style_id ==
             "copy" else self.settings.handle_style_id),
            ("element", "button", "slider_handle"),
            self,
            self.ui_manager
        )
        self.deactivate()
        self.bar.deactivate()
        self.build()
        self.set_value(self.settings.start_value)

    def get_value(self) -> float:
        return (((self.handle.relative_rect.centerx-self.bar.relative_rect.left)/self.bar.relative_rect.w)
                if self.settings.axis == "horizontal" else
                ((self.handle.relative_rect.centery-self.bar.relative_rect.top)/self.bar.relative_rect.h))

    def get_percent(self) -> float:
        return self.get_value()*100

    def set_value(self, value: float) -> typing.Self:
        if self.settings.axis == "horizontal":
            pos = self.bar.relative_rect.x+(value*self.bar.relative_rect.w)-self.settings.handle_size//2
            self.handle.set_relative_pos(
                (pos, self.bar.relative_rect.centery-self.settings.handle_size//2))
        elif self.settings.axis == "vertical":
            pos = self.bar.relative_rect.y+(value*self.bar.relative_rect.h)-self.settings.handle_size//2
            self.handle.set_relative_pos(
                (self.bar.relative_rect.centerx-self.settings.handle_size//2, pos))
        self.buffers.update("value", value)
        return self

    def set_percent(self, value_percent: float) -> typing.Self:
        return self.set_value(value_percent/100)

    def on_logic(self):
        if not self.handle.status.pressed:
            return
        if self.settings.axis == "horizontal" and UIState.mouse_rel[0] != 0:
            prev = self.get_value()
            self.handle.set_relative_pos((pygame.math.clamp(self.handle.relative_rect.x+UIState.mouse_rel[0],
                                                            self.bar.relative_rect.left-self.settings.handle_size//2,
                                                            self.bar.relative_rect.right-self.settings.handle_size//2),
                                          self.handle.relative_rect.y))
            val = self.get_value()
            if prev != val:
                _post_slider_event(prev, val, self)
                self.status.invoke_callback("on_move")
                self.buffers.update("value", val)
        elif self.settings.axis == "vertical" and UIState.mouse_rel[1] != 0:
            prev = self.get_value()
            self.handle.set_relative_pos((self.handle.relative_rect.x,
                                          pygame.math.clamp(self.handle.relative_rect.y+UIState.mouse_rel[1],
                                                            self.bar.relative_rect.top-self.settings.handle_size//2,
                                                            self.bar.relative_rect.bottom-self.settings.handle_size//2), ))
            val = self.get_value()
            if prev != val:
                _post_slider_event(prev, val, self)
                self.status.invoke_callback("on_move")
                self.buffers.update("value", val)

    def size_changed(self):
        cur_value = self.get_value()
        style = self.get_style()
        self.handle.set_size(
            (self.settings.handle_size, self.settings.handle_size))
        if self.settings.axis == "horizontal":
            self.bar.set_size(
                (self.relative_rect.w-self.settings.handle_size-style.stack.padding*2, self.settings.bar_size))
        elif self.settings.axis == "vertical":
            self.bar.set_size(
                (self.settings.bar_size, self.relative_rect.h-self.settings.handle_size-style.stack.padding*2))
        self.bar.set_relative_pos((self.relative_rect.w//2-self.bar.relative_rect.w //
                                  2, self.relative_rect.h//2-self.bar.relative_rect.h//2))
        self.set_value(cur_value)


class GIF(UIElement):
    def __init__(self,
                 frames: list[pygame.Surface],
                 relative_rect: pygame.Rect,
                 frame_speed: float = 0.04,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id, style_id, ("element", "image", "gif"), parent,
                         ui_manager)
        self.set_frames(frames, frame_speed).play()
        self.build()

    def set_frames(self, frames: list[pygame.Surface], frame_speed: float = 0.04) -> typing.Self:
        if len(frames) <= 0:
            raise UIError(f"GIF frames list must contain at least 1 surface")
        self.frames: list[pygame.Surface] = frames
        self.frame_index: float = 0
        self.frame_speed: float = frame_speed
        self.set_surface(self.frames[int(self.frame_index)])
        return self

    def set_surface(self, surface: pygame.Surface) -> typing.Self:
        self.image.set_surface(surface)
        return self

    def set_frame_index(self, index: float) -> typing.Self:
        self.frame_index = pygame.math.clamp(index, 0, len(self.frames)-1)
        return self

    def get_frame(self) -> pygame.Surface:
        return self.frames[int(self.frame_index)]

    def on_logic(self):
        if not self.is_playing:
            return

        self.frame_index += self.frame_speed*UIState.delta_time
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

        self.set_surface(self.frames[int(self.frame_index)])

    def play(self) -> typing.Self:
        self.is_playing: bool = True
        return self

    def stop(self) -> typing.Self:
        self.is_playing: bool = False
        return self


class Slideshow(UIElement):
    def __init__(self,
                 surfaces: list[pygame.Surface],
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 settings: settings.SlideshowSettings = settings.SlideshowDefaultSettings
                 ):
        super().__init__(relative_rect, element_id, style_id,
                         ("element", "image", "slideshow"), parent, ui_manager)
        self.settings = settings
        self.left_arrow = Button(self.settings.left_arrow_txt,
                                 pygame.Rect(0, 0, 100, 100),
                                 self.element_id+"_left_arrow",
                                 (self.settings.arrows_style_id if self.settings.arrows_style_id !=
                                  "copy" else self.style_id),
                                 False,
                                 self,
                                 self.ui_manager,
                                 )
        self.right_arrow = Button(self.settings.right_arrow_txt,
                                  pygame.Rect(0, 0, 100, 100),
                                  self.element_id+"_right_arrow",
                                  (self.settings.arrows_style_id if self.settings.arrows_style_id !=
                                   "copy" else self.style_id),
                                  False,
                                  self,
                                  self.ui_manager,
                                  )
        self.left_arrow.status.add_listener("on_stop_press",self.on_left_click)
        self.right_arrow.status.add_listener("on_stop_press",self.on_right_click)
        self.left_arrow.add_element_types(
            "slideshow_arrow", "slideshow_left_arrow")
        self.right_arrow.add_element_types(
            "slideshow_arrow", "slideshow_right_arrow")
        self.set_surfaces(surfaces)
        self.deactivate()
        self.build()

    def set_surfaces(self, surfaces: list[pygame.Surface]) -> typing.Self:
        if len(surfaces) <= 0:
            raise UIError(
                f"Slideshow surfaces list must contain at least 1 surface")
        self.surfaces: list[pygame.Surface] = surfaces
        self.surface_index: int = 0
        self.set_surface(self.surfaces[self.surface_index])
        return self

    def set_surface(self, surface: pygame.Surface) -> typing.Self:
        self.image.set_surface(surface)
        return self

    def set_surface_index(self, index: int) -> typing.Self:
        self.surface_index = pygame.math.clamp(index, 0, len(self.surfaces)-1)
        self.set_surface(self.surfaces[self.surface_index])
        return self

    def move_right(self) -> typing.Self:
        self.surface_index += 1
        if self.surface_index >= len(self.surfaces):
            self.surface_index = 0
        self.set_surface(self.surfaces[self.surface_index])
        return self

    def move_left(self) -> typing.Self:
        self.surface_index -= 1
        if self.surface_index < 0:
            self.surface_index = len(self.surfaces)-1
        self.set_surface(self.surfaces[self.surface_index])
        return self

    def on_right_click(self):
        self.move_right()
        _post_slideshow_event("right", self)
        self.status.invoke_callback("on_move", "right")

    def on_left_click(self):
        self.move_left()
        _post_slideshow_event("left", self)
        self.status.invoke_callback("on_move", "left")

    def size_changed(self):
        size = (self.settings.arrows_w, self.relative_rect.h *
                self.settings.arrows_rel_h)
        self.left_arrow.set_size(size)
        self.right_arrow.set_size(size)
        self.left_arrow.set_relative_pos((self.settings.arrows_padding,
                                          self.relative_rect.h//2-self.left_arrow.relative_rect.h//2))
        self.right_arrow.set_relative_pos((self.relative_rect.w-self.settings.arrows_padding-self.right_arrow.relative_rect.w,
                                           self.relative_rect.h//2-self.left_arrow.relative_rect.h//2))


class Label(UIElement):
    def __init__(self,
                 text: str,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id,
                         style_id, ("element", "label"), parent, ui_manager)
        self.text.set_text(text)
        self.deactivate()

    def set_text(self, text: str) -> typing.Self:
        self.text.set_text(text)
        return self


class Icon(UIElement):
    def __init__(self,
                 name: str|None,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id,
                         style_id, ("element", "icon"), parent, ui_manager)
        self.icon.set_icon(name)
        self.deactivate()
        
    def set_icon(self, name: str) -> typing.Self:
        self.icon.set_icon(name)
        return self


class Image(UIElement):
    def __init__(self,
                 surface: pygame.Surface,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id,
                         style_id, ("element", "image"), parent, ui_manager)
        self.image.set_surface(surface)

        self.deactivate()

    def set_surface(self, surface: pygame.Surface) -> typing.Self:
        self.image.set_surface(surface)
        return self


class Button(UIElement):
    def __init__(self,
                 text: str,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 selectable: bool = False,
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id, style_id, ("element", "button"), parent,
                         ui_manager)
        self.text.set_text(text)
        self.status.can_select = selectable

    def set_text(self, text: str) -> typing.Self:
        self.text.set_text(text)
        return self


class ImageButton(UIElement):
    def __init__(self,
                 surface: pygame.Surface,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 selectable: bool = False,
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id,
                         style_id, ("element", "image", "button", "image_button"), parent, ui_manager)
        self.image.set_surface(surface)
        self.status.can_select = selectable

    def set_surface(self, surface: pygame.Surface) -> typing.Self:
        self.image.set_surface(surface)
        return self
   
    
class IconButton(UIElement):
    def __init__(self,
                 name: str|None,
                 relative_rect: pygame.Rect,
                 element_id: str = "none",
                 style_id: str = "default",
                 selectable: bool = False,
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id,
                         style_id, ("element", "icon", "button", "icon_button"), parent, ui_manager)
        self.icon.set_icon(name)
        if selectable: self.status.can_select = True
        
    def set_icon(self, name: str) -> typing.Self:
        self.icon.set_icon(name)
        return self


class Checkbox(UIElement):
    def __init__(self,
                 relative_rect: pygame.Rect,
                 start_selected: bool = False,
                 element_id: str = "none",
                 style_id: str = "default",
                 parent: UIElement | None = None,
                 ui_manager: UIManager | None = None,
                 #align: ElementAlign = ElementAlign.middle,
                 ):
        super().__init__(relative_rect, element_id, style_id, ("element", "button", "checkbox"), parent,
                         ui_manager)
        self.status.can_select = True
        self.status.selected = start_selected

    def get_selected(self) -> bool:
        return self.status.selected

    def select(self) -> typing.Self:
        self.status.select()
        return self

    def deselect(self) -> typing.Self:
        self.status.deselect()
        return self
