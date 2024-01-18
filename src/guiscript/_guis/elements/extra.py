import pygame
import typing

from .stacks import VStack, HStack
from .factories import Slider, Image
from .entries import Entry
from .element import Element
from ..manager import Manager
from .. import common
from .. import settings as settings_
from .. import events


class ColorPicker(VStack):
    """Builtin element that have UI to select color values"""

    def __init__(self,
                 relative_rect: pygame.Rect,
                 start_color: common.Color = pygame.Color(0,0,0,255),
                 element_id: str = "none",
                 style_id: str = "",
                 parent: Element | None = None,
                 manager: Manager | None = None,
                 settings: settings_.ColorPickerSettings|None = None,
                 ):
        if settings is None:
            settings = settings_.ColorPickerSettings()
        if settings.slider_settings is None:
            settings.slider_settings = settings_.SliderSettings()
        if settings.entry_settings is None:
            settings.entry_settings = settings_.EntrySettings(placeholder="Enter value...")
        if settings.hex_entry_settings is None:
            settings.hex_entry_settings = settings_.EntrySettings(placeholder="Enter hex value...")
        super().__init__(relative_rect, element_id, style_id, parent, manager)
        self.add_element_type("colorpicker").status.register_callback("on_change")
        self.settings: settings_.ColorPickerSettings = settings
        self.color: pygame.Color = pygame.Color(start_color)
        
        previews_sid, entries_sid, sliders_sid = common.style_id_or_copy(self, settings.previews_style_id),\
                                                 common.style_id_or_copy(self, settings.entries_style_id),\
                                                 common.style_id_or_copy(self, settings.sliders_style_id)
        if self.settings.main_preview:
            self.preview_image: Image = Image(None, pygame.Rect(0,0,0,0), self.element_id+"_preview_image", common.style_id_or_copy(self, settings.main_preview_style_id), self, self.manager)\
                .add_element_types("colorpicker_preview", "colorpicker_preview_image").set_attr("builtin", True)
        else:
            self.preview_image = None
        # R
        with HStack(pygame.Rect(0,0,0,settings.rows_h),self.element_id+"_row_r", "invis_cont", self, self.manager)\
            .add_element_types("colorpicker_row", "colorpicker_row_r").set_attr("builtin", True) as self.row_r:
            self.slider_r: Slider = Slider(pygame.Rect(0,0,0,settings.rows_h), self.element_id+"_slider_r", sliders_sid, manager=self.manager, settings=settings.slider_settings)\
                .add_element_types("colorpicker_slider", "colorpicker_slider_r").set_attr("builtin", True)\
                .status.add_listener("on_move", self._on_r_move).element
            self.entry_r: Entry = Entry(pygame.Rect(0,0,settings.entries_w, settings.rows_h), self.color.r, self.element_id+"_entry_r", entries_sid, manager=self.manager, settings=settings.entry_settings)\
                .add_element_types("colorpicker_entry", "colorpicker_entry_r").set_attr("builtin", True)\
                .status.add_listener("on_change", self._on_r_change).element
            self.preview_r: Image = Image(None, pygame.Rect(0,0,settings.previews_w, settings.rows_h), self.element_id+"_preview_r", previews_sid, manager=self.manager)\
                .add_element_types("colorpicker_preview", "colorpicker_preview_r").set_attr("builtin", True)
        # G
        with HStack(pygame.Rect(0,0,0,settings.rows_h),self.element_id+"_row_g", "invis_cont", self, self.manager)\
            .add_element_types("colorpicker_row", "colorpicker_row_g").set_attr("builtin", True) as self.row_g:
            self.slider_g: Slider = Slider(pygame.Rect(0,0,0,settings.rows_h), self.element_id+"_slider_g", sliders_sid, manager=self.manager, settings=settings.slider_settings)\
                .add_element_types("colorpicker_slider", "colorpicker_slider_g").set_attr("builtin", True)\
                .status.add_listener("on_move", self._on_g_move).element
            self.entry_g: Entry = Entry(pygame.Rect(0,0,settings.entries_w, settings.rows_h), self.color.g, self.element_id+"_entry_g", entries_sid, manager=self.manager, settings=settings.entry_settings)\
                .add_element_types("colorpicker_entry", "colorpicker_entry_g").set_attr("builtin", True)\
                .status.add_listener("on_change", self._on_g_change).element
            self.preview_g: Image = Image(None, pygame.Rect(0,0,settings.previews_w, settings.rows_h), self.element_id+"_preview_g", previews_sid, manager=self.manager)\
                .add_element_types("colorpicker_preview", "colorpicker_preview_g").set_attr("builtin", True)
        # B
        with HStack(pygame.Rect(0,0,0,settings.rows_h),self.element_id+"_row_b", "invis_cont", self, self.manager)\
            .add_element_types("colorpicker_row", "colorpicker_row_b").set_attr("builtin", True) as self.row_b:
            self.slider_b: Slider = Slider(pygame.Rect(0,0,0,settings.rows_h), self.element_id+"_slider_b", sliders_sid, manager=self.manager, settings=settings.slider_settings)\
                .add_element_types("colorpicker_slider", "colorpicker_slider_b").set_attr("builtin", True)\
                .status.add_listener("on_move", self._on_b_move).element
            self.entry_b: Entry = Entry(pygame.Rect(0,0,settings.entries_w, settings.rows_h), self.color.b, self.element_id+"_entry_b", entries_sid, manager=self.manager, settings=settings.entry_settings)\
                .add_element_types("colorpicker_entry", "colorpicker_entry_b").set_attr("builtin", True)\
                .status.add_listener("on_change", self._on_b_change).element
            self.preview_b: Image = Image(None, pygame.Rect(0,0,settings.previews_w, settings.rows_h), self.element_id+"_preview_b", previews_sid, manager=self.manager)\
                .add_element_types("colorpicker_preview", "colorpicker_preview_b").set_attr("builtin", True)
        # A
        if settings.alpha:
            with HStack(pygame.Rect(0,0,0,settings.rows_h),self.element_id+"_row_a", "invis_cont", self, self.manager)\
                .add_element_types("colorpicker_row", "colorpicker_row_a").set_attr("builtin", True) as self.row_a:
                self.slider_a: Slider = Slider(pygame.Rect(0,0,0,settings.rows_h), self.element_id+"_slider_a", sliders_sid, manager=self.manager, settings=settings.slider_settings)\
                    .add_element_types("colorpicker_slider", "colorpicker_slider_a").set_attr("builtin", True)\
                    .status.add_listener("on_move", self._on_a_move).element
                self.entry_a: Entry = Entry(pygame.Rect(0,0,settings.entries_w, settings.rows_h), self.color.a, self.element_id+"_entry_a", entries_sid, manager=self.manager, settings=settings.entry_settings)\
                    .add_element_types("colorpicker_entry", "colorpicker_entry_a").set_attr("builtin", True)\
                    .status.add_listener("on_change", self._on_a_change).element
                self.preview_a: Image = Image(None, pygame.Rect(0,0,settings.previews_w, settings.rows_h), self.element_id+"_preview_a", previews_sid, manager=self.manager)\
                    .add_element_types("colorpicker_preview", "colorpicker_preview_a").set_attr("builtin", True)
        else:
            self.row_a = None
            self.slider_a = None
            self.entry_a = None
            self.preview_a = None
        if settings.hex:
            self.hex_entry: Entry = Entry(pygame.Rect(0,0,0,settings.rows_h), self.get_hex(), self.element_id+"_hex_entry", entries_sid, self, self.manager)\
                .add_element_types("colorpicker_entry", "colorpicker_hex_entry").set_attr("builtin", True)\
                .status.add_listener("on_change", self._on_hex_change).element
        else:
            self.hex_entry = None
        
        self._color_changed()
        
    def _on_r_move(self):
        self.color.r = int(self.slider_r.get_value()*255)
        self._color_changed_s()
        
    def _on_g_move(self):
        self.color.g = int(self.slider_g.get_value()*255)
        self._color_changed_s()
        
    def _on_b_move(self):
        self.color.b = int(self.slider_b.get_value()*255)
        self._color_changed_s()
        
    def _on_a_move(self):
        self.color.a = int(self.slider_a.get_value()*255)
        self._color_changed_s()
        
    def _on_r_change(self, *args):
        v = self._parse_entry_v(self.entry_r.get_text())
        if v is None:
            return
        self.color.r = v
        self._color_changed_e()
        
    def _on_g_change(self, *args):
        v = self._parse_entry_v(self.entry_g.get_text())
        if v is None:
            return
        self.color.g = v
        self._color_changed_e()
        
    def _on_b_change(self, *args):
        v = self._parse_entry_v(self.entry_b.get_text())
        if v is None:
            return
        self.color.b = v
        self._color_changed_e()
        
    def _on_a_change(self, *args):
        v = self._parse_entry_v(self.entry_a.get_text())
        if v is None:
            return
        self.color.a = v
        self._color_changed_e()
        
    def _on_hex_change(self, *args):
        hexv = self.hex_entry.get_text().replace("#", "").strip()
        if len(hexv) != 6 and len(hexv) != 8:
            return
        if not all([char.lower() in "abcdef0123456789" for char in hexv]):
            return
        if not self.settings.alpha and len(hexv) == 8:
            hexv = hexv[0:-2]
        if self.settings.alpha and len(hexv) == 6:
            hexv += "00"
        self._hex_changed("#"+hexv)
        
    def _parse_entry_v(self, txt):
        try:
            v = float(txt)
        except ValueError:
            return None
        if self.settings.range_01:
            v *= 255
        return int(pygame.math.clamp(v, 0, 255))
        
    def _update_previews(self):
        self.preview_r.style.image.fill_color = pygame.Color(self.color.r, 0, 0, 255)
        self.preview_g.style.image.fill_color = pygame.Color(0, self.color.g, 0, 255)
        self.preview_b.style.image.fill_color = pygame.Color(0,0,self.color.b, 255)
        self.preview_r.build_components()
        self.preview_g.build_components()
        self.preview_b.build_components()
        if self.settings.main_preview:
            self.preview_image.style.image.fill_color = pygame.Color(self.color)
            self.preview_image.build_components()
        if self.settings.alpha:
            self.preview_a.style.image.fill_color = pygame.Color(255,255,255,self.color.a)
            self.preview_a.build_components()
        
    def _update_hex(self):
        if self.settings.hex:
            self.hex_entry.set_text(common.rgba_to_hex(self.color.r, self.color.g, self.color.b, self.color.a if self.settings.alpha else None))
        
    def _hex_changed(self, hexv):
        rgb = common.hex_to_rgba(hexv, self.settings.alpha)
        if self.settings.alpha:
            self.color.r, self.color.g, self.color.b, self.color.a = rgb
        else:
            self.color.r, self.color.g, self.color.b = rgb
        self._update_sliders()
        self._update_entries()
        self._update_previews()
        self._changed_events()
        
    def _update_sliders(self):
        self.slider_r.set_value(self.color.r/255)
        self.slider_g.set_value(self.color.g/255)
        self.slider_b.set_value(self.color.b/255)
        if self.settings.alpha:
            self.slider_a.set_value(self.color.a/255)
            
    def _update_entries(self):
        if self.settings.range_01:
            rtxt, gtxt, btxt, atxt = round(self.color.r/255, 3), round(self.color.g/255, 3), round(self.color.b/255, 3), round(self.color.a/255, 3)
        else:
            rtxt, gtxt, btxt, atxt = self.color
        self.entry_r.set_text(rtxt)
        self.entry_g.set_text(gtxt)
        self.entry_b.set_text(btxt)
        if self.settings.alpha:
            self.entry_a.set_text(atxt)
        
    def _color_changed(self):
        self._update_sliders()
        self._update_entries()
        self._update_hex()
        self._update_previews()
        self.buffers.update("color", self.color)
        
    def _color_changed_s(self):
        self._update_entries()
        self._update_hex()
        self._update_previews()
        self._changed_events()
        
    def _color_changed_e(self):
        self._update_sliders()
        self._update_hex()
        self._update_previews()
        self._changed_events()
        
    def _changed_events(self):
        self.status.invoke_callback("on_change", self.color)
        events._post_colorpicker_event(self)
        self.buffers.update("color", self.color)
        
    def get_hex(self):
        """Return the hexadecimal representation of the color"""
        return common.rgba_to_hex(self.color.r, self.color.g, self.color.b, self.color.a if self.settings.alpha else None)
        
    def set_color(self, color: common.Color) -> typing.Self:
        """Set the color and refresh the picker"""
        self.color = pygame.Color(color)
        self._color_changed()
        return self
        