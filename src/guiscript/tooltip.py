import pygame
import typing
if typing.TYPE_CHECKING:
    from .elements.element import UIElement

from .state import UIState


class UITooltips:
    """Tooltip Manager. Updated by static_logic, automatically set up by UIElement.set_tooltip"""
    hover_time: float = 1200
    tooltips: list[dict[str]] = []
    active_tooltip: "UIElement" = None

    @classmethod
    def set_hover_time(cls, hover_time_ms: float) -> typing.Self:
        """Set how much time in ms must pass after tooltips appear while the mouse is still"""
        cls.hover_time = hover_time_ms
        return cls

    @classmethod
    def register(cls, tooltip: "UIElement", element: "UIElement") -> typing.Self:
        """Register a tooltip and an element for the tooltip to appear on prolungated hover. Automated by UIElement.set_tooltip"""
        already = False
        for tt_data in list(cls.tooltips):
            if tt_data["el"] is element:
                cls.tooltips.remove(tt_data)
                already = True
        if not already:
            element.status.add_listener("on_start_hover", cls.on_start_hover)
            element.status.add_listener("on_stop_hover", cls.on_stop_hover)
            cls.tooltips.append(
                {
                    "tt": tooltip,
                    "el": element,
                    "start_hover_time": 0
                }
            )
        return cls

    @classmethod
    def on_start_hover(cls, element):
        """[Internal] Callback given to registered elements"""
        if cls.active_tooltip is not None:
            cls.active_tooltip.hide()
        cls.active_tooltip = None
        for tt_data in cls.tooltips:
            if tt_data["el"] is element:
                tt_data["start_hover_time"] = pygame.time.get_ticks()
                cls.active_tooltip = tt_data["tt"]

    @classmethod
    def on_stop_hover(cls):
        """[Internal] Callback given to registered elements"""
        if cls.active_tooltip is not None:
            cls.active_tooltip.hide()
        cls.active_tooltip = None

    @classmethod
    def logic(cls):
        """[Internal] Update tooltips (called by static_logic)"""
        if cls.active_tooltip is not None:
            tt_data: dict[str] = None
            for tt_data_i in cls.tooltips:
                if tt_data_i["tt"] is cls.active_tooltip:
                    tt_data = tt_data_i
                    break
            if tt_data is None:
                return
            if not cls.active_tooltip.visible:
                if UIState.mouse_rel.length() != 0:
                    tt_data["start_hover_time"] = pygame.time.get_ticks()
                if pygame.time.get_ticks()-tt_data["start_hover_time"] >= cls.hover_time:
                    cls.active_tooltip.show()
            tt: "UIElement" = tt_data["tt"]
            px, py = UIState.mouse_pos.x, UIState.mouse_pos.y+10
            win_size = pygame.display.get_window_size()
            if px+tt.relative_rect.w > win_size[0]:
                px = win_size[0]-tt.relative_rect.w
            if py+tt.relative_rect.h > win_size[1]:
                py = UIState.mouse_pos.y-10-tt.relative_rect.h
            tt.set_absolute_pos((px, py))
