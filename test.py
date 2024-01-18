import pygame, pathlib
import sys, os
import guiscript as guis
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
    
def starthover(opt: guis.Element):
    opt.remove_animations()
    opt.animate_h_to(60, 150)
    
def stophover(opt: guis.Element):
    opt.remove_animations()
    opt.animate_h_to(30, 150)
    
class FD:
    fd: guis.FileDialog = None

options = []

def openfd():
    if FD.fd is not None:
        return
    def onclose():
        FD.fd = None
    FD.fd = guis.FileDialog(os.getcwd(), pygame.Rect(50,50,700,500), settings=guis.FileDialogSettings(
            selectionlist_settings=guis.SelectionListSettings(multi_select=True),            
        ))
    FD.fd.status.add_listener("on_close", onclose).element
    FD.fd.title.set_tooltip("YO HI BROTHA", height=40)

with guis.column((W, H), False) as MAIN:
    with guis.VStack(guis.SizeR(600,700), style_id="no_scroll").set_resizers(guis.ALL_RESIZERS):
        guis.Button("Open Filedialog", guis.SizeR(200,50)).status.add_listener("on_click", openfd).element.set_tooltip("Open Filedialog", "Open the silly file dialogue with coolie animations uwu")
        guis.ColorPicker(guis.SizeR(300,300), pygame.Color(255,0,255)).set_resizers(guis.ALL_RESIZERS)
        
modal_element:guis.Window=guis.Window(guis.SizeR(300,300), "Modal Thing",
                                 settings=guis.WindowSettings(have_close_button=False)).status.set_drag(False).element.set_ignore(False, False)
with modal_element.enter():
    guis.Button(f"HIDE", guis.SizeR(200,60)).status.add_listener("on_click", close_modal)
    
modal = guis.Modal(modal_element)
          
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
        elif event.type == guis.FILEDIALOG_OK:
            print(event.selected, event.path)
            
        manager.event(event)
        
    screen.fill("black")
    
    if FD.fd is not None:
        if options != FD.fd.selectionlist.option_buttons:
            for opt in FD.fd.selectionlist.option_buttons:
                opt.status.add_multi_listeners(on_start_hover=starthover, on_stop_hover=stophover)
            options = FD.fd.selectionlist.option_buttons

    manager.logic()
    guis.static_logic(1)
    manager.render()

    clock.tick_busy_loop(0)
    pygame.display.flip()
    pygame.display.set_caption(f"{clock.get_fps():.0f} FPS")
