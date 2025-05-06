import pygame

# fix

class Player:
    def __init__(self, x, y):
        self.image = pygame.image.load("assets/avatar.png")
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.jump_power = -12
        self.gravity = 0.6
        self.on_ground = False

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power

        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect) and self.vel_y > 0:
                self.rect.bottom = plat.rect.top
                self.vel_y = 0
                self.on_ground = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)
