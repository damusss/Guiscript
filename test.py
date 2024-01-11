import pygame
import sys, os
import src.guiscript as guis
from pygame import Rect as rect

pygame.Rect()
W, H = 1200, 800
pygame.init()
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
clock = pygame.Clock()

test_surf = pygame.image.load("tests/test.jpg").convert()
menu_surf = pygame.transform.scale_by(pygame.image.load("tests/menu.png").convert_alpha(), 3)


manager = guis.Manager(screen, True, ["tests/example.gss"])

surfaces = [test_surf, menu_surf, test_surf]

def open_modal():
    modal.show()
    
def close_modal():
    modal.hide()

with guis.VStack(guis.SizeR(W, H), style_id="invis_cont") as MAIN:
    with guis.VStack(guis.SizeR(600,700), style_id="no_scroll").set_resizers(guis.ALL_RESIZERS):
        el = guis.Entry(guis.SizeR(500,80), '<c fg="green">ciao!!</c>', settings=guis.EntrySettings(inner_style_id="richtext")).set_resizers(guis.ALL_RESIZERS)
        guis.Image(None, guis.SizeR(200,200), style_id="imgtest")
        guis.Button(f"OPEN", guis.SizeR(200,60)).status.add_listener("on_click", open_modal)
        guis.DropMenu(["ciao", "ti", "amo", "tanto"], "comeva", guis.SizeR(150,30))
        with guis.HStack(guis.SizeR(400, 50)):
        #with guis.HStack(guis.SizeR(200,50), style_id="invisible"):
            c1 = guis.Checkbox(guis.SizeR(40,40))
            guis.Label("Check 1", guis.ZeroR(), style_id="fill")
        #with guis.HStack(guis.SizeR(200,50), style_id="invisible"):
            c2 = guis.Checkbox(guis.SizeR(40,40))
            guis.Label("Check 2", guis.ZeroR(), style_id="fill") 
        guis.bind_one_selected_only((c1, c2), True)
        
with (modal_element:=guis.Window(guis.SizeR(300,300), "Modal Thing",
                                 settings=guis.WindowSettings(have_close_button=False))).status.set_drag(False).element.set_ignore(False, False).enter():
    guis.Button(f"HIDE", guis.SizeR(200,60)).status.add_listener("on_click", close_modal)
    
modal = guis.ModalContainer(modal_element)
          
while True:   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.VIDEORESIZE:
            W, H = event.w, event.h
            screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
            manager.set_screen_surface(screen)
            MAIN.set_size((W, H))
            
        manager.event(event)
        
    screen.fill("black")

    manager.logic()
    guis.static_logic(1)
    manager.render()


    clock.tick_busy_loop(0)
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")
