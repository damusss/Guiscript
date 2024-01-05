import pygame
import sys, os
import src.guiscript as guis
from pygame import Rect as rect

W, H = 1200, 800
pygame.init()
win = pygame.Window("Dockspace Test", (W, H))
clock = pygame.Clock()

manager = guis.Manager(win.get_surface(), True, ["tests/example.gss"], None)

class MyTestDockspace:
    def __init__(self):
        ...

ds = MyTestDockspace()

with guis.Window(pygame.Rect(100,50,800,700), "MNG1", settings=guis.WindowSettings(have_close_button=True, 
                                                                                title_bar_height=30, 
                                                                                have_collapse_button=True)).enter():
    guis.Button("TEST", pygame.Rect(0,0,100,100))\
        .set_anchor("parent", guis.Anchor.bottom, guis.Anchor.centery)\
        .set_anchor("parent", guis.Anchor.top, guis.Anchor.top)\
        .set_anchor("parent", guis.Anchor.right, guis.Anchor.right)\
        .set_anchor("parent", guis.Anchor.left, guis.Anchor.centerx)\

while True:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        manager.event(event)

    win.get_surface().fill("black")
        
    manager.logic()
    guis.static_logic(1)
    manager.render()
    
    clock.tick_busy_loop(0)
    #pygame.display.flip()
    #pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")
    win.flip()
    win.title = f"{clock.get_fps():.0f} FPS"