import pygame

screen_w = 640
screen_h = 480

def Health_display(attr, screen):
    font = pygame.font.Font("data/Pixeltype.ttf", 35)
    text = "Health: " + str(attr)
    display = font.render(text, True, "mediumspringgreen")
    rect = display.get_rect(topleft = (4, 6))
    img = pygame.Surface((rect.width + 4, rect.height + 4))
    img.set_alpha(150)
    img.fill("black")
    screen.blit(img, (rect.x - 2, rect.y -4))
    screen.blit(display, rect)
