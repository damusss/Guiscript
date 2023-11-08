import pygame
import typing
if typing.TYPE_CHECKING:
    from .manager import UIManager
    
from .elements.element import UIElement
    
    
class UINavigation:
    def __init__(self, ui_manager: "UIManager"):
        self.ui_manager: "UIManager" = ui_manager
        
        self.enabled: bool = True
        self.tabbed_element: UIElement|None = None
        
    def enable(self) -> typing.Self:
        self.enabled = True
        return self 
    
    def disable(self) -> typing.Self:
        self.enabled = False
        return self
    
    def event(self, event: pygame.Event):
        if not event.type == pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.stop_navigating()
        elif event.key == pygame.K_TAB:
            if self.tabbed_element is None:
                self.tabbed_element = self.ui_manager.root.find_navigable_child()
            else:
                if event.mod == pygame.KMOD_LSHIFT:
                    self.tab(False)
                else:
                    self.tab(True)
        elif event.key == pygame.K_RETURN:
            self.tab_inside()
            
        elif event.key == pygame.K_UP:
            if self.tabbed_element is not None and self.tabbed_element.parent is not None and self.tabbed_element.parent.can_navigate():
                self.tabbed_element = self.tabbed_element.parent
                
    def tab_inside(self) -> typing.Self:
        if self.tabbed_element is not None:
            element = self.tabbed_element.find_navigable_child()
            if element is not None:
                self.tabbed_element = element
        return self
            
    def tab(self, forward: bool) -> typing.Self:
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
        self.tabbed_element = self.tabbed_element.parent.children[new_index]
        if not self.tabbed_element.can_navigate():
            if self.tabbed_element.parent.has_navigable_child():
                self.tab(forward)
            else:
                self.tabbed_element = old_tabbed
        return self
                
    def stop_navigating(self) -> typing.Self:
        self.tabbed_element = None
        return self
        
    def help(self) -> typing.LiteralString:
        return """
        Exit: ESC
        Start: TAB
        Next Element: TAB
        Previous Element: LSHIFT+TAB
        First Child: ENTER
        Parent: UP
        Interact: SPACE
        """    
    