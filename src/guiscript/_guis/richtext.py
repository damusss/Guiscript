import pygame
from enum import StrEnum
from html import parser as html_parser


class ModifierName(StrEnum):
    font_name = "font-name"
    font_size = "font-size"
    fg_color = "fg-color"
    bg_color = "bg-color"
    antialiasing = "antialiasing"
    bold = "bold"
    underline = "underline"
    italic = "italic"
    strikethrough = "strike"


def modifier_of_char(char_i: int, modifier_name: ModifierName, modifiers, default_modifiers, start_i: int):
    for mod in modifiers[modifier_name]:
        if (mod[0]-start_i) <= char_i and (mod[1]-start_i) >= char_i:
            return mod[2] if len(mod) == 3 else False
    return default_modifiers[modifier_name]


def modifiers_of_char(char_i: int, modifiers, default_modifiers, start_i: int):
    return {
        ModifierName.font_name: modifier_of_char(char_i, ModifierName.font_name, modifiers, default_modifiers, start_i),
        ModifierName.font_size: modifier_of_char(char_i, ModifierName.font_size, modifiers, default_modifiers, start_i),
        ModifierName.fg_color: modifier_of_char(char_i, ModifierName.fg_color, modifiers, default_modifiers, start_i),
        ModifierName.bg_color: modifier_of_char(char_i, ModifierName.bg_color, modifiers, default_modifiers, start_i),
        ModifierName.antialiasing: modifier_of_char(char_i, ModifierName.antialiasing, modifiers, default_modifiers, start_i),
        ModifierName.italic: modifier_of_char(char_i, ModifierName.italic, modifiers, default_modifiers, start_i),
        ModifierName.bold: modifier_of_char(char_i, ModifierName.bold, modifiers, default_modifiers, start_i),
        ModifierName.underline: modifier_of_char(char_i, ModifierName.underline, modifiers, default_modifiers, start_i),
        ModifierName.strikethrough: modifier_of_char(char_i, ModifierName.strikethrough, modifiers, default_modifiers, start_i),
    }


class RichTextParser(html_parser.HTMLParser):
    """Internal rich text parser using the builtin html parser. Functions aren't be documented"""

    def __init__(self):
        super().__init__()
        self.reset_text("")

    def reset_text(self, raw_text: str):
        self.raw_text: str = raw_text
        self.output_text: str = ""
        self.modifiers = {
            ModifierName.font_name: [],
            ModifierName.font_size: [],
            ModifierName.fg_color: [],
            ModifierName.bg_color: [],
            ModifierName.antialiasing: [],
            ModifierName.bold: [],
            ModifierName.underline: [],
            ModifierName.italic: [],
            ModifierName.strikethrough: [],
        }
        self.modifiers_stack: list = []
        self.start_i_stack: list[int] = []

    def parse_text(self, raw_text: str) -> tuple[str]:
        self.reset_text(raw_text)
        self.feed(self.raw_text)
        self.close()
        return self.output_text, self.modifiers

    def handle_data(self, data: str) -> None:
        self.output_text += data

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.modifiers_stack.append([tag, attrs])
        self.start_i_stack.append(len(self.output_text))

    def handle_endtag(self, tag: str) -> None:
        try:
            modifier = self.modifiers_stack[-1]
            start_i = self.start_i_stack[-1]
            end_i = len(self.output_text)-1
        except IndexError:
            return

        self.parse_modifier(modifier, start_i, end_i)

        self.modifiers_stack.pop()
        self.start_i_stack.pop()

    def parse_modifier(self, mod: tuple[str, tuple[str, str]], start_i: int, end_i: int):
        tag_name = mod[0]
        tagmod = tag_name.lower().strip()
        match tagmod:
            case "i" | "italic":
                self.modifiers[ModifierName.italic].append(
                    [start_i, end_i, True])
            case "b" | "bold":
                self.modifiers[ModifierName.bold].append(
                    [start_i, end_i, True])
            case "u" | "underline":
                self.modifiers[ModifierName.underline].append(
                    [start_i, end_i, True])
            case "s" | "strike" | "strikethrough":
                self.modifiers[ModifierName.strikethrough].append(
                    [start_i, end_i, True])
            case "a" | "antialasing" | "antialas":
                self.modifiers[ModifierName.antialiasing].append(
                    [start_i, end_i, True])
            case "f" | "font":
                for attr, value in mod[1]:
                    attrmod = attr.lower().strip()
                    match attrmod:
                        case "size":
                            self.modifiers[ModifierName.font_size].append(
                                [start_i, end_i, eval(value)])
                        case "name":
                            self.modifiers[ModifierName.font_name].append(
                                [start_i, end_i, value])
            case "c" | "color":
                for attr, value in mod[1]:
                    attrmod = attr.lower().strip()
                    match attrmod:
                        case "fg":
                            self.modifiers[ModifierName.fg_color].append(
                                [start_i, end_i, value if value.replace(" ", "").isalpha() else eval(value)])
                        case "bg":
                            self.modifiers[ModifierName.bg_color].append(
                                [start_i, end_i, value if value.replace(" ", "").isalpha() else eval(value)])


class TextAlign(StrEnum):
    """
    Enum to specify the alignment of the paragraph. Strings can be used but not recommended
    NOTE: Center is replaced with middle for IDE linting errors
    """
    middle = "middle"
    left = "left"
    right = "right"


class FontCache:
    def __init__(self):
        self.cache: dict[str, pygame.Font] = {}

    def refresh_cache(self, modifiers, default_modifiers):
        sysfonts = pygame.font.get_fonts()
        done_names = []
        done_sizes = []
        dfn, dfs = default_modifiers[ModifierName.font_name], default_modifiers[ModifierName.font_size]
        for _, _, font_name in list(modifiers[ModifierName.font_name])+[[0, 0, dfn]]:
            if font_name in done_names:
                continue
            for _, _, font_size in list(modifiers[ModifierName.font_size])+[[0, 0, dfs]]:
                if font_size in done_sizes:
                    continue
                cache_str = f"{font_name}_{font_size}"
                if cache_str in self.cache:
                    continue

                font_func = pygame.font.SysFont if font_name is not None and font_name.lower(
                ).replace(" ", "") in sysfonts else pygame.Font
                self.cache[cache_str] = font_func(font_name, font_size)

                done_sizes.append(font_size)
            done_names.append(font_name)

    def reset(self):
        self.cache = {}


def render(text: str,
           modifiers,
           default_modifiers,
           font_cache: FontCache,
           align=TextAlign.middle,
           wraplength=500,
           start_i: int = 0,
           end_i: int = -1,
           mask: pygame.Rect = None,
           strict_mask: bool = False,
           ) -> tuple[pygame.Surface, pygame.Rect | None]:
    font_cache.refresh_cache(modifiers, default_modifiers)
    text = text[start_i:] if end_i == -1 else text[start_i:end_i]

    longest_line = cur_x = tallest_char = total_h = 0
    lines, cur_line = [], []
    for i, char in enumerate(text):
        if char == "\n":
            if cur_x > longest_line:
                longest_line = cur_x
            cur_line.append(tallest_char)
            cur_line.append(cur_x)
            total_h += tallest_char
            lines.append(cur_line)
            tallest_char = cur_x = 0
            cur_line = []
            continue
        char_mods = modifiers_of_char(i, modifiers, default_modifiers, start_i)
        font = font_cache.cache[f"{char_mods[ModifierName.font_name]}_{
            char_mods[ModifierName.font_size]}"]
        char_w, char_h = font.size(char)
        if wraplength != -1:
            if cur_x + char_w > wraplength:
                if cur_x > longest_line:
                    longest_line = cur_x
                cur_line.append(tallest_char)
                cur_line.append(cur_x)
                total_h += tallest_char
                lines.append(cur_line)
                tallest_char = cur_x = 0
                cur_line = []

        cur_line.append((char_mods, char_w, char_h, font, char))
        if char_h > tallest_char:
            tallest_char = char_h
        cur_x += char_w

    if cur_x > 0:
        if cur_x > longest_line:
            longest_line = cur_x
        cur_line.append(tallest_char)
        cur_line.append(cur_x)
        total_h += tallest_char
        lines.append(cur_line)

    line_w = longest_line
    if mask is not None:
        if longest_line > mask.w:
            longest_line = mask.w
        if total_h > mask.h:
            total_h = mask.h

    render_surf = pygame.Surface((longest_line, total_h), pygame.SRCALPHA)
    render_surf.fill(0)
    render_rect = pygame.Rect(
        0, 0, mask.w, mask.h) if mask is not None else render_surf.get_rect()

    y = i = 0
    for line in lines:
        x = 0
        tall = line[-2]
        this_line_w = line[-1]
        line.pop()
        line.pop()
        for c_mods, c_w, c_h, font, char in line:
            rx = x
            if align == TextAlign.right:
                rx = line_w-this_line_w+x
            elif align == TextAlign.middle:
                rx = (line_w//2)-(this_line_w//2)+x
            pos = (rx, y+((tall//2)-c_h//2))
            x += c_w

            if mask is not None:
                c1, c2 = mask.collidepoint(pos), mask.collidepoint(
                    (pos[0]+c_w, pos[1]+c_h))
                if ((not c1 and not c2) and not strict_mask) or ((not c1 or not c2) and strict_mask):
                    i += 1
                    continue
                pos = (pos[0]-mask.x, pos[1]-mask.y)

            font.bold, font.italic, font.underline, font.strikethrough = (
                c_mods[ModifierName.bold],
                c_mods[ModifierName.italic],
                c_mods[ModifierName.underline],
                c_mods[ModifierName.strikethrough],
            )
            render_surf.blit(font.render(char,
                                         c_mods[ModifierName.antialiasing],
                                         c_mods[ModifierName.fg_color],
                                         c_mods[ModifierName.bg_color]),
                             pos)
            i += 1

        y += tall
    return render_surf


global_rich_text_parser: RichTextParser = RichTextParser()
global_font_cache: FontCache = FontCache()
