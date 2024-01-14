import pygame
import sys, os
import guiscript as guis
from pygame import Rect as rect

W, H = 1200, 800
pygame.init()
win = pygame.Window("Dockspace Test", (W, H))
clock = pygame.Clock()

manager = guis.Manager(win.get_surface(), True, ["tests/example.gss"], None)
rects = []

root = guis.Element(guis.SizeR(W, H)).deactivate().set_style_id("inactive")

dock_win = [
    (1, "topleft"),
    (2, "topright"),
    (3, "bottomleft"),
    (4, "bottom"),
    (5, "bottomright"),
    (6, "bottomtop")
]

win_win = [
    (1, "x>", 6),
    (6, "<x", 2),
    (1, "<y>", 3),
    (3, "<x>", 4),
    (4, "x>", 6),
    (6, "<x", 5),
    (2, "<y>", 5),
    (1, "<y", 4)
]

with (w1:=guis.Window(pygame.Rect(0,0,200,200), "1", 
                settings=guis.WindowSettings(
                have_collapse_button=True, resizers=("bottom",)
    ))).enter():
    guis.ProgressBar(50, rect(50,50,500,100), settings=guis.ProgressBarSettings(direction=guis.ProgressBarDirection.left_right))
    
with (w2:=guis.Window(pygame.Rect(0,0,200,200), "2", settings=guis.WindowSettings(have_collapse_button=True, resizers=("bottom",)))).enter():
    ...
    
with (w3:=guis.Window(pygame.Rect(0,0,200,200), "3", settings=guis.WindowSettings(have_collapse_button=True, resizers=("top", "right")))).enter():
    ...
    
with (w4:=guis.Window(pygame.Rect(500,0,200,200), "4", settings=guis.WindowSettings(have_collapse_button=True, resizers=("left",)))).enter():
    ...
    
with (w5:=guis.Window(pygame.Rect(0,0,200,200), "5", settings=guis.WindowSettings(have_collapse_button=True, resizers=("top",)))).enter():
    ...
    
w6 = guis.Element(pygame.Rect(800,0,10,100)).status.set_drag(True).element
    
wins = [
    (1, w1),
    (2, w2),
    (3, w3),
    (4, w4),
    (5, w5),
    (6, w6)
]

guis.static_dock(root, wins, dock_win, win_win)
    

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
    #for r, n in rects:
    #    pygame.draw.rect(win.get_surface(), "green", r)
    
    clock.tick_busy_loop(0)
    #pygame.display.flip()
    #pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")
    win.flip()
    win.title = f"{clock.get_fps():.0f} FPS"