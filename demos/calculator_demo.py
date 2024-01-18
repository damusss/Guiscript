import pygame
import sys
import math
import decimal
import guiscript as guis

GSS = """
.alignleft:: {
    stack.align left;
    text.align left;
    text.font_align left;
}

.anchortop:: {
    stack.anchor top;
}

.btnscol:: {
    stack.padding 0;
    stack.spacing 2;
}

.main:: {
    stack.padding 4;
}
"""

TXTH = 50
BTNH = 40
VARNAMEW = 85
GLOBALS = math.__dict__.copy()
MATHATTRS = {k: v for k, v in GLOBALS.items() if not k.startswith("__")}
GLOBALS.update({
    "__import__": None,
    "exec": None,
    "eval": None,
    "compile": None,
    "open": None,
    "print": None,
    "decimal": decimal.Decimal,
    "d": decimal.Decimal,
    "c": complex,
    "i": complex(0, 1),
    "__name__": "calculator"
})


class Calculator:
    def __init__(self):
        self.sizes = self.w, self.h = 300, 400
        pygame.init()
        self.win = pygame.Window(
            "Calculator Demo", self.sizes, pygame.WINDOWPOS_CENTERED, resizable=True)
        self.win.minimum_size = (210, 325)
        self.screen = self.win.get_surface()
        self.clock = pygame.Clock()

        self.manager = guis.Manager(self.screen, True, gss_sources=[GSS])
        self.vars = {}
        self.vars_elements = []
        self.prev_expr = None
        self.build()

    def build(self):
        with guis.VStack(guis.SizeR(self.w, self.h), style_id="no_scroll;main") as self.main_cont:
            self.build_display()
            self.build_buttons()
            self.math_sl = guis.SelectionList(["<-"]+list(MATHATTRS.keys()), guis.SizeR(0, 0))\
                .set_anchors(("parent", "left", "left"), ("parent", "right", "right"), ("parent", "bottom", "bottom"),
                             (self.display_cont, "top", "bottom"))\
                .hide().anchors_padding(4, "top")
            self.math_sl.status.add_listener(
                "on_option_select", self.math_sl_select)
            self.build_vars()

    def build_vars(self):
        with guis.VStack(guis.ZeroR(), style_id="anchortop")\
            .set_anchors(("parent", "left", "left"), ("parent", "right", "right"), ("parent", "bottom", "bottom"),
                         (self.display_cont, "top", "bottom"))\
                .hide().anchors_padding(4, "top") as self.vars_cont:
            with guis.row((0, BTNH), True) as self.vars_bottom_row:
                self.vars_plus = guis.Button("add", guis.ZeroR(), style_id="fill;icons_font")\
                    .status.add_listener("on_click", self.vars_plus_click).element
                self.vars_showhide = guis.Button("visibility", guis.ZeroR(), style_id="fill;icons_font")\
                    .status.add_listener("on_click", self.vars_showhide_click).element
                self.vars_close = guis.Button("arrow_back", guis.ZeroR(), style_id="fill;icons_font")\
                    .status.add_listener("on_click", self.vars_close_click).element

    def build_display(self):
        with guis.column((0, TXTH+TXTH*1.2), False, "fill_x;no_scroll") as self.display_cont:
            self.expr_entry = guis.Entry(guis.SizeR(
                0, TXTH), "0", style_id="fill_x", settings=guis.EntrySettings("Enter expression"))
            self.result_text = guis.Text("0", guis.SizeR(
                0, TXTH*1.2), style_id="fill_x;alignleft")

    def build_buttons(self):
        with guis.column((0, 0), False, "fill_x;fill_y;btnscol") as self.main_buttons_cont:
            for row in [
                ["delete", "backspace", "chevron_left", "chevron_right"],
                ["( [", ") ]", "^", "/"],
                ["1", "2", "3", "close"],
                ["4", "5", "6", "add"],
                ["7", "8", "9", "remove"],
                ["0", ".", "Math", "Vars"]
            ]:
                with guis.row((0, BTNH), True, extra_style_id="fill_y;btnscol"):
                    for btntxt in row:
                        if btntxt in ["chevron_right", "chevron_left", "backspace", "delete", "close", "add", "remove"]:
                            sid = "fill;icons_font"
                        else:
                            sid = "fill"
                        guis.Button(btntxt, guis.SizeR(0, 0), style_id=sid).status.add_multi_listeners(
                            on_click=self.btn_click, on_right_click=self.btn_right_click)

    def vars_plus_click(self):
        with self.vars_cont:
            with guis.column((0, 0), False, "fill_x;resize_y;no_scroll") as col:
                with guis.row((0, BTNH), True, "no_scroll") as row:
                    ne = guis.Entry(guis.SizeR(VARNAMEW, 0), "var", style_id="fill_y", settings=guis.EntrySettings("Var name"))\
                        .status.add_listener("on_change", self.vars_entry_change).element
                    ve = guis.Entry(guis.SizeR(0, 0), "0", style_id="fill", settings=guis.EntrySettings("Var value"))\
                        .status.add_listener("on_change", self.vars_entry_change).element
                    delb = guis.Button("delete", guis.SizeR(BTNH, BTNH), style_id="icons_font")\
                        .set_attr("rowid", col.object_id)\
                        .status.add_listener("on_click", self.vars_del_click).element
                pr = guis.Text("0", guis.SizeR(0, BTNH),
                               style_id="fill_x;alignleft")
                if self.vars_showhide.get_text() == "visibility":
                    pr.hide()
                self.vars_elements.append((col, ne, ve, delb, pr))
        self.vars_bottom_row.move_in_parent(1)
        self.parse_vars()

    def vars_showhide_click(self):
        if self.vars_showhide.get_text() == "visibility":
            self.vars_showhide.set_text("visibility_off")
        else:
            self.vars_showhide.set_text("visibility")
        for row, ne, ve, delb, pr in self.vars_elements:
            pr.show() if not pr.status.visible else pr.hide()

    def vars_close_click(self):
        self.vars_cont.hide()

    def vars_entry_change(self, *args):
        self.parse_vars()

    def vars_del_click(self, b):
        for t in list(self.vars_elements):
            row, ne, ve, delb, pr = t
            if row.object_id == b.get_attr("rowid"):
                self.vars_elements.remove(t)
                row.destroy()
                break
        self.parse_vars()

    def btn_click(self, btn):
        txt = btn.get_text().lower()
        if txt == "backspace":
            self.expr_entry.delete_at_cursor()
        elif txt == "chevron_left":
            self.expr_entry.move_cursor(-1)
        elif txt == "chevron_right":
            self.expr_entry.move_cursor(1)
        elif txt == "delete":
            self.expr_entry.set_text("")
        elif txt == "math":
            self.math_sl.show()
        elif txt == "vars":
            self.vars_cont.show()
        else:
            if txt == "^":
                txt = "**"
            if txt == "close":
                txt = "*"
            if txt == "add":
                txt = "+"
            if txt == "remove":
                txt = "-"
            if " " in txt:
                txt = txt[0]
            self.expr_entry.add_text(txt)
        self.expr_entry.focus()

    def btn_right_click(self, btn):
        txt = btn.get_text().lower()
        if " " in txt:
            txt = txt[-1]
        self.expr_entry.add_text(txt)
        self.expr_entry.focus()

    def math_sl_select(self, sl, option):
        self.math_sl.set_selected(None)
        self.math_sl.set_scroll(0, 0)
        self.math_sl.hide()
        if option.lower() == "<-":
            return
        self.expr_entry.add_text(option)

    def parse_vars(self):
        self.vars = {}
        for row, ne, ve, delb, pr in self.vars_elements:
            name: str = ne.get_text().strip()
            val: str = ve.get_text().strip()
            if not name or not val:
                pr.set_text("empty name or value")
                continue
            if not name.isidentifier():
                pr.set_text("invalid name")
                continue
            try:
                res = eval(val, GLOBALS, self.vars)
                self.vars[name] = res
                pr.set_text(res)
            except Exception as e:
                pr.set_text(f"{str(e).replace("(<string>, line 1)", "").replace(
                    "(<string>, line 0)", "")}")
        self.prev_expr = None

    def update(self):
        if self.math_sl.status.visible:
            self.result_text.set_text("select an element")
            return
        try:
            txt = self.expr_entry.get_text().strip()
            if txt == self.prev_expr:
                return
            if not txt:
                txt = "float('nan')"
            res = eval(txt, GLOBALS, self.vars)
            self.result_text.set_text(res)
            self.prev_expr = txt
        except Exception as e:
            self.result_text.set_text(
                f"{str(e).replace("(<string>, line 1)", "").replace("(<string>, line 0)", "")}")
            self.prev_expr = None

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    self.sizes = self.w, self.h = event.w, event.h
                    self.manager.set_screen_surface(self.screen)
                    self.main_cont.set_size((self.w, self.h))
                self.manager.event(event)

            self.screen.fill(0)
            self.manager.logic()
            guis.static_logic()
            self.update()
            self.manager.render()
            self.win.flip()
            self.clock.tick(0)


if __name__ == "__main__":
    Calculator().run()
