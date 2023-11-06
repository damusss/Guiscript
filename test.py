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

def on_select(button: guis.ImageButton):
    label.set_text(f"You selected button {int(button.element_id.replace('select_button_', ''))+1}")
    
surfaces = [test_surf, menu_surf, player_surf, test_surf]

with guis.VStack(rect(0, 0, 1200, 800), style_id="invis_cont"):
    with guis.VStack(rect(0,0,400,700), style_id="no_scroll"):
        with guis.HStack(rect(0,0,400-14,100), style_id="invis_cont;no_padding"):
            for i in range(4):
                guis.ImageButton(surfaces[i], rect(0,0,370//4,100), f"select_button_{i}").status.add_listener("on_click", on_select)
        label = guis.Label("Select something", rect(0,0,390,600))
    
    
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
