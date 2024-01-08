import pygame
import sys, os
import src.guiscript as guis
from pygame import Rect as rect
pygame.Rect()
W, H = 1200, 800
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.Clock()

test_surf = pygame.image.load("tests/test.jpg").convert()
menu_surf = pygame.transform.scale_by(pygame.image.load("tests/menu.png").convert_alpha(), 3)

manager = guis.Manager(screen, True, ["tests/example.gss"], None, {
    "MENU": menu_surf,
    "MENU_HOVER": menu_surf,
    "MENU_PRESS": menu_surf,
    
})    

surfaces = [test_surf, menu_surf, test_surf]

v = 0
with guis.VStack(guis.SizeR(1200, 800), style_id="invis_cont"):
    with guis.VStack(guis.SizeR(600,700), style_id="no_scroll").set_resizers(guis.ALL_RESIZERS):
        el = guis.Entry(guis.SizeR(500,80), '<c fg="green">ciao!!</c>', settings=guis.EntrySettings(inner_style_id="richtext")).set_resizers(guis.ALL_RESIZERS)
        pb = guis.ProgressBar(0, rect(50,50,500,100), settings=guis.ProgressBarSettings(direction=guis.ProgressBarDirection.left_right))
        lb = guis.Label("""<c fg="red">ciao
come va</c>""", guis.SizeR(100,100), style_id="richtext")
        nlb = guis.Label("", guis.SizeR(300,100), style_id="changing").activate()
                
while True:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        manager.event(event)

    screen.fill("black")
    
    manager.logic()
    guis.static_logic(1)
    manager.render()
    
    v += 0.05
    pb.set_value(v)

    clock.tick_busy_loop(0)
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")
