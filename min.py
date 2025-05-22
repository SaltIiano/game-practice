import pygame
import sys

pygame.init()

screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Minimal Pygame Example")

red = (255, 0, 0)  # RGB color for red

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))  # Fill the screen with black

    # Draw a red square
    pygame.draw.rect(screen, red, (50, 50, 100, 100)) # (screen, color, (x, y, width, height))

    pygame.display.flip()

pygame.quit()
sys.exit()
