import pygame
import sys, os
import src.guiscript as guis
from pygame import Rect as rect
import random

W, H = 1200, 800
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.Clock()


manager = guis.Manager(screen, True, ["tests/example.gss"])    

with guis.VStack(guis.SizeR(1200, 800), style_id="invis_cont"):
    l = guis.Label("MA TIPO\nSTI GRAN CAZZI", guis.SizeR(900,600), style_id=guis.quick_style(".ID {text.rich true; text.font_size 100;}"))

last = pygame.time.get_ticks()
rndcol = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
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
    
    if pygame.time.get_ticks() - last >= 100:
        last = pygame.time.get_ticks()
        rndcol = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        l.style.text.color = rndcol
        l.text._build(l.style)
    #l.set_text(f'<c fg="{rndcol}"> MA TIPO\nSTI GRAN CAZZI</c>')

    clock.tick_busy_loop(0)
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")