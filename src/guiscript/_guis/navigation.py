import pygame
import typing
if typing.TYPE_CHECKING:
    from .manager import Manager
from .elements.element import Element


class UINavigation:
    """Keyboard navigation manager bound to a Manager"""

    def __init__(self, manager: "Manager"):
        self.manager: "Manager" = manager

        self.enabled: bool = True
        self.tabbed_element: Element | None = None

    def enable(self) -> typing.Self:
        """Enable keyboard navigation"""
        self.enabled = True
        return self

    def disable(self) -> typing.Self:
        """Disable keyboard navigation"""
        self.enabled = False
        return self

    def _event(self, event: pygame.Event):
        if not event.type == pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.stop_navigating()

        elif event.key == pygame.K_TAB:
            if self.tabbed_element is None:
                self.tabbed_element = self.manager.root.find_navigable_child()
                self.tabbed_element.set_dirty()
            else:
                if event.mod == pygame.KMOD_LSHIFT:
                    self.tab(False)
                else:
                    self.tab(True)

        elif event.key == pygame.K_RETURN:
            self.tab_inside()

        elif event.key == pygame.K_UP:
            self.tab_outside()

    def tab_inside(self) -> typing.Self:
        """Navigate the first child of the current tabbed element"""
        if self.tabbed_element is not None:
            element = self.tabbed_element.find_navigable_child()
            if element is not None:
                if self.tabbed_element is not None:
                    self.tabbed_element.set_dirty()
                self.tabbed_element = element
                self.tabbed_element.set_dirty()
        return self

    def tab_outside(self) -> typing.Self:
        """Navigate the parent of the current tabbed element"""
        if self.tabbed_element is not None and self.tabbed_element.parent is not None and self.tabbed_element.parent.can_navigate():
            self.tabbed_element.set_dirty()
            self.tabbed_element = self.tabbed_element.parent
            self.tabbed_element.set_dirty()
        return self

    def tab(self, forward: bool) -> typing.Self:
        """Move backwards or forward on the tabbed element's parent, or tab inside if it's the only element"""
        if self.tabbed_element is None or self.tabbed_element.parent is None:
            return
        if self.tabbed_element.parent.navigable_children_count() <= 1:
            self.tab_inside()
            return
        old_tabbed = self.tabbed_element
        index = self.tabbed_element.parent.children.index(self.tabbed_element)
        new_index = index+1 if forward else index-1
        if new_index <= 0:
            new_index = len(self.tabbed_element.parent.children)-1
        if new_index >= len(self.tabbed_element.parent.children):
            new_index = 0
        self.tabbed_element.set_dirty()
        self.tabbed_element = self.tabbed_element.parent.children[new_index]
        self.tabbed_element.set_dirty()
        if not self.tabbed_element.can_navigate():
            if self.tabbed_element.parent.has_navigable_child():
                self.tab(forward)
            else:
                self.tabbed_element = old_tabbed
                self.tabbed_element.set_dirty()
        return self

    def start_navigating(self) -> typing.Self:
        """Manually start navigating"""
        self.tabbed_element = self.manager.root.find_navigable_child()
        self.tabbed_element.set_dirty()
        return self

    def stop_navigating(self) -> typing.Self:
        """Manually stop navigating"""
        if self.tabbed_element is not None:
            self.tabbed_element.set_dirty()
        self.tabbed_element = None
        return self
