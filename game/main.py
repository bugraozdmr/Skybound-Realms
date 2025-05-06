import pygame
from player import Player
from island_platform import Platform
from coin import Coin
from portal import Portal

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

player = Player(100, 300)
platforms = [Platform(100, 400, "ice"), Platform(300, 350, "island_platform")]
coins = [Coin(310, 320)]
portal = Portal(700, 330)

score = 0
running = True

while running:
    screen.fill((135, 206, 235))  # Sky blue background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    # Update
    player.update(platforms)
    if player.rect.top > HEIGHT:
        print("Game Over!")
        running = False

    for coin in coins[:]:
        if player.rect.colliderect(coin.rect):
            coins.remove(coin)
            score += 10
            print("Score:", score)

    if player.rect.colliderect(portal.rect):
        print("Next scene!")
        # sahne geçişi yapılır (fade, yeni platformlar vs.)

    # Draw
    for plat in platforms:
        plat.draw(screen)
    for coin in coins:
        coin.draw(screen)
    portal.draw(screen)
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
