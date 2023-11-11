import pygame
import typing
import pathlib
if typing.TYPE_CHECKING:
    from .elements.element import UIElement

from . import common
from . import enums
from .animation import UIStyleAnim
from .error import UIError


class UICompStyle:
    def __init__(self):
        self.enabled: bool = True
        
    def set(self, **properties) -> typing.Self:
        for name, val in properties.items():
            setattr(self, name, val)
        return self


class UIStackStyle:
    def __init__(self):
        self.spacing: int = 5
        self.padding: int = 7
        self.scroll_x: bool = True
        self.scroll_y: bool = True
        self.grow_x: bool = False
        self.grow_y: bool = False
        self.shrink_x: bool = False
        self.shrink_y: bool = False
        self.fill_x: bool = False
        self.fill_y: bool = False
        self.anchor: enums.StackAnchor = enums.StackAnchor.middle
        self.align: enums.ElementAlign = enums.ElementAlign.middle
        self.scrollbar_size: int = 10


class UIBGStyle(UICompStyle):
    def __init__(self):
        super().__init__()
        self.color: common.Color = (25, 25, 25)
        self.border_radius: int = 7


class UIImageStyle(UICompStyle):
    def __init__(self):
        super().__init__()
        self.image: pygame.Surface | None = None
        self.padding: int = 5
        self.border_radius: int = 7
        self.stretch_x: bool = False
        self.stretch_y: bool = False
        self.fill: bool = False
        self.border_size: int = 0
        self.outline_width = 0
        self.outline_color = (50, 50, 50)


class UIShapeStyle(UICompStyle):
    def __init__(self):
        super().__init__()
        self.color: common.Color = (0, 120, 255)
        self.outline_width: int = 0
        self.type: enums.ShapeType | str = "rect"
        self.padding: int = 8
        self.rect_border_radius: int = 7
        self.polygon_points: list[common.Coordinate] = []
        self.ellipse_padding_x: int = 10
        self.ellipse_padding_y: int = 20


class UITextStyle(UICompStyle):
    def __init__(self):
        super().__init__()
        self.text: str = ""
        self.color: common.Color = (255, 255, 255)
        self.selection_color: common.Color = (0, 100, 200)
        self.bg_color: common.Color | None = None
        self.padding: int = 5
        self.y_padding: int = 1
        self.align: enums.TextAlign | str = "center"
        self.antialas: bool = True
        self.font_name: str = "Segoe UI"
        self.font_size: int = 22
        self.sysfont: bool = True
        self.font_align: enums.FontAlign | int = pygame.FONT_CENTER
        self.bold: bool = False
        self.italic: bool = False
        self.underline: bool = False
        self.strikethrough: bool = False
    
        self.build_font()
        self.apply_mods()

    def build_font(self) -> typing.Self:
        func = pygame.font.SysFont if self.sysfont else pygame.Font
        font_name = self.font_name
        if font_name == "googleicons":
            font_name = str(pathlib.Path(__file__).parent) + \
                "/googleiconsfontttf.py"
            func = pygame.Font
        self.font = func(font_name, int(self.font_size))
        return self

    def apply_mods(self) -> typing.Self:
        self.font.align = self.font_align
        self.font.bold = self.bold
        self.font.italic = self.italic
        self.font.underline = self.underline
        self.font.strikethrough = self.strikethrough
        return self


class UIIconStyle(UICompStyle):
    def __init__(self):
        super().__init__()
        self.name: str | None = None
        self.scale: float = 1
        self.padding: int = 5
        self.align: enums.TextAlign | str = "center"


class UIOutlineStyle(UICompStyle):
    def __init__(self):
        super().__init__()
        self.color: common.Color = (50, 50, 50)
        self.width: int = 1
        self.border_radius: int = 7
        self.navigation_color: common.Color = (255, 0, 0)


class UIStyle:
    def __init__(self):
        self.stack: UIStackStyle = UIStackStyle()
        self.bg: UIBGStyle = UIBGStyle()
        self.image: UIImageStyle = UIImageStyle()
        self.shape: UIShapeStyle = UIShapeStyle()
        self.text: UITextStyle = UITextStyle()
        self.icon: UIIconStyle = UIIconStyle()
        self.outline: UIOutlineStyle = UIOutlineStyle()
        
        self.style_group: "UIStyleGroup" = None
        self.dirty: bool = True
        self.animations: list[UIStyleAnim] = []
        self.styles: tuple[UICompStyle] = (
            self.bg, self.image, self.shape, self.text, self.outline)
        
    def add_animation(self,
                      comp_name: str,
                      property_name: str,
                      property_type: enums.StyleAnimPropertyType,
                      duration_ms: float,
                      value,
                      ease_func_name: enums.AnimEaseFunc = enums.AnimEaseFunc.ease_in
                      ) -> typing.Self:
        self.animations.append(
            UIStyleAnim(self, (self.style_group.style, self.style_group.hover_style, self.style_group.press_style), 
                        comp_name, property_name, property_type, duration_ms, value, ease_func_name)
        )
        return self
        
    def logic(self):
        for anim in self.animations:
            if not anim.completed:
                anim.logic()
        
    def enter(self):
        for anim in self.animations:
            anim.start()

def _default_style() -> UIStyle:
    return UIStyle()


def _default_hover_style() -> UIStyle:
    default_hover = UIStyle()
    default_hover.bg.color = (32, 32, 32)
    return default_hover


def _default_press_style() -> UIStyle:
    default_press = UIStyle()
    default_press.bg.color = (17, 17, 17)
    return default_press


class UIStyleHolder:
    def __init__(self, properties: dict[str, dict[str]],
                 animations: list,
                 style_type: enums.StyleType | str,
                 style_target: enums.StyleTarget | str,
                 target_id: str
                 ):
        self.properties: dict[str, dict[str]] = properties
        self.animations: list = animations
        self.style_type: str = style_type
        self.style_target: str = style_target
        self.target_id: str = target_id

    def copy_as_type(self, style_type: enums.StyleType | str) -> "UIStyleHolder":
        return UIStyleHolder(self.properties, self.animations, style_type, self.style_target, self.target_id)

    def __repr__(self):
        return f"UIStyleHolder(style_type={self.style_type}, style_target={self.style_target}, target_id={self.target_id}, \nproperties={self.properties}\n)\n"


class UIStyleGroup:
    def __init__(self, style: UIStyle, hover_style: UIStyle, press_style: UIStyle):
        self.style: UIStyle = style
        self.hover_style: UIStyle = hover_style
        self.press_style: UIStyle = press_style
        self.style.style_group = self
        self.hover_style.style_group = self
        self.press_style.style_group = self


class UIStyles:
    styles: list[UIStyleHolder] = []

    @classmethod
    def add_style(cls, style_holder: UIStyleHolder):
        cls.styles.append(style_holder)

    @classmethod
    def add_styles(cls, *style_holders: UIStyleHolder):
        for holder in style_holders:
            cls.styles.append(holder)

    @classmethod
    def get_style_group(cls, element: "UIElement") -> UIStyleGroup:
        normal_style, normal_anims = cls.get_style_of_type(element, "normal")
        hover_style, hover_anims = cls.get_style_of_type(element, "hover")
        press_style, press_anims = cls.get_style_of_type(element, "press")
        group = UIStyleGroup(
            normal_style,
            hover_style,
            press_style
        )
        for normal_anim in normal_anims:
            group.style.add_animation(*normal_anim)
        for hover_anim in hover_anims:
            group.hover_style.add_animation(*hover_anim)
        for press_anim in press_anims:
            group.press_style.add_animation(*press_anim)
        return group

    @classmethod
    def get_style_of_type(cls, element: "UIElement", type_: enums.StyleType | str) -> tuple[UIStyle, list]:
        match type_:
            case "normal":
                style = _default_style()
            case "hover":
                style = _default_hover_style()
            case "press":
                style = _default_press_style()
        el_types, style_id, el_id = element.element_types, element.style_id.strip(), element.element_id.strip()
        style_id_styles, el_id_styles = [], []
        animations: list = []
        el_type_styles: dict[str, UIStyleHolder] = {
            el_t: [] for el_t in el_types}
        for style_holder in cls.styles:
            if style_holder.style_type != type_:
                continue
            if style_holder.style_target == "element_type" and style_holder.target_id in el_type_styles:
                el_type_styles[style_holder.target_id].append(style_holder)
            elif style_holder.style_target == "style_id" and (style_holder.target_id == style_id or ";"+style_holder.target_id+";" in style_id or style_id.endswith(";"+style_holder.target_id) or style_id.startswith(style_holder.target_id+";")):
                style_id_styles.append(style_holder)
            elif style_holder.style_target == "element_id" and style_holder.target_id == el_id:
                el_id_styles.append(style_holder)
        for el_type_styles_i in el_type_styles.values():
            for el_type_style in el_type_styles_i:
                cls.apply_style_properties(el_type_style.properties, style)
                animations = cls.update_style_animations(animations, el_type_style.animations)
        for style_id_style in style_id_styles:
            cls.apply_style_properties(style_id_style.properties, style)
            animations = cls.update_style_animations(animations, style_id_style.animations)
        for el_id_style in el_id_styles:
            cls.apply_style_properties(el_id_style.properties, style)
            animations = cls.update_style_animations(animations, el_id_style.animations)
        return style, animations

    @classmethod
    def apply_style_properties(cls, properties: dict[str, dict[str]], style: UIStyle):
        for comp_name in ["stack", "bg", "image", "shape", "text", "icon", "outline"]:
            if comp_name in properties:
                comp = getattr(style, comp_name)
                for name, value in properties[comp_name].items():
                    if not hasattr(comp, name):
                        raise UIError(
                            f"{comp_name.title()} style has no property '{name}'")
                    setattr(comp, name, value)
        style.text.build_font()
        style.text.apply_mods()
        
    @classmethod
    def update_style_animations(cls, current_animations: list, holder_animations: list) -> list:
        new_anims = current_animations.copy()
        for anim_data in holder_animations:
            for old_anim_data in list(new_anims):
                if old_anim_data[0] == anim_data[0] and old_anim_data[1] == anim_data[1]:
                    new_anims.remove(old_anim_data)
            new_anims.append(anim_data)
        return new_anims
