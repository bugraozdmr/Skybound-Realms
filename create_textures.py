import pygame
import os

def create_texture(name, color, size=(256, 256)):
    # Create textures directory if it doesn't exist
    if not os.path.exists('textures'):
        os.makedirs('textures')
    
    # Create surface
    surface = pygame.Surface(size)
    surface.fill(color)
    
    # Add some pattern
    for i in range(0, size[0], 32):
        for j in range(0, size[1], 32):
            if (i + j) % 64 == 0:
                pygame.draw.rect(surface, (min(color[0] + 0.2, 1.0), 
                                        min(color[1] + 0.2, 1.0), 
                                        min(color[2] + 0.2, 1.0)), 
                               (i, j, 16, 16))
    
    # Save the texture
    pygame.image.save(surface, f'textures/{name}.png')
    print(f"Created texture: {name}.png")

def main():
    pygame.init()
    
    # Create basic textures
    create_texture('grass', (0.3, 0.8, 0.3))  # Green
    create_texture('rock', (0.5, 0.5, 0.5))   # Gray
    create_texture('ice', (0.8, 0.8, 1.0))    # Light blue
    
    pygame.quit()

if __name__ == "__main__":
    main() 