import pygame

class Coin:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/coin.png")
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
