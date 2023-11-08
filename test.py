import pygame
import sys
import src.guiscript as guis
from pygame import Rect as rect


W, H = 1200, 800
pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.Clock()

test_surf = pygame.image.load("test.jpg").convert()
menu_surf = pygame.transform.scale_by(pygame.image.load("menu.png").convert_alpha(), 3)
player_surf = pygame.transform.scale_by(pygame.image.load("player.png").convert_alpha(), 4)

manager = guis.UIManager(screen, True, ["example.gss"], {
    "MENU": menu_surf,
    "MENU_HOVER": menu_surf,
    "MENU_PRESS": menu_surf,
})

def on_select(slides: guis.Slideshow, direction):
    label.set_text(f"You selected button {slides.surface_index+1}")

surfaces = [test_surf, menu_surf, player_surf, test_surf]

with guis.VStack(guis.SizeR(1200, 800), style_id="invis_cont"):
    with guis.VStack(guis.SizeR(600,700), style_id="no_scroll"):
        guis.Slideshow([test_surf,menu_surf,player_surf,test_surf], rect(0,0,0,200), style_id="fill_x").status.add_listener("on_move", on_select)
        #with guis.HStack(guis.SizeR(0,100), style_id="invis_cont;fill_x") as lol:
        #    for i in range(4):
        #        guis.ImageButton(surfaces[i], guis.ZeroR(), f"select_button_{i}", "fill").status.add_listener("on_click", on_select)
        label = guis.Label("AB AB AB ABA BA BA dsag dhgdas gdas gjhdjhas jhgdjasg jasdghj gjdhsag jdhas BABABBABAB\nABABA ABABAMAS\nMASNDSA VB Adsa\nBA BABABA B AAB Select something", guis.ZeroR(), style_id="fill")
        
while True:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        manager.event(event)

    screen.fill("black")
    
    manager.logic(1)
    manager.render()

    clock.tick_busy_loop(0)
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")
