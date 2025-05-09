import pygame
from OpenGL.raw.GLUT import glutBitmapCharacter
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import random
import math

# Texture loading function
def load_texture(filename):
    try:
        texture_surface = pygame.image.load(filename)
        texture_data = pygame.image.tostring(texture_surface, 'RGBA', 1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()
        
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        
        # Set texture parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        return texture_id
    except Exception as e:
        print(f"Error loading texture {filename}: {e}")
        return None

# Game variables
player_pos = [0, 2, 0]  # x, y, z
player_vel = [0, 0, 0]  # x, y, z
gravity = -0.008  # Reduced gravity for slower falling
jump_strength = 0.35  # Increased jump strength for higher jumps
on_ground = False
score = 0
level = 1  # Added level counter
auto_move_speed = 0.05  # Reduced forward movement speed for more time on islands
side_move_speed = 0.15  # Reduced side movement speed
portal_active = False  # Track if portal is active
portal_pos = [0, 0, 0]  # Portal position
portal_rotation = 0  # Portal rotation angle
portal_scale = 1.0  # Portal scale for animation
in_portal = False  # Track if player is in portal
portal_animation_time = 0  # Track portal animation time
islands_in_level = 0  # Track number of islands in current level
transition_effect = False  # Track if level transition effect is active
transition_alpha = 0.0  # Alpha value for transition effect

# Island types and their properties
ISLAND_TYPES = {
    'grass': {'color': (0.3, 0.8, 0.3), 'texture': 'grass.png'},
    'rock': {'color': (0.5, 0.5, 0.5), 'texture': 'rock.png'},
    'ice': {'color': (0.8, 0.8, 1.0), 'texture': 'ice.png'}
}

# Island generation
island_width = 5  # Adjusted island width
min_gap = 2  # Further reduced minimum gap between islands
max_gap = 3  # Further reduced maximum gap between islands
islands = []
coins = []
textures = {}
clouds = []  # List to store cloud positions

def generate_clouds():
    global clouds
    clouds = []
    for _ in range(20):  # Generate 20 clouds
        x = random.uniform(-50, 50)
        y = random.uniform(5, 15)
        z = random.uniform(-20, 20)
        size = random.uniform(2, 4)
        clouds.append({'pos': [x, y, z], 'size': size})

def draw_cloud(x, y, z, size):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor4f(1.0, 1.0, 1.0, 0.8)  # White with some transparency
    
    # Draw multiple spheres to create a cloud shape
    for dx in [-0.3, 0, 0.3]:
        for dy in [-0.2, 0, 0.2]:
            for dz in [-0.3, 0, 0.3]:
                glPushMatrix()
                glTranslatef(dx * size, dy * size, dz * size)
                sphere = gluNewQuadric()
                gluSphere(sphere, size * 0.3, 8, 8)
                gluDeleteQuadric(sphere)
                glPopMatrix()
    
    glPopMatrix()

def draw_island(x, y, z, width, color, texture_id=None):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    if texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glColor3f(*color)
    
    # Draw the main island body
    vertices = [
        # Top surface (slightly elevated)
        [-width/2, 0.2, -width/2],  # 0
        [ width/2, 0.2, -width/2],  # 1
        [ width/2, 0.2,  width/2],  # 2
        [-width/2, 0.2,  width/2],  # 3
        
        # Bottom surface
        [-width/2, -0.5, -width/2],  # 4
        [ width/2, -0.5, -width/2],  # 5
        [ width/2, -0.5,  width/2],  # 6
        [-width/2, -0.5,  width/2],  # 7
    ]
    
    # Define faces for the island
    faces = [
        [0, 1, 2, 3],  # Top
        [4, 5, 6, 7],  # Bottom
        [0, 4, 7, 3],  # Left
        [1, 5, 6, 2],  # Right
        [0, 1, 5, 4],  # Front
        [3, 2, 6, 7]   # Back
    ]
    
    # Define texture coordinates for each face
    tex_coords = [
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Top
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Bottom
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Left
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Right
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Front
        [(0, 0), (1, 0), (1, 1), (0, 1)]   # Back
    ]
    
    # Draw the main body
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        for j, vertex in enumerate(face):
            if texture_id:
                glTexCoord2f(*tex_coords[i][j])
            glVertex3fv(vertices[vertex])
    glEnd()
    
    # Draw the top surface with a different color
    if texture_id:
        glColor3f(0.8, 0.8, 0.8)  # Lighter color for top
    else:
        glColor3f(color[0] * 1.2, color[1] * 1.2, color[2] * 1.2)  # Lighter version of the color
    
    glBegin(GL_QUADS)
    if texture_id:
        glTexCoord2f(0, 0); glVertex3f(-width/2, 0.21, -width/2)
        glTexCoord2f(1, 0); glVertex3f( width/2, 0.21, -width/2)
        glTexCoord2f(1, 1); glVertex3f( width/2, 0.21,  width/2)
        glTexCoord2f(0, 1); glVertex3f(-width/2, 0.21,  width/2)
    else:
        glVertex3f(-width/2, 0.21, -width/2)
        glVertex3f( width/2, 0.21, -width/2)
        glVertex3f( width/2, 0.21,  width/2)
        glVertex3f(-width/2, 0.21,  width/2)
    glEnd()
    
    if texture_id:
        glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()

def generate_islands():
    global islands, coins, portal_active, portal_pos, in_portal, islands_in_level
    # Keep only islands that are within a reasonable distance
    max_distance = 50  # Maximum distance to keep islands
    islands = [island for island in islands if abs(island['pos'][0] - player_pos[0]) < max_distance]
    coins = [coin for coin in coins if abs(coin[0] - player_pos[0]) < max_distance]
    
    # Generate new islands if needed
    if not islands or player_pos[0] > islands[-1]['pos'][0] - 20:
        # Start from the last island or player position
        start_x = islands[-1]['pos'][0] if islands else player_pos[0]
        
        # Generate islands until we reach 8 per level
        while islands_in_level < 8:
            # Random gap between islands
            gap = random.uniform(min_gap, max_gap)
            start_x += gap
            
            # Random side offset (-4 to 4 units)
            side_offset = random.uniform(-4, 4)
            
            # Random island type
            island_type = random.choice(list(ISLAND_TYPES.keys()))
            
            # Add new island
            islands.append({
                'pos': [start_x, 0, side_offset],
                'type': island_type
            })
            
            # Add coins above island
            for j in range(3):
                coin_x = start_x + (j - 1) * 1.5
                coins.append([coin_x, 1.5, side_offset])
            
            start_x += island_width
            islands_in_level += 1
            
            # Spawn portal after 8th island
            if islands_in_level == 8 and not portal_active:
                portal_active = True
                # Position portal at player height and right at the end of the last island
                portal_pos = [start_x - island_width, 0.7, side_offset]  # Portal at player height
                in_portal = False

def draw_cube(x, y, z, size=1, color=(0.3, 0.8, 0.3), texture_id=None):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    if texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0)
    else:
        glColor3f(*color)
    
    vertices = [
        [-size/2, -size/2, -size/2],  # 0
        [ size/2, -size/2, -size/2],  # 1
        [ size/2,  size/2, -size/2],  # 2
        [-size/2,  size/2, -size/2],  # 3
        [-size/2, -size/2,  size/2],  # 4
        [ size/2, -size/2,  size/2],  # 5
        [ size/2,  size/2,  size/2],  # 6
        [-size/2,  size/2,  size/2],  # 7
    ]
    
    faces = [
        [0, 1, 2, 3],  # Front face
        [4, 5, 6, 7],  # Back face
        [0, 4, 7, 3],  # Left face
        [1, 5, 6, 2],  # Right face
        [0, 1, 5, 4],  # Bottom face
        [3, 2, 6, 7]   # Top face
    ]
    
    # Define texture coordinates for each face
    tex_coords = [
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Front
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Back
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Left
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Right
        [(0, 0), (1, 0), (1, 1), (0, 1)],  # Bottom
        [(0, 0), (1, 0), (1, 1), (0, 1)]   # Top
    ]
    
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        for j, vertex in enumerate(face):
            if texture_id:
                glTexCoord2f(*tex_coords[i][j])
            glVertex3fv(vertices[vertex])
    glEnd()
    
    if texture_id:
        glDisable(GL_TEXTURE_2D)
    
    glPopMatrix()

def check_ground():
    for island in islands:
        if abs(player_pos[0] - island['pos'][0]) < island_width/2 and abs(player_pos[2] - island['pos'][2]) < island_width/2:
            if abs(player_pos[1] - island['pos'][1] - 0.7) < 0.2:  # Adjusted for new island height
                return True
    return False

def check_coin_collection():
    global score, coins
    remaining = []
    for coin in coins:
        if abs(player_pos[0] - coin[0]) < 1.5 and abs(player_pos[2] - coin[2]) < 1.5 and abs(player_pos[1] - coin[1]) < 1.5:
            score += 1
            print(f"Coin collected! Score: {score}")  # Debug print
        else:
            remaining.append(coin)
    coins = remaining

def draw_portal(x, y, z, rotation, scale):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(rotation, 0, 1, 0)
    glScalef(scale, scale, scale)
    
    # Enable blending for portal effects
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw outer glow
    glColor4f(0.0, 0.8, 1.0, 0.3)  # Light blue with transparency
    glBegin(GL_QUAD_STRIP)
    for i in range(37):  # 36 segments for smooth circle
        angle = i * 10 * math.pi / 180
        # Outer glow
        glVertex3f(math.cos(angle) * 3, math.sin(angle) * 0.5, math.sin(angle) * 3)
        # Inner glow
        glVertex3f(math.cos(angle) * 2.5, math.sin(angle) * 0.5, math.sin(angle) * 2.5)
    glEnd()
    
    # Draw portal ring
    glColor4f(0.0, 0.8, 1.0, 0.8)  # More opaque light blue
    glBegin(GL_QUAD_STRIP)
    for i in range(37):  # 36 segments for smooth circle
        angle = i * 10 * math.pi / 180
        # Outer ring
        glVertex3f(math.cos(angle) * 2, math.sin(angle) * 0.5, math.sin(angle) * 2)
        # Inner ring
        glVertex3f(math.cos(angle) * 1.5, math.sin(angle) * 0.5, math.sin(angle) * 1.5)
    glEnd()
    
    # Draw portal center with pulsing effect
    pulse = math.sin(portal_animation_time * 0.1) * 0.2 + 0.8
    glColor4f(0.0, 0.8, 1.0, 0.5 * pulse)  # Pulsing transparency
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0, 0, 0)  # Center
    for i in range(37):  # 36 segments
        angle = i * 10 * math.pi / 180
        glVertex3f(math.cos(angle) * 1.5, math.sin(angle) * 0.5, math.sin(angle) * 1.5)
    glEnd()
    
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_transition_effect():
    if transition_effect:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, 800, 600, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Draw white flash
        glColor4f(1.0, 1.0, 1.0, transition_alpha)
        glBegin(GL_QUADS)
        glVertex2f(0, 0)
        glVertex2f(800, 0)
        glVertex2f(800, 600)
        glVertex2f(0, 600)
        glEnd()
        
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

def check_portal_collision():
    global in_portal, level, portal_active, portal_animation_time, transition_effect, transition_alpha
    if portal_active and not in_portal:
        if (abs(player_pos[0] - portal_pos[0]) < 2 and 
            abs(player_pos[1] - portal_pos[1]) < 2 and 
            abs(player_pos[2] - portal_pos[2]) < 2):
            in_portal = True
            level += 1
            portal_animation_time = 0
            transition_effect = True
            transition_alpha = 0.0
            return True
    return False

def draw_player(x, y, z):
    # Disable lighting for the player to maintain colors
    glDisable(GL_LIGHTING)
    
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Rotate to face forward
    glRotatef(90, 0, 1, 0)  # Rotate to face forward
    
    # Body (main part)
    glColor3f(0.0, 0.6, 1.0)  # Bright blue color
    glPushMatrix()
    glScalef(0.3, 0.5, 0.2)  # Make body taller and thinner
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.6, 1.0))
    glPopMatrix()
    
    # Head
    glColor3f(1.0, 0.9, 0.8)  # Light skin tone
    glPushMatrix()
    glTranslatef(0, 0.4, 0)  # Position head on top of body
    glScalef(0.25, 0.25, 0.25)  # Make head smaller than body
    draw_cube(0, 0, 0, size=1.0, color=(1.0, 0.9, 0.8))
    glPopMatrix()
    
    # Face details
    # Eyes
    glColor3f(0.0, 0.0, 0.0)  # Black for eyes
    # Left eye
    glPushMatrix()
    glTranslatef(-0.06, 0.4, 0.13)  # Position left eye
    glScalef(0.04, 0.04, 0.04)
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.0, 0.0))
    glPopMatrix()
    
    # Right eye
    glPushMatrix()
    glTranslatef(0.06, 0.4, 0.13)  # Position right eye
    glScalef(0.04, 0.04, 0.04)
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.0, 0.0))
    glPopMatrix()
    
    # Smile
    glColor3f(0.0, 0.0, 0.0)  # Black for smile
    glPushMatrix()
    glTranslatef(0, 0.35, 0.13)  # Position smile
    glScalef(0.1, 0.02, 0.02)
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.0, 0.0))
    glPopMatrix()
    
    # Arms
    glColor3f(0.0, 0.6, 1.0)  # Same blue as body
    # Left arm
    glPushMatrix()
    glTranslatef(-0.2, 0.1, 0)  # Position left arm
    glScalef(0.1, 0.3, 0.1)  # Make arms thin and long
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.6, 1.0))
    glPopMatrix()
    
    # Right arm
    glPushMatrix()
    glTranslatef(0.2, 0.1, 0)  # Position right arm
    glScalef(0.1, 0.3, 0.1)  # Make arms thin and long
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.6, 1.0))
    glPopMatrix()
    
    # Legs
    glColor3f(0.0, 0.3, 0.8)  # Darker blue for pants
    # Left leg
    glPushMatrix()
    glTranslatef(-0.1, -0.4, 0)  # Position left leg
    glScalef(0.1, 0.3, 0.1)  # Make legs thin and long
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.3, 0.8))
    glPopMatrix()
    
    # Right leg
    glPushMatrix()
    glTranslatef(0.1, -0.4, 0)  # Position right leg
    glScalef(0.1, 0.3, 0.1)  # Make legs thin and long
    draw_cube(0, 0, 0, size=1.0, color=(0.0, 0.3, 0.8))
    glPopMatrix()
    
    glPopMatrix()
    
    # Re-enable lighting for the rest of the scene
    glEnable(GL_LIGHTING)

def draw_scene():
    global portal_rotation, portal_scale, portal_animation_time, transition_alpha
    
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Draw sky background
    glClearColor(0.5, 0.7, 1.0, 1.0)  # Light blue sky color
    
    # Draw clouds
    for cloud in clouds:
        draw_cloud(cloud['pos'][0], cloud['pos'][1], cloud['pos'][2], cloud['size'])
    
    # Set up camera to look from behind the player
    glLoadIdentity()
    gluLookAt(
        player_pos[0] - 12,  # Camera X: 12 units behind player
        player_pos[1] + 4,   # Camera Y: 4 units above player (lower view)
        player_pos[2],       # Camera Z: Same Z as player
        player_pos[0] + 25,  # Look at point: 25 units ahead of player
        player_pos[1],       # Look at Y: Same height as player
        player_pos[2],       # Look at Z: Same Z as player
        0, 1, 0             # Up vector
    )
    
    # Enable lighting and depth testing for 3D scene
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set up light with increased intensity and better positioning
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 20, 0, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.4, 0.4, 0.4, 1))  # Reduced ambient light
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))  # Reduced diffuse light
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.5, 0.5, 0.5, 1))  # Reduced specular light
    
    # Set material properties for better color visibility
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, (0.4, 0.4, 0.4, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.5, 0.5, 0.5, 1))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 30.0)  # Reduced shininess
    
    # Draw islands
    for island in islands:
        texture_id = textures.get(island['type'])
        if texture_id:
            draw_island(island['pos'][0], island['pos'][1], island['pos'][2], 
                       island_width, ISLAND_TYPES[island['type']]['color'], texture_id)
        else:
            draw_island(island['pos'][0], island['pos'][1], island['pos'][2], 
                       island_width, ISLAND_TYPES[island['type']]['color'])
    
    # Draw coins with glow effect
    for coin in coins:
        # Draw outer glow
        glColor3f(1.0, 1.0, 0.0)  # Bright yellow
        draw_cube(coin[0], coin[1], coin[2], size=0.8, color=(1.0, 1.0, 0.0))
        # Draw inner coin
        glColor3f(1.0, 0.8, 0.0)  # Slightly darker yellow
        draw_cube(coin[0], coin[1], coin[2], size=0.6, color=(1.0, 0.8, 0.0))
    
    # Draw portal if active
    if portal_active:
        portal_rotation += 3  # Faster rotation
        portal_animation_time += 1
        portal_scale = 1.0 + math.sin(portal_animation_time * 0.1) * 0.3  # Larger scale variation
        draw_portal(portal_pos[0], portal_pos[1], portal_pos[2], portal_rotation, portal_scale)
    
    # Draw player character
    draw_player(player_pos[0], player_pos[1], player_pos[2])
    
    # Draw transition effect
    draw_transition_effect()
    
    # Draw HUD (coin counter and level)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 600, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable 3D features for 2D rendering
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_COLOR_MATERIAL)
    
    # Draw black background for coin counter
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(10, 10)
    glVertex2f(150, 10)
    glVertex2f(150, 50)
    glVertex2f(10, 50)
    glEnd()
    
    # Draw coin counter text
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(20, 35)
    score_text = f"Coins: {score}"
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Draw level counter
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(10, 60)
    glVertex2f(150, 60)
    glVertex2f(150, 100)
    glVertex2f(10, 100)
    glEnd()
    
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(20, 85)
    level_text = f"Level: {level}"
    for char in level_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Restore OpenGL state
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    
    # Restore matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    pygame.display.flip()

def draw_text(x, y, text, color=(1.0, 1.0, 1.0)):
    glColor3f(*color)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_start_screen():
    # Switch to 2D rendering mode
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 800, 600, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Clear the screen with a gradient background
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Draw gradient background
    glBegin(GL_QUADS)
    # Top color (darker blue)
    glColor3f(0.1, 0.2, 0.4)
    glVertex2f(0, 0)
    glVertex2f(800, 0)
    # Bottom color (lighter blue)
    glColor3f(0.2, 0.4, 0.8)
    glVertex2f(800, 600)
    glVertex2f(0, 600)
    glEnd()
    
    # Draw decorative elements
    # Draw stars
    glColor3f(1.0, 1.0, 1.0)
    for _ in range(50):
        x = random.randint(0, 800)
        y = random.randint(0, 300)
        size = random.uniform(1, 3)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + size, y)
        glVertex2f(x + size, y + size)
        glVertex2f(x, y)
        glEnd()
    
    # Draw title with glow effect
    # Outer glow
    glColor3f(0.0, 0.8, 1.0)  # Light blue
    for offset in range(-2, 3):
        for offset2 in range(-2, 3):
            glRasterPos2f(300 + offset, 150 + offset2)
            for char in "Skybound-Realms":
                glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    
    # Main title
    glColor3f(1.0, 1.0, 1.0)  # White
    glRasterPos2f(300, 150)
    for char in "Skybound-Realms":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    
    # Draw controls with better formatting
    controls = [
        "JUMP = SPACE",
        "LEFT = A",
        "RIGHT = D"
    ]
    
    y_pos = 300
    for control in controls:
        # Draw text shadow
        glColor3f(0.0, 0.0, 0.0)  # Black shadow
        glRasterPos2f(302, y_pos + 2)
        for char in control:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
        # Draw main text
        glColor3f(1.0, 1.0, 1.0)  # White text
        glRasterPos2f(300, y_pos)
        for char in control:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        y_pos += 50
    
    # Draw start message with animation
    pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.2 + 0.8  # Pulsing effect
    glColor3f(0.8 * pulse, 0.8 * pulse, 1.0 * pulse)  # Pulsing light blue
    glRasterPos2f(250, 500)
    for char in "Press any key to start":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Restore OpenGL state
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    # Restore matrices
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    
    pygame.display.flip()

def main():
    global player_pos, player_vel, on_ground, score, level, textures, clouds, portal_active, portal_pos, in_portal, islands_in_level, transition_effect, transition_alpha, islands, coins
    
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    # Initialize GLUT
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    
    # Enable texture mapping and blending
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # OpenGL setup
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, display[0] / display[1], 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.5, 0.7, 1.0, 1.0)  # Light blue sky color
    
    # Load textures
    textures = {}
    for island_type in ISLAND_TYPES:
        try:
            texture_path = f"textures/{ISLAND_TYPES[island_type]['texture']}"
            print(f"Loading texture: {texture_path}")
            textures[island_type] = load_texture(texture_path)
            if textures[island_type] is None:
                print(f"Failed to load texture for {island_type}")
        except Exception as e:
            print(f"Error loading texture for {island_type}: {e}")
    
    # Generate initial islands and clouds
    generate_islands()
    generate_clouds()
    
    # Place player on first island
    if islands:
        player_pos = [islands[0]['pos'][0], islands[0]['pos'][1] + 0.7, islands[0]['pos'][2]]
        player_vel = [0, 0, 0]
        on_ground = True
    
    clock = pygame.time.Clock()
    running = True
    game_started = False
    
    # Start screen loop
    while running and not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                game_started = True
        
        draw_start_screen()
        clock.tick(60)
    
    # Main game loop
    while running and game_started:
        clock.tick(60)
        
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Handle all key presses simultaneously
        keys = pygame.key.get_pressed()
        
        # Automatic forward movement
        player_pos[0] += auto_move_speed
        
        # Left/right movement (using A and D keys)
        if keys[K_a]:
            player_pos[2] -= side_move_speed
        if keys[K_d]:
            player_pos[2] += side_move_speed
        
        # Jump (can be pressed while moving)
        if keys[K_SPACE] and on_ground:
            player_vel[1] = jump_strength
        
        # Physics
        player_vel[1] += gravity
        player_pos[1] += player_vel[1]
        
        on_ground = check_ground()
        if on_ground and player_vel[1] < 0:
            player_vel[1] = 0
            player_pos[1] = 0.7
        
        if player_pos[1] < -5:
            print(f"Game Over! Score: {score}")
            running = False
        
        # Check for portal collision
        if check_portal_collision():
            # Start transition effect
            transition_effect = True
            transition_alpha = 0.0
        
        # Update transition effect
        if transition_effect:
            transition_alpha += 0.1
            if transition_alpha >= 1.0:
                # Reset portal state
                portal_active = False
                in_portal = False
                islands_in_level = 0
                # Clear existing islands and coins
                islands = []
                coins = []
                # Generate new islands for the next level
                generate_islands()
                # Reset player position to start of new level
                if islands:
                    player_pos = [islands[0]['pos'][0], islands[0]['pos'][1] + 0.7, islands[0]['pos'][2]]
                    player_vel = [0, 0, 0]
                    on_ground = True
                transition_effect = False
                transition_alpha = 0.0
        
        # Update game state
        check_coin_collection()
        
        # Generate new islands and clean up old ones
        generate_islands()
        
        # Move clouds
        for cloud in clouds:
            cloud['pos'][0] -= 0.02  # Move clouds slowly
            if cloud['pos'][0] < player_pos[0] - 50:  # Reset cloud position if too far behind
                cloud['pos'][0] = player_pos[0] + 50
                cloud['pos'][1] = random.uniform(5, 15)
                cloud['pos'][2] = random.uniform(-20, 20)
        
        draw_scene()
    
    pygame.quit()

if __name__ == "__main__":
    main()
