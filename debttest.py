import pygame
import sys
import src.guiscript as guis
from pygame import Rect as rect

W, H = 1200, 800
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.Clock()

GSS = """
#title:: {
    text.font_size 40;
}

.anchor_top:: {
    stack.anchor top;
}
"""

manager = guis.UIManager(screen, gs_sources=[GSS])

with guis.VStack(guis.SizeR(W, H), style_id="anchor_top"):
    title = guis.Label("Family Debt Registry", guis.SizeR(W//2, 80), "title").text.disable_selection().element

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

    clock.tick_busy_loop(0)
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")