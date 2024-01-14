# import guiscript (i don't suggest importing * but i suggest renaming)
import guiscript as guis
import pygame
import sys # i close python with this!

# Setup pygame. Either use the display module or the new Window API. The choice is yours!
pygame.init()
screen = pygame.display.set_mode((1200, 750))
# window = pygame.Window("Title", (1200, 750))
clock = pygame.Clock()

# Create a manager. Multiple ones are possible, but you should only have one manager getting updated/rendered at once. By default this will be the current one
manager = guis.Manager(screen)
# manager = guis.Manager(window.get_surface())

# Create some elements
with guis.column((1200, 750)):
    with guis.VStack(guis.SizeR(900, 700)):
        guis.Text("Example Text", guis.SizeR(300,50))
        guis.Button("A Button", guis.SizeR(200, 60), "my_button")

# Create the game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit() # close python how you prefer
        # elements post events
        elif event.type == guis.CLICK:
            if event.id == "my_button":
                print("Clicked!", event.element.get_text())
        manager.event(event)

    screen.fill("black")
    # window.get_surface().fill("black")

    manager.logic()
    guis.static_logic()
    manager.render()

    clock.tick(0)
    pygame.display.flip()
    # window.flip()
    