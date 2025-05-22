import pygame
from pygame.sprite import Sprite

class Boss(Sprite):
    def __init__(self, ai_game):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.image = pygame.image.load('assets/boss.bmp')
        self.image = pygame.transform.scale(self.image, (self.settings.alien_width * 3, self.settings.alien_height * 3))
        self.rect = self.image.get_rect()

        self.rect.x = self.rect.width
        self.rect.y = self.rect.height

        self.health = 10
        self.direction = 1

    def update(self):
        self.rect.x += self.settings.boss_speed * self.direction

        if self.rect.right >= self.screen.get_rect().right or self.rect.left <= 0:
            self.direction *= -1
            self.rect.y += self.settings.fleet_drop_speed

        if self.rect.bottom >= self.screen.get_rect().bottom:
            self.rect.y = self.rect.height

    def draw(self):
        self.screen.blit(self.image, self.rect)

