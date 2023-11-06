import pygame
pygame.init()

#variables for background
BACKGROUND = (127, 0, 255)
WIN_WIDTH, WIN_HEIGHT = 1000, 800 
FPS = 60
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("PROTOTYPE BY MY GLORIOUS KING KAMIL")
clock = pygame.time.Clock()

#variables for platform
PLATFORM_COLOR = (92, 64, 51)
LEFT_PLATFORM = 0
TOP_PLATFORM = WIN_HEIGHT - 25
WIDTH_PLATFORM = int(WIN_WIDTH)
HEIGHT_PLATFORM = 50
platform = pygame.Rect(LEFT_PLATFORM, TOP_PLATFORM, WIDTH_PLATFORM, HEIGHT_PLATFORM)

#variables for character

#width and height for character
KAMIL_WIDTH, KAMIL_HEIGHT = 160, 290
#load kamil png
player_image = pygame.image.load("player.png").convert_alpha()
#scales image
player_scale = pygame.transform.scale(player_image, (KAMIL_WIDTH, KAMIL_HEIGHT))
#coordinates
KAMIL_RECT = player_scale.get_rect(bottomleft=(0, TOP_PLATFORM))
#speed
KAMIL_SPEED = 29

#game loop

keepWorkingSlave = True

while keepWorkingSlave:
    dt = clock.tick(FPS) / 1000
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            keepWorkingSlave = False
    
    keys = pygame.key.get_pressed() # moving kamil with WASD
    if keys[pygame.K_w]:
        KAMIL_RECT.y -= KAMIL_SPEED
    if keys[pygame.K_s]:
        KAMIL_RECT.y  += KAMIL_SPEED
    if keys[pygame.K_a]:
        KAMIL_RECT.x -= KAMIL_SPEED
    if keys[pygame.K_d]:
        KAMIL_RECT.x += KAMIL_SPEED
    if keys[pygame.K_UP]:
        KAMIL_RECT.y-= KAMIL_SPEED
    if keys[pygame.K_DOWN]:
        KAMIL_RECT.y  += KAMIL_SPEED
    if keys[pygame.K_LEFT]:
        KAMIL_RECT.x -= KAMIL_SPEED
    if keys[pygame.K_RIGHT]:
        KAMIL_RECT.x += KAMIL_SPEED

#character dont leave the window
    if KAMIL_RECT.x  < 0:
        KAMIL_RECT.x  = 0

    if KAMIL_RECT.x  > WIN_WIDTH - KAMIL_WIDTH:
        KAMIL_RECT.x  = WIN_WIDTH - KAMIL_WIDTH

    if KAMIL_RECT.bottom> TOP_PLATFORM:
        KAMIL_RECT.bottom = TOP_PLATFORM

    if KAMIL_RECT.y < 0:
        KAMIL_RECT.y = 0

#refreshes character/platform and background
        
    screen.fill((BACKGROUND))  # colored background
    pygame.draw.rect(screen, PLATFORM_COLOR, platform) #draws platform
    screen.blit(player_scale, KAMIL_RECT) #scale n coordinates
    pygame.draw.rect(screen, "red", KAMIL_RECT, 5)
    pygame.display.flip() #refreshes

#leaves game once keepWorkingSlave is false
pygame.quit()