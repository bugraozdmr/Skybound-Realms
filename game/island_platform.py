import pygame

class Platform:
    def __init__(self, x, y, texture):
        self.image = pygame.image.load(f"assets/{texture}.png")
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)
