import pygame
import typing
import pathlib
import os
from enum import StrEnum

from .style import UIStyles, UIStyleHolder
from .error import UIScriptError
from .enums import StyleType, StyleTarget, AnimEaseFunc, StyleAnimPropertyType
from .icon import Icons
from . import common


class UISTT(StrEnum):
    """[Internal] The type enum of tokens"""
    left_paren = "left_paren"
    right_paren = "right_paren"
    left_brace = "left_brace"
    right_brace = "right_brace"
    semicolon = "semicolon"
    identifier = "identifier"
    number = "number"
    colon = "colon"
    hash = "hash"
    dot = "dot"
    comma = "comma"
    dash = "dash"
    dollar = "dollar"
    bool = "bool"
    null = "null"
    eof = "eof"
    expr = "expr"
    string = "string"
    slash = "slash"
    percent = "percent"


class UIScriptToken:
    """[Internal] Token used when lexing and parsing a GSS Script"""

    def __init__(self, type_: UISTT, value, line: int, col: int):
        self.type: UISTT = type_
        self.value = value
        self.line: int = line
        self.col: int = col

    def __repr__(self) -> str:
        return f"{self.type}:'{self.value}'" if self.value is not None else f"{self.type}"

    def __str__(self) -> str:
        return f"{self.value}" if self.value is not None else f"{self.type}"


class UIScriptLexer:
    """[Internal] Lexer for GSS scripts"""
    start_iden_chars: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    number_chars: str = "0123456789"
    iden_chars: str = start_iden_chars + number_chars
    ignore_chars: str = " \n\t"

    def __init__(self, source: str, filename: str):
        self.filename: str = filename
        self.source: str = source
        self.max_i: int = len(source)-1
        self.tokens: list[UIScriptToken] = []
        self.char: str | None = None
        self.idx: int = -1
        self.line: int = 1
        self.col: int = 0
        self.next_number_negative = False
        self.advance()

    def advance(self):
        self.idx += 1
        if self.idx <= self.max_i:
            self.char = self.source[self.idx]
            if self.char == "\n":
                self.line += 1
                self.col = 0
            else:
                self.col += 1
        else:
            self.char = None
            self.col += 1

    def add_tok(self, type_: UISTT, val=None, advance: bool = True, line=None, col=None):
        self.tokens.append(UIScriptToken(
            type_, val, self.line if not line else line, self.col if not col else col))
        if advance:
            self.advance()

    def make_number(self):
        num = self.char
        sl, sc = self.line, self.col
        self.advance()

        while self.char in self.number_chars+".":
            num += self.char
            self.advance()

        if "." in num:
            num = float(num)
        else:
            num = int(num)
        if self.next_number_negative:
            num *= -1
            self.next_number_negative = False
        self.add_tok(UISTT.number, num, False, sl, sc)

    def make_iden(self):
        iden = self.char
        sl, sc = self.line, self.col
        self.advance()

        while self.char in self.iden_chars:
            iden += self.char
            self.advance()

        if iden == "null":
            self.add_tok(UISTT.null, None, False)
        elif iden in ["true", "false"]:
            self.add_tok(UISTT.bool, iden == "true", False, sl, sc)
        else:
            self.add_tok(UISTT.identifier, iden, False, sl, sc)

    def make_string(self):
        string = ""
        sl, sc = self.line, self.col
        self.advance()

        while self.char != "'":
            string += self.char
            self.advance()

        self.add_tok(UISTT.string, string, True, sl, sc)

    def make_expr(self):
        expr = ""
        sl, sc = self.line, self.col
        self.advance()

        while self.char != '|':
            expr += self.char
            self.advance()

        self.add_tok(UISTT.expr, expr, line=sl, col=sc)

    def lex(self) -> typing.Self:
        if self.max_i < 0:
            self.add_tok(UISTT.eof, advance=False)
            return self

        while self.char is not None:
            if self.char == "/":
                self.advance()
                while self.char != "\n":
                    self.advance()
            if self.char in self.ignore_chars:
                self.advance()
            elif self.char == "(":
                self.add_tok(UISTT.left_paren)
            elif self.char == ")":
                self.add_tok(UISTT.right_paren)
            elif self.char == "{":
                self.add_tok(UISTT.left_brace)
            elif self.char == "}":
                self.add_tok(UISTT.right_brace)
            elif self.char == ";":
                self.add_tok(UISTT.semicolon)
            elif self.char == ":":
                self.add_tok(UISTT.colon)
            elif self.char == ".":
                self.add_tok(UISTT.dot)
            elif self.char == ",":
                self.add_tok(UISTT.comma)
            elif self.char == "#":
                self.add_tok(UISTT.hash)
            elif self.char == "%":
                self.add_tok(UISTT.percent)
            elif self.char == "-":
                self.advance()
                if self.char in self.number_chars:
                    self.next_number_negative = True
                else:
                    self.add_tok(UISTT.dash, None, False)
            elif self.char == "$":
                self.add_tok(UISTT.dollar)
            elif self.char == "'":
                self.make_string()
            elif self.char == '|':
                self.make_expr()
            elif self.char in self.number_chars:
                self.make_number()
            elif self.char in self.start_iden_chars:
                self.make_iden()
            else:
                raise UIScriptError(
                    f"Unknown token '{self.char}' found in script '{self.filename}' at line {self.line}, column {self.col}")

        self.add_tok(UISTT.eof)
        return self


class UIScriptParser:
    "[Internal] Parser for GSS scripts"

    def __init__(self, tokens: list[UIScriptToken], filename: str, variables: dict[str]):
        self.filename: str = filename
        self.variables: dict[str] = variables
        self.eval_globals = self.variables.copy()
        self.eval_globals.update({
            "__import__": None,
            "exec": None,
            "eval": None,
            "compile": None,
            "open": None,
            "quit": None,
            "exit": None,
        })
        self.tokens: list[UIScriptToken] = tokens
        self.max_i: int = len(self.tokens)-1
        self.tok: UIScriptToken = None
        self.idx: int = -1
        self.style_holders: list[UIStyleHolder] = []
        self.advance()

    def error_suffix(self) -> str:
        return f" in script '{self.filename}' at line {self.tok.line}, column {self.tok.col}"

    def advance(self):
        self.idx += 1
        if self.idx <= self.max_i:
            self.tok = self.tokens[self.idx]
        else:
            self.tok = None

    def parse_style_target(self) -> tuple[StyleTarget, list[str]]:
        target = None
        if self.tok.type == UISTT.dot:
            target = StyleTarget.style_id
            self.advance()
            if not self.tok.type == UISTT.identifier:
                raise UIScriptError(
                    f"Expected target id identifier after '.', got '{self.tok}' instead"+self.error_suffix())
        elif self.tok.type == UISTT.hash:
            target = StyleTarget.element_id
            self.advance()
            if not self.tok.type == UISTT.identifier:
                raise UIScriptError(
                    f"Expected target id identifier after '#', got '{self.tok}' instead"+self.error_suffix())
        else:
            target = StyleTarget.element_type
        target_ids = []
        target_ids.append(self.tok.value)
        self.advance()
        while self.tok.type == UISTT.comma:
            self.advance()
            if not self.tok.type == UISTT.identifier:
                raise UIScriptError(
                    f"Expected target id identifier after ',', got '{self.tok}' instead"+self.error_suffix())
            target_ids.append(self.tok.value)
            self.advance()
        return target, target_ids

    def parse_style_type(self) -> tuple[StyleType, StyleType | None, bool]:
        main_type = StyleType.normal
        copy_type = None
        also_normal = False
        if self.tok.type == UISTT.colon:
            self.advance()
            if self.tok.type == UISTT.colon:
                self.advance()
                main_type = StyleType.hover
                copy_type = StyleType.press
                also_normal = True
            else:
                if not self.tok.type == UISTT.identifier:
                    raise UIScriptError(
                        f"Expected style type identifier after ':', got '{self.tok}' instead"+self.error_suffix())
                type_tok = self.tok
                if type_tok.value not in ["hover", "press"]:
                    raise UIScriptError(
                        f"Invalid style type '{type_tok.value}', available are hover and press"+self.error_suffix())
                main_type = type_tok.value
                self.advance()
                if self.tok.type == UISTT.colon:
                    self.advance()
                    if self.tok.type == UISTT.identifier:
                        type_tok = self.tok
                        if type_tok.value not in ["hover", "press"] or type_tok.value == main_type:
                            raise UIScriptError(
                                f"The second style type should only be hover or press and not the same as the first style type"+self.error_suffix())
                        copy_type = type_tok.value
                        self.advance()
                        if self.tok.type == UISTT.colon:
                            self.advance()
                            also_normal = True
                    else:
                        also_normal = True
        return main_type, copy_type, also_normal

    def parse_literal_value(self):
        value = self.tok.value
        self.advance()
        return value

    def parse_string_value(self):
        string = self.tok.value
        self.advance()
        while self.tok.type == UISTT.identifier:
            string += f" {self.tok.value}"
            self.advance()
        return string

    def parse_variable_value(self):
        self.advance()
        if not self.tok.type == UISTT.identifier:
            raise UIScriptError(
                f"Expected variable name identifier after '$', got '{self.tok}' instead"+self.error_suffix())
        var_name = self.tok.value
        if not var_name in self.variables:
            raise UIScriptError(
                f"Variable '{var_name}' does not exist, make sure to provide it to the ui manager;"+self.error_suffix())
        self.advance()
        return self.variables[var_name]

    def parse_list_value(self):
        self.advance()
        values = []
        if self.tok.type != UISTT.right_paren:
            values.append(self.parse_property_value())
            while self.tok.type == UISTT.comma:
                self.advance()
                if self.tok.type == UISTT.right_paren:
                    break
                values.append(self.parse_property_value())
            if not self.tok.type == UISTT.right_paren:
                raise UIScriptError(
                    f"Expected ')' after the last tuple value, got '{self.tok}' instead"+self.error_suffix())
            self.advance()
        else:
            self.advance()
        return values

    def parse_expr_value(self):
        try:
            eval_value = eval(
                self.tok.value, self.eval_globals, self.eval_globals)
        except Exception as e:
            raise UIScriptError(
                f"Tried to parse expression value '{self.tok.value}' with variables as globals using (blacklisted) python eval(), failed with error message: '{e}'"+self.error_suffix())
        else:
            self.advance()
            return eval_value

    def parse_hex_value(self):
        self.advance()
        hex_num = ""
        while self.tok.type == UISTT.identifier or self.tok.type == UISTT.number:
            hex_num += str(self.tok.value)
            self.advance()
        return f"#{hex_num}"

    def parse_property_value(self) -> typing.Any:
        if self.tok.type in [UISTT.number, UISTT.null, UISTT.bool, UISTT.string]:
            return self.parse_literal_value()
        elif self.tok.type == UISTT.identifier:
            return self.parse_string_value()
        elif self.tok.type == UISTT.dollar:
            return self.parse_variable_value()
        elif self.tok.type == UISTT.left_paren:
            return self.parse_list_value()
        elif self.tok.type == UISTT.expr:
            return self.parse_expr_value()
        elif self.tok.type == UISTT.hash:
            return self.parse_hex_value()
        extra_msg = ""
        if self.tok.type == UISTT.semicolon:
            extra_msg = f", perhaps you forgot to close an open parenthesis?"
        raise UIScriptError(
            f"Invalid property value starting with token '{self.tok}'{extra_msg}"+self.error_suffix())

    def parse_style_property(self) -> tuple[str, str, typing.Any]:
        if not self.tok.type == UISTT.identifier:
            raise UIScriptError(
                f"Expected component name identifier inside style block, got '{self.tok.value}' instead"+self.error_suffix())
        if not self.tok.value in ["stack", "bg", "image", "shape", "text", "icon", "outline"]:
            raise UIScriptError(
                f"Supported component names are stack, bg, image, shape, text, icon, outline; got '{self.tok.value}' instead"+self.error_suffix())
        comp_name = self.tok.value
        self.advance()
        if not self.tok.type == UISTT.dot:
            raise UIScriptError(
                f"Expected '.' after component name identifier, got '{self.tok}' instead"+self.error_suffix())
        self.advance()
        if not self.tok.type == UISTT.identifier:
            raise UIScriptError(
                f"Expected property name identifier after '{comp_name}.', got '{self.tok}' instead"+self.error_suffix())
        property_name = self.tok.value
        if property_name in ["set", "build_font", "apply_mods"]:
            raise UIScriptError(
                f"Property name not allowed: '{
                    property_name}'"+self.error_suffix()
            )
        self.advance()
        value = self.parse_property_value()
        if comp_name == "image" and property_name == "image" and value is not None and isinstance(value, str):
            try:
                value = pygame.image.load(value).convert_alpha()
            except:
                raise UIScriptError(f"Could not auto-load surface from path '{value}'"+self.error_suffix())
        if comp_name == "icon" and comp_name == "name" and value is not None and not value in Icons.icons and os.path.exists(value):
            path = pathlib.Path(value)
            if path.is_file():
                Icons.add(path.name, pygame.image.load(
                    value).convert_alpha())
            value = path.name
        return (False, comp_name, property_name, value)

    def parse_style_animation(self):
        self.advance()
        if not self.tok.type == UISTT.identifier:
            raise UIScriptError(
                f"Expected component name identifier inside style animation after '%', got '{self.tok.value}' instead"+self.error_suffix())
        if not self.tok.value in ["stack", "bg", "image", "shape", "text", "icon", "outline"]:
            raise UIScriptError(
                f"Supported component names are stack, bg, image, shape, text, icon, outline; got '{self.tok.value}' instead"+self.error_suffix())
        comp_name = self.tok.value
        self.advance()
        if not self.tok.type == UISTT.dot:
            raise UIScriptError(
                f"Expected '.' after component name identifier, got '{self.tok}' instead"+self.error_suffix())
        self.advance()
        if not self.tok.type == UISTT.identifier:
            raise UIScriptError(
                f"Expected property name identifier after '{comp_name}.', got '{self.tok}' instead"+self.error_suffix())
        property_name = self.tok.value
        if property_name in ["set", "build_font", "apply_mods"]:
            raise UIScriptError(
                f"Property name not allowed: '{
                    property_name}'"+self.error_suffix()
            )
        if not property_name in common.STYLE_ANIMATION_TYPES[comp_name]:
            raise UIScriptError(
                f"Property name '{property_name}''s type does not support animation"+self.error_suffix())
        self.advance()
        value = self.parse_property_value()
        if not self.tok.type == UISTT.comma:
            raise UIScriptError(
                f"Expected comma after style animation value '{value}' and the animation duration in ms after the comma, got '{self.tok.value}' instead"+self.error_suffix())
        self.advance()
        if not self.tok.type == UISTT.number:
            raise UIScriptError(
                f"Expected number representing duration in ms after comma in style animation, got '{self.tok.value}' instead"+self.error_suffix())
        duration = self.tok.value
        ease_func_name = AnimEaseFunc.ease_in
        self.advance()
        if self.tok.type == UISTT.comma:
            self.advance()
            ease_func_name = self.parse_property_value()
            if not isinstance(ease_func_name, str):
                raise UIScriptError(
                    f"Style animation ease function name was evaluated with an unsupported python type '{type(ease_func_name)}', expected 'str'"+self.error_suffix())
        return (True, comp_name, property_name, common.STYLE_ANIMATION_TYPES[comp_name][property_name], duration, value, ease_func_name)

    def parse_style_instruction(self):
        if self.tok.type == UISTT.percent:
            return self.parse_style_animation()
        return self.parse_style_property()

    def parse_style_body(self) -> list[tuple[str, str, typing.Any]]:
        if not self.tok.type == UISTT.left_brace:
            raise UIScriptError("Expected '{' at the start of the style body, got '"+str(
                self.tok)+"' instead"+self.error_suffix())
        self.advance()
        expressions = []
        if self.tok.type == UISTT.right_brace:
            self.advance()
            return expressions
        expressions.append(self.parse_style_instruction())
        while self.tok.type == UISTT.semicolon:
            self.advance()
            if self.tok.type == UISTT.right_brace:
                break
            expressions.append(self.parse_style_instruction())
        if not self.tok.type == UISTT.right_brace:
            raise UIScriptError("Expected '}' at the end of the style body, got '" +
                                str(self.tok)+"' instead"+self.error_suffix())
        self.advance()
        return expressions

    def parse_style_properties_animations(self, expressions: list[tuple[str, str, typing.Any]]) -> tuple[dict[str, dict[str]], list]:
        properties, animations = {}, []
        for expr in expressions:
            if expr[0]:
                animations.append(expr[1:])
            else:
                if expr[1] not in properties:
                    properties[expr[1]] = {}
                properties[expr[1]][expr[2]] = expr[3]
        return properties, animations

    def make_style_holder(self, style_type: StyleType, style_target: StyleTarget, target_id: str, properties: dict[str, dict[str]], animations: list):
        self.style_holders.append(UIStyleHolder(
            properties, animations, style_type, style_target, target_id))

    def parse_style(self):
        target, target_ids = self.parse_style_target()
        main_type, copy_type, also_normal = self.parse_style_type()
        expressions = self.parse_style_body()
        properties, animations = self.parse_style_properties_animations(
            expressions)
        for target_id in target_ids:
            if not copy_type:
                self.make_style_holder(
                    main_type, target, target_id, properties, animations)
                if also_normal:
                    self.make_style_holder(
                        StyleType.normal, target, target_id, properties, animations)
            else:
                self.make_style_holder(
                    main_type, target, target_id, properties, animations)
                self.make_style_holder(
                    copy_type, target, target_id, properties, animations)
                if also_normal:
                    self.make_style_holder(
                        StyleType.normal, target, target_id, properties, animations)

    def parse(self) -> typing.Self:
        while self.tok and self.tok.type in [UISTT.dot, UISTT.hash, UISTT, UISTT.identifier]:
            self.parse_style()
        if self.tok and not self.tok.type == UISTT.eof:
            raise UIScriptError(
                f"Expected EOF after all the styles, got '{self.tok}' instead"+self.error_suffix())
        return self


class UIScript:
    """Manage style script execution by lexing and parsing"""
    @classmethod
    def parse_script(self, filename: str, variables: dict[str]):
        """Load styles and animations from a GSS file using the given variables"""
        if not os.path.exists(filename):
            raise UIScriptError(
                f"UI Script file '{filename}' doesn't exist. Is the file name/path correct?")
        source = ""
        with open(filename, "r") as file:
            source = file.read()
        lexer = UIScriptLexer(source, filename).lex()
        parser = UIScriptParser(lexer.tokens, filename, variables).parse()
        UIStyles.add_styles(*parser.style_holders)

    @classmethod
    def parse_source(self, source: str, filename: str, variables: dict[str]):
        """Load styles and animations from a GSS source using the given variables. The filename is needed for error messages"""
        lexer = UIScriptLexer(source, filename).lex()
        if len(lexer.tokens) > 0:
            parser = UIScriptParser(lexer.tokens, filename, variables).parse()
        UIStyles.add_styles(*parser.style_holders)
