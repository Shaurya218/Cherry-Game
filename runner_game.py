import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 50
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (135, 206, 235)  # Sky blue
GREEN = (76, 153, 0)    # Ground
RED = (255, 0, 0)       # Player
BROWN = (139, 69, 19)   # Tree
YELLOW = (255, 215, 0)  # Bee
DARK_BLUE = (65, 105, 225)  # Bird
GRAY = (128, 128, 128)  # Box
CLOUD_WHITE = (240, 240, 240)  # Slightly off-white for clouds
MOUNTAIN_COLORS = [
    (110, 110, 160),  # Distant mountains (purplish)
    (90, 120, 150),   # Mid mountains (bluish)
    (70, 90, 120)     # Near mountains (darker blue)
]
CHERRY_BLOSSOM = (255, 223, 228)  # Light pink for cherry blossoms

# Global variables
obstacles = []
ground_patches = []
mountains = []
cherry_blossoms = []

# Mountain class for background
class Mountain:
    def __init__(self, layer):
        self.layer = layer  # 0 = farthest, 2 = closest
        self.color = MOUNTAIN_COLORS[layer]
        self.height = random.randint(80, 150) + (layer * 30)
        self.width = random.randint(200, 400) + (layer * 50)
        self.x = random.randint(-100, SCREEN_WIDTH)
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.speed = 0.2 + (layer * 0.2)  # Parallax effect - closer mountains move faster
    
    def update(self, game_speed):
        self.x -= self.speed * game_speed
        if self.x + self.width < -100:
            self.x = SCREEN_WIDTH + random.randint(0, 100)
            self.height = random.randint(80, 150) + (self.layer * 30)
            self.width = random.randint(200, 400) + (self.layer * 50)
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
    
    def draw(self, screen):
        # Draw mountain silhouette
        points = [
            (self.x, SCREEN_HEIGHT - GROUND_HEIGHT),  # Bottom left
            (self.x + self.width * 0.2, self.y + self.height * 0.7),  # First bump
            (self.x + self.width * 0.4, self.y + self.height * 0.3),  # Second bump
            (self.x + self.width * 0.6, self.y),  # Peak
            (self.x + self.width * 0.8, self.y + self.height * 0.5),  # Fourth bump
            (self.x + self.width, SCREEN_HEIGHT - GROUND_HEIGHT)  # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)
        
        # Add snow caps on distant mountains
        if self.layer == 0:
            snow_points = [
                (self.x + self.width * 0.5, self.y + 5),
                (self.x + self.width * 0.6, self.y),
                (self.x + self.width * 0.7, self.y + 5)
            ]
            pygame.draw.polygon(screen, WHITE, snow_points)

# Cherry Blossom petal class
class CherryBlossom:
    def __init__(self):
        self.size = random.randint(3, 6)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-50, SCREEN_HEIGHT // 2)
        self.speed_y = random.uniform(0.5, 1.5)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.alpha = random.randint(150, 255)
        self.color = CHERRY_BLOSSOM
    
    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x + math.sin(pygame.time.get_ticks() * 0.001 + self.x * 0.1) * 0.5
        self.rotation += self.rotation_speed
        
        # Reset if off screen
        if self.y > SCREEN_HEIGHT or self.x < -20 or self.x > SCREEN_WIDTH + 20:
            self.reset()
    
    def reset(self):
        self.size = random.randint(3, 6)
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-30, -10)
        self.speed_y = random.uniform(0.5, 1.5)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(150, 255)
    
    def draw(self, screen):
        # Create a surface for the petal with transparency
        petal_surface = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)
        
        # Draw a petal shape (oval)
        pygame.draw.ellipse(petal_surface, (*self.color, self.alpha), (0, 0, self.size * 2, self.size))
        
        # Rotate the petal
        rotated_petal = pygame.transform.rotate(petal_surface, self.rotation)
        
        # Get the rect of the rotated surface
        rect = rotated_petal.get_rect(center=(self.x, self.y))
        
        # Draw the rotated petal
        screen.blit(rotated_petal, rect)

# Cloud class for background
class Cloud:
    def __init__(self):
        self.width = random.randint(60, 120)
        self.height = random.randint(30, 50)
        self.x = SCREEN_WIDTH + random.randint(0, 100)
        self.y = random.randint(20, 150)
        self.speed = random.uniform(0.5, 1.5)
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        # Draw a fluffy cloud using multiple circles
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Draw main cloud body
        pygame.draw.ellipse(screen, CLOUD_WHITE, 
                          (center_x - self.width//2, center_y - self.height//2, 
                           self.width, self.height))
        
        # Draw additional cloud puffs
        puff_radius = self.height // 2
        pygame.draw.circle(screen, CLOUD_WHITE, 
                         (center_x - self.width//4, center_y), puff_radius)
        pygame.draw.circle(screen, CLOUD_WHITE, 
                         (center_x + self.width//4, center_y), puff_radius)
        pygame.draw.circle(screen, CLOUD_WHITE, 
                         (center_x, center_y - self.height//4), puff_radius)
        
    def is_off_screen(self):
        return self.x + self.width < 0
# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Runner Game")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont('Arial', 30)

class Player:
    def __init__(self):
        self.radius = 25
        self.x = 80
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.radius
        self.velocity = 0
        self.gravity = 1
        self.jump_power = -18
        self.is_jumping = False
        self.is_ducking = False
        self.duck_radius = 15
        self.normal_radius = self.radius
        self.rotation = 0  # For rolling animation
        self.falling = False  # Track if player is falling into a hole
    
    def jump(self):
        if not self.is_jumping and not self.is_ducking and not self.falling:
            self.is_jumping = True
            self.velocity = self.jump_power
    
    def duck(self):
        if not self.is_jumping and not self.falling:
            self.is_ducking = True
            self.radius = self.duck_radius
            # Adjust y position to keep the player on the ground
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.radius
    
    def stop_duck(self):
        if self.is_ducking and not self.falling:
            self.is_ducking = False
            self.radius = self.normal_radius
            # Adjust y position to keep the player on the ground
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.radius
    
    def update(self):
        # Apply gravity
        if self.is_jumping:
            self.y += self.velocity
            self.velocity += self.gravity
            
            # Check if player has landed
            if self.y >= SCREEN_HEIGHT - GROUND_HEIGHT - self.radius:
                self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.radius
                self.is_jumping = False
                self.velocity = 0
        
        # Update rotation for rolling animation
        if not self.is_jumping and not self.is_ducking:
            self.rotation = (self.rotation + 5) % 360
    
    def draw(self, screen):
        # Draw the ball
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        
        # Add a line to show rotation (optional)
        if not self.is_ducking:
            end_x = self.x + self.radius * 0.8 * pygame.math.Vector2(1, 0).rotate(self.rotation).x
            end_y = self.y + self.radius * 0.8 * pygame.math.Vector2(1, 0).rotate(self.rotation).y
            pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 3)

class Obstacle:
    def __init__(self, game_speed):
        self.game_speed = game_speed
        self.type = random.choice(['box', 'tree', 'bee', 'bird', 'hole'])
        
        # Set dimensions and position based on type
        if self.type == 'box':
            self.width = 35
            self.height = 35
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
            self.color = (200, 150, 100)  # Light brown/tan for house
            self.is_house = True
        elif self.type == 'tree':
            self.width = 38  # Increased from 35
            self.height = 75  # Increased from 70
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
            self.color = (100, 100, 150)  # Building color (grayish blue)
            # Add window data
            self.is_building = True
            self.num_floors = 4  # Increased back to 4 floors
            self.num_windows = 2
        elif self.type == 'bee':
            self.width = 60  # Wider
            self.height = 30  # Taller
            # Position at a height where player must duck (considering normal player radius)
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 60
            self.color = YELLOW
        elif self.type == 'bird':
            self.width = 70  # Wider
            self.height = 35  # Taller
            # Position at a height where player must duck (considering normal player radius)
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT - 70
            self.color = DARK_BLUE
        elif self.type == 'hole':
            self.width = 70  # Increased from 50
            self.height = GROUND_HEIGHT  # Make hole as deep as the ground
            self.y = SCREEN_HEIGHT - GROUND_HEIGHT  # Position at ground level
            self.color = BLACK
            self.is_hole = True
        
        self.x = SCREEN_WIDTH
    
    def update(self):
        self.x -= self.game_speed
    
    def draw(self, screen):
        # Draw the obstacle
        if hasattr(self, 'is_hole') and self.is_hole:
            # Draw a more realistic hole
            
            # Draw the main hole (black background)
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # Draw dirt texture on the sides of the hole
            dirt_color = (101, 67, 33)  # Brown color for dirt
            dark_dirt_color = (60, 40, 20)  # Darker brown for depth
            
            # Left edge of hole
            pygame.draw.rect(screen, dirt_color, (self.x, self.y, 5, self.height))
            # Right edge of hole
            pygame.draw.rect(screen, dirt_color, (self.x + self.width - 5, self.y, 5, self.height))
            
            # Add some depth effect with darker color at the bottom
            pygame.draw.rect(screen, dark_dirt_color, 
                           (self.x + 5, self.y + 10, self.width - 10, self.height - 10))
            
            # Add some texture/detail to make the hole look deeper
            for i in range(3):
                depth_line_y = self.y + 15 + i * 10
                if depth_line_y < self.y + self.height:
                    # Draw horizontal lines with varying darkness
                    line_color = (max(20, 40 - i * 10), max(20, 40 - i * 10), max(20, 40 - i * 10))
                    pygame.draw.line(screen, line_color, 
                                   (self.x + 10, depth_line_y),
                                   (self.x + self.width - 10, depth_line_y), 2)
            
            # Add some small rocks/debris at the bottom
            for _ in range(5):
                rock_x = self.x + random.randint(10, self.width - 10)
                rock_y = self.y + self.height - random.randint(5, 15)
                rock_size = random.randint(1, 3)
                rock_color = (100 + random.randint(-20, 20), 
                             100 + random.randint(-20, 20), 
                             100 + random.randint(-20, 20))  # Grayish with variation
                pygame.draw.circle(screen, rock_color, (rock_x, rock_y), rock_size)
            
            # Add some grass hanging over the edges
            for x_offset in range(0, self.width, 8):
                if random.random() < 0.5:
                    grass_x = self.x + x_offset
                    grass_length = random.randint(2, 5)
                    grass_color = (50, 205, 50) if random.random() > 0.3 else (34, 139, 34)
                    
                    if x_offset < 10 or x_offset > self.width - 10:  # Only at the edges
                        pygame.draw.line(screen, grass_color, 
                                       (grass_x, self.y),
                                       (grass_x + random.choice([-1, 1]) * 2, self.y + grass_length), 1)
        
        elif self.type == 'bee':
            # Draw a realistic bee
            
            # Body parts
            body_color = (250, 217, 65)  # Yellow
            stripe_color = (10, 10, 10)  # Black
            wing_color = (240, 240, 255, 150)  # Transparent white
            
            # Calculate center points
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Draw the main body (ellipse)
            body_rect = pygame.Rect(self.x + 10, center_y - 8, self.width - 20, 16)
            pygame.draw.ellipse(screen, body_color, body_rect)
            
            # Draw black stripes
            stripe_width = 4
            for i in range(3):
                stripe_x = self.x + 15 + i * 10
                stripe_rect = pygame.Rect(stripe_x, center_y - 8, stripe_width, 16)
                pygame.draw.ellipse(screen, stripe_color, stripe_rect)
            
            # Draw head (circle)
            head_radius = 7
            pygame.draw.circle(screen, stripe_color, (self.x + 8, center_y), head_radius)
            
            # Draw eyes
            eye_color = (255, 255, 255)  # White
            pygame.draw.circle(screen, eye_color, (self.x + 5, center_y - 3), 2)
            pygame.draw.circle(screen, eye_color, (self.x + 5, center_y + 3), 2)
            
            # Draw wings (semi-transparent)
            wing_surface = pygame.Surface((20, 15), pygame.SRCALPHA)
            pygame.draw.ellipse(wing_surface, wing_color, (0, 0, 20, 15))
            
            # Draw top and bottom wings with slight angle
            screen.blit(wing_surface, (center_x - 5, center_y - 15))
            
            # Flip the wing surface for bottom wing
            bottom_wing = pygame.transform.flip(wing_surface, False, True)
            screen.blit(bottom_wing, (center_x - 5, center_y))
            
            # Draw stinger
            pygame.draw.polygon(screen, stripe_color, [
                (self.x + self.width - 5, center_y),
                (self.x + self.width + 3, center_y - 2),
                (self.x + self.width + 3, center_y + 2)
            ])
            
            # Add animation - make wings "flutter"
            if pygame.time.get_ticks() % 200 < 100:  # Alternate every 100ms
                flutter_wing = pygame.transform.rotate(wing_surface, 15)
                screen.blit(flutter_wing, (center_x - 8, center_y - 15))
                flutter_bottom = pygame.transform.rotate(bottom_wing, -15)
                screen.blit(flutter_bottom, (center_x - 8, center_y))
        
        elif self.type == 'bird':
            # Draw a realistic bird
            
            # Bird colors
            body_color = (65, 105, 225)  # Royal blue
            wing_color = (30, 70, 180)  # Darker blue
            beak_color = (255, 165, 0)  # Orange
            eye_color = (255, 255, 255)  # White
            pupil_color = (0, 0, 0)  # Black
            
            # Calculate center points
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            
            # Draw the main body (ellipse)
            body_rect = pygame.Rect(self.x + 5, center_y - 10, self.width - 15, 20)
            pygame.draw.ellipse(screen, body_color, body_rect)
            
            # Draw head
            head_radius = 10
            pygame.draw.circle(screen, body_color, (self.x + 15, center_y - 5), head_radius)
            
            # Draw eye
            pygame.draw.circle(screen, eye_color, (self.x + 12, center_y - 8), 3)
            pygame.draw.circle(screen, pupil_color, (self.x + 12, center_y - 8), 1)
            
            # Draw beak
            pygame.draw.polygon(screen, beak_color, [
                (self.x + 5, center_y - 5),
                (self.x - 5, center_y),
                (self.x + 5, center_y + 2)
            ])
            
            # Draw tail
            pygame.draw.polygon(screen, body_color, [
                (self.x + self.width - 10, center_y - 5),
                (self.x + self.width + 5, center_y),
                (self.x + self.width - 10, center_y + 5)
            ])
            
            # Draw wings
            # Determine wing position based on time for flapping animation
            wing_time = pygame.time.get_ticks() % 600
            if wing_time < 200:  # Wings up
                wing_y_offset = -10
                wing_height = 15
            elif wing_time < 400:  # Wings middle
                wing_y_offset = -5
                wing_height = 10
            else:  # Wings down
                wing_y_offset = 0
                wing_height = 5
                
            # Draw the wing
            pygame.draw.ellipse(screen, wing_color, 
                              (center_x - 15, center_y + wing_y_offset, 
                               30, wing_height))
            
            # Add some feather details
            for i in range(3):
                feather_x = center_x - 10 + i * 10
                pygame.draw.line(screen, (50, 90, 200),
                               (feather_x, center_y + wing_y_offset + wing_height - 2),
                               (feather_x, center_y + wing_y_offset + wing_height + 3), 1)
        
        elif hasattr(self, 'is_house') and self.is_house:
            # Draw the main house body first
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # Draw a roof (triangle)
            roof_color = (180, 0, 0)  # Red roof
            pygame.draw.polygon(screen, roof_color, [
                (self.x - 5, self.y),
                (self.x + self.width//2, self.y - 15),
                (self.x + self.width + 5, self.y)
            ])
            
            # Draw windows (2 small windows)
            window_color = (200, 255, 255)  # Light blue windows
            window_width = 8
            window_height = 8
            window_margin = 6
            
            # Left window
            pygame.draw.rect(screen, window_color, 
                            (self.x + window_margin, self.y + window_margin, 
                             window_width, window_height))
            pygame.draw.rect(screen, BLACK, 
                            (self.x + window_margin, self.y + window_margin, 
                             window_width, window_height), 1)
            
            # Right window
            pygame.draw.rect(screen, window_color, 
                            (self.x + self.width - window_margin - window_width, 
                             self.y + window_margin, window_width, window_height))
            pygame.draw.rect(screen, BLACK, 
                            (self.x + self.width - window_margin - window_width, 
                             self.y + window_margin, window_width, window_height), 1)
            
            # Draw a door
            door_width = 10
            door_height = 15
            door_x = self.x + (self.width - door_width) // 2
            door_y = self.y + self.height - door_height
            
            pygame.draw.rect(screen, (101, 67, 33), (door_x, door_y, door_width, door_height))
            pygame.draw.rect(screen, BLACK, (door_x, door_y, door_width, door_height), 1)
            
            # Door knob
            pygame.draw.circle(screen, YELLOW, (door_x + door_width - 3, door_y + door_height//2), 2)
            
        elif hasattr(self, 'is_building') and self.is_building:
            # Draw the main building body first (solid color)
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            
            # Draw a roof
            roof_color = (160, 82, 45)  # Brown roof
            pygame.draw.polygon(screen, roof_color, [
                (self.x - 5, self.y),
                (self.x + self.width//2, self.y - 15),
                (self.x + self.width + 5, self.y)
            ])
            
            # Window properties
            window_width = 8
            window_height = 10
            window_color = (200, 255, 255)  # Light blue windows
            window_margin = 4
            
            # Draw windows on each floor
            floor_height = (self.height - (self.num_floors + 1) * window_margin) / self.num_floors
            
            for floor in range(self.num_floors):
                for window in range(self.num_windows):
                    window_x = self.x + window_margin + window * (window_width + window_margin)
                    window_y = self.y + window_margin + floor * (floor_height)
                    
                    # Draw the window
                    pygame.draw.rect(screen, window_color, 
                                    (window_x, window_y, window_width, window_height))
                    
                    # Draw window frame
                    pygame.draw.rect(screen, BLACK, 
                                    (window_x, window_y, window_width, window_height), 1)
            
            # Draw a door at the bottom
            door_width = 12
            door_height = 20
            door_x = self.x + (self.width - door_width) // 2
            door_y = self.y + self.height - door_height
            
            pygame.draw.rect(screen, (101, 67, 33), (door_x, door_y, door_width, door_height))
            pygame.draw.rect(screen, BLACK, (door_x, door_y, door_width, door_height), 1)
            
            # Door knob
            pygame.draw.circle(screen, YELLOW, (door_x + door_width - 3, door_y + door_height//2), 2)
        
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
    
    def is_off_screen(self):
        return self.x < -self.width
def draw_background(game_speed):
    # Draw sky gradient
    sky_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_HEIGHT)
    
    # Draw mountains in layers (back to front)
    for mountain in mountains:
        mountain.update(game_speed)
        mountain.draw(screen)
    
    # Draw cherry blossoms
    for blossom in cherry_blossoms:
        blossom.update()
        blossom.draw(screen)

def draw_ground():
    # Draw the ground, but with gaps for holes
    holes = [obstacle for obstacle in obstacles if hasattr(obstacle, 'is_hole') and obstacle.is_hole]
    
    # Draw ground in segments, skipping the holes
    current_x = 0
    for hole in sorted(holes, key=lambda h: h.x):
        if hole.x > current_x:
            # Draw ground segment before the hole
            draw_ground_segment(current_x, hole.x)
            
            # Add grass on top of this ground segment
            draw_grass(current_x, hole.x)
            
        # Skip the hole
        current_x = hole.x + hole.width
    
    # Draw the final segment after the last hole
    if current_x < SCREEN_WIDTH:
        draw_ground_segment(current_x, SCREEN_WIDTH)
        
        # Add grass on top of this ground segment
        draw_grass(current_x, SCREEN_WIDTH)

def draw_ground_segment(start_x, end_x):
    # Draw a more realistic ground segment with texture
    
    # Main ground rectangle
    pygame.draw.rect(screen, GREEN, 
                   (start_x, SCREEN_HEIGHT - GROUND_HEIGHT, 
                    end_x - start_x, GROUND_HEIGHT))
    
    # Add a darker top layer of soil
    soil_color = (76, 120, 0)  # Darker green/brown for soil
    pygame.draw.rect(screen, soil_color, 
                   (start_x, SCREEN_HEIGHT - GROUND_HEIGHT, 
                    end_x - start_x, 5))
    
    # Add some texture/dirt patches from the global list
    for x, y, size, color in ground_patches:
        # Only draw patches that are within this segment
        if start_x <= x <= end_x:
            pygame.draw.circle(screen, color, (int(x), int(y)), size)

def draw_grass(start_x, end_x):
    # Draw more realistic grass on top of the ground
    grass_color = (50, 205, 50)  # Bright green for grass
    dark_grass_color = (34, 139, 34)  # Darker green for variation
    
    # Draw a base layer of grass (short blades)
    for x in range(int(start_x), int(end_x), 4):
        # Vary the height slightly for a more natural look
        height_variation = random.randint(1, 4)
        blade_height = height_variation
        
        # Alternate between light and dark green
        color = grass_color if random.random() > 0.3 else dark_grass_color
        
        # Draw a simple grass blade (line)
        pygame.draw.line(screen, color, 
                       (x, SCREEN_HEIGHT - GROUND_HEIGHT),
                       (x, SCREEN_HEIGHT - GROUND_HEIGHT - blade_height), 1)
    
    # Draw taller grass blades less frequently
    for x in range(int(start_x), int(end_x), 10):
        if random.random() < 0.7:  # 70% chance for tall grass
            # Vary the height for a more natural look
            height = random.randint(4, 8)
            
            # Alternate between light and dark green
            color = grass_color if random.random() > 0.3 else dark_grass_color
            
            # Draw a slightly curved grass blade
            curve = random.choice([-1, 1]) * random.random() * 2
            
            # Draw a curved blade using multiple short lines
            blade_x = x
            for h in range(height):
                pygame.draw.line(screen, color, 
                               (blade_x, SCREEN_HEIGHT - GROUND_HEIGHT - h),
                               (blade_x + curve, SCREEN_HEIGHT - GROUND_HEIGHT - h - 1), 2)
                blade_x += curve * 0.5
                
    # Add some small flowers occasionally
    for x in range(int(start_x), int(end_x), 30):
        if random.random() < 0.15:  # 15% chance for a flower
            flower_y = SCREEN_HEIGHT - GROUND_HEIGHT - 6
            flower_color = random.choice([(255, 255, 0), (255, 192, 203), (255, 255, 255)])  # Yellow, pink, or white
            pygame.draw.circle(screen, flower_color, (x, flower_y), 2)
            # Draw small petals
            for angle in range(0, 360, 90):
                petal_x = x + 2 * pygame.math.Vector2(1, 0).rotate(angle).x
                petal_y = flower_y + 2 * pygame.math.Vector2(1, 0).rotate(angle).y
                pygame.draw.circle(screen, flower_color, (int(petal_x), int(petal_y)), 1)

def show_score(score):
    # Create a semi-transparent score display
    score_font = pygame.font.SysFont('Arial', 28)
    speed_font = pygame.font.SysFont('Arial', 20)
    
    # Render score with shadow
    score_shadow = score_font.render(f"Score: {score}", True, (20, 20, 20))
    score_text = score_font.render(f"Score: {score}", True, WHITE)
    
    # Create a small panel for the score
    panel_width = score_text.get_width() + 20
    panel_height = score_text.get_height() + 10
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 100))  # Very transparent black
    
    # Add the panel and score
    screen.blit(panel, (SCREEN_WIDTH - panel_width - 10, 10))
    screen.blit(score_shadow, (SCREEN_WIDTH - panel_width - 10 + 11, 11 + 5))
    screen.blit(score_text, (SCREEN_WIDTH - panel_width - 10 + 10, 10 + 5))
    
    return panel_height  # Return the height for positioning other UI elements

def show_game_over(score):
    # Create a semi-transparent panel for the game over UI
    panel_width = 400
    panel_height = 200
    panel_x = (SCREEN_WIDTH - panel_width) // 2
    panel_y = (SCREEN_HEIGHT - panel_height) // 2
    
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 150))  # Semi-transparent black
    
    # Create a border for the panel
    border_width = 2
    pygame.draw.rect(panel, (255, 255, 255, 100), (border_width, border_width, 
                                                  panel_width - 2*border_width, 
                                                  panel_height - 2*border_width), 
                    border_width)
    
    # Add the panel to the screen
    screen.blit(panel, (panel_x, panel_y))
    
    # Create fonts for the game over screen
    title_font = pygame.font.SysFont('Arial', 48, bold=True)
    regular_font = pygame.font.SysFont('Arial', 24)
    
    # Render text with a subtle shadow effect
    title_shadow = title_font.render("GAME OVER", True, (20, 20, 20))
    title_text = title_font.render("GAME OVER", True, (255, 100, 100))  # Red color
    
    score_shadow = regular_font.render(f"Final Score: {score}", True, (20, 20, 20))
    score_text = regular_font.render(f"Final Score: {score}", True, WHITE)
    
    restart_shadow = regular_font.render("Press SPACE to restart", True, (20, 20, 20))
    restart_text = regular_font.render("Press SPACE to restart", True, WHITE)
    
    # Position text
    title_y = panel_y + 40
    score_y = panel_y + 110
    restart_y = panel_y + 150
    
    # Draw text shadows (slightly offset)
    screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 2, title_y + 2))
    screen.blit(score_shadow, (SCREEN_WIDTH // 2 - score_shadow.get_width() // 2 + 1, score_y + 1))
    screen.blit(restart_shadow, (SCREEN_WIDTH // 2 - restart_shadow.get_width() // 2 + 1, restart_y + 1))
    
    # Draw main text
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, title_y))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, score_y))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, restart_y))
def check_collision(player, obstacle):
    # Special case for holes - player falls in if they're not jumping over it
    if hasattr(obstacle, 'is_hole') and obstacle.is_hole:
        # Check if player is above the hole (horizontally aligned)
        if (player.x + player.radius > obstacle.x + 5 and 
            player.x - player.radius < obstacle.x + obstacle.width - 5):  # Slightly reduced collision area
            # Check if player is not jumping high enough
            if player.y + player.radius >= obstacle.y:
                player.falling = True  # Set falling state
                return True
        return False
    
    # Use circle collision for player
    player_center = (player.x, player.y)
    
    # Create rectangle for obstacle
    obstacle_rect = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
    
    # Calculate closest point on rectangle to circle center
    closest_x = max(obstacle_rect.left, min(player_center[0], obstacle_rect.right))
    closest_y = max(obstacle_rect.top, min(player_center[1], obstacle_rect.bottom))
    
    # Calculate distance between closest point and circle center
    distance_x = player_center[0] - closest_x
    distance_y = player_center[1] - closest_y
    distance = (distance_x ** 2 + distance_y ** 2) ** 0.5
    
    # Collision if distance is less than circle radius
    return distance < player.radius

def game_loop():
    player = Player()
    global obstacles, mountains, cherry_blossoms
    obstacles = []
    score = 0
    game_speed = 5  # Starting speed
    max_game_speed = 15  # Maximum speed cap
    obstacle_timer = 0
    obstacle_frequency = 1500  # milliseconds
    game_over = False
    
    # Create initial clouds
    clouds = [Cloud() for _ in range(4)]
    cloud_spawn_timer = 0
    
    # Create mountains in layers
    mountains = []
    for layer in range(3):  # 3 layers of mountains
        for _ in range(3):  # 3 mountains per layer
            mountains.append(Mountain(layer))
    
    # Create cherry blossoms
    cherry_blossoms = [CherryBlossom() for _ in range(30)]
    
    # Generate random grass positions for static grass
    grass_positions = [(x, random.randint(-2, 3)) for x in range(0, SCREEN_WIDTH, 10)]
    
    # Ground texture positions
    global ground_patches
    ground_patches = []
    for _ in range(20):
        patch_x = random.randint(0, SCREEN_WIDTH)
        patch_y = SCREEN_HEIGHT - GROUND_HEIGHT + random.randint(10, GROUND_HEIGHT - 5)
        patch_size = random.randint(3, 8)
        patch_color = (101, 67, 33) if random.random() > 0.5 else (85, 107, 47)
        ground_patches.append((patch_x, patch_y, patch_size, patch_color))
    
    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Restart game
                        return
                    else:
                        player.jump()
                elif event.key == pygame.K_DOWN:
                    player.duck()
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    player.stop_duck()
        
        # Fill background with sky color
        screen.fill(BLUE)
        
        # Draw background elements (mountains, clouds, cherry blossoms)
        draw_background(game_speed)
        
        # Update and draw clouds
        for cloud in clouds[:]:
            cloud.update()
            cloud.draw(screen)
            
            if cloud.is_off_screen():
                clouds.remove(cloud)
        
        # Spawn new clouds occasionally
        cloud_spawn_timer += 1
        if cloud_spawn_timer > 120:  # Every ~2 seconds at 60 FPS
            if random.random() < 0.3:  # 30% chance to spawn a cloud
                clouds.append(Cloud())
            cloud_spawn_timer = 0
        
        # Draw ground
        draw_ground()
        
        if not game_over:
            # Update player
            player.update()
            
            # Generate obstacles
            current_time = pygame.time.get_ticks()
            if current_time - obstacle_timer > obstacle_frequency:
                obstacles.append(Obstacle(game_speed))
                obstacle_timer = current_time
                # Gradually decrease obstacle frequency (increase difficulty)
                obstacle_frequency = max(1000, obstacle_frequency - 10)
            
            # Update and draw obstacles
            for obstacle in obstacles[:]:
                obstacle.update()
                obstacle.draw(screen)
                
                # Remove off-screen obstacles
                if obstacle.is_off_screen():
                    obstacles.remove(obstacle)
                
                # Check for collision
                if check_collision(player, obstacle):
                    game_over = True
                    # If player fell in a hole, animate falling
                    if hasattr(obstacle, 'is_hole') and obstacle.is_hole:
                        fall_animation(player, obstacle)
            
            # Draw player
            player.draw(screen)
            
        # Update score
            score += 1
            score_panel_height = show_score(score)
            
            # Increase game speed gradually based on score
            # More frequent small increases for smoother acceleration
            if score % 200 == 0 and game_speed < max_game_speed:
                game_speed += 0.1
                # Also adjust player jump power to match increased speed
                player.jump_power = min(-18, player.jump_power - 0.05)
                
            # Display current speed (optional)
            speed_font = pygame.font.SysFont('Arial', 20)
            speed_shadow = speed_font.render(f"Speed: {game_speed:.1f}", True, (20, 20, 20))
            speed_text = speed_font.render(f"Speed: {game_speed:.1f}", True, WHITE)
            
            # Create a small panel for the speed
            panel_width = speed_text.get_width() + 20
            panel_height = speed_text.get_height() + 10
            panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel.fill((0, 0, 0, 100))  # Very transparent black
            
            # Add the panel and speed
            screen.blit(panel, (10, 10))
            screen.blit(speed_shadow, (11 + 10, 11 + 5))
            screen.blit(speed_text, (10 + 10, 10 + 5))
                
            # Shift grass positions based on game speed (slower than obstacles)
            ground_speed = game_speed * 0.6  # Reduce ground movement speed to 60% of game speed
            grass_positions = [(x - ground_speed, h) for x, h in grass_positions]
            # Add new grass when needed
            while grass_positions and grass_positions[0][0] < 0:
                grass_positions.pop(0)
            while grass_positions[-1][0] < SCREEN_WIDTH:
                new_x = grass_positions[-1][0] + 10
                grass_positions.append((new_x, random.randint(-2, 3)))
            
            # Update ground patches
            ground_patches = [(x - ground_speed, y, size, color) for x, y, size, color in ground_patches]
            # Replace off-screen patches
            for i, (x, y, size, color) in enumerate(ground_patches):
                if x < -size:
                    patch_x = SCREEN_WIDTH + random.randint(0, 50)
                    patch_y = SCREEN_HEIGHT - GROUND_HEIGHT + random.randint(10, GROUND_HEIGHT - 5)
                    patch_size = random.randint(3, 8)
                    patch_color = (101, 67, 33) if random.random() > 0.5 else (85, 107, 47)
                    ground_patches[i] = (patch_x, patch_y, patch_size, patch_color)
                
        else:
            # Draw player and obstacles in their last positions
            for obstacle in obstacles:
                obstacle.draw(screen)
            
            # Show game over screen
            show_game_over(score)
        
        pygame.display.update()
        clock.tick(FPS)
def fall_animation(player, hole):
    # Animate player falling into the hole with realistic physics
    gravity = 0.5  # Gravity acceleration for falling
    fall_velocity = 0  # Initial fall velocity
    max_fall_velocity = 10  # Terminal velocity
    fall_duration = 60  # How many frames to animate
    rotation_speed = 5  # How fast the ball rotates while falling
    
    # Store original position
    original_x = player.x
    original_y = player.y
    
    # Calculate center of hole
    hole_center_x = hole.x + hole.width / 2
    
    # Move player toward center of hole as it falls
    x_move_direction = 1 if hole_center_x > original_x else -1
    x_move_speed = min(2, abs(hole_center_x - original_x) / 20)
    
    # Get current clouds
    current_clouds = [Cloud() for _ in range(4)]
    for cloud in current_clouds:
        cloud.x = random.randint(0, SCREEN_WIDTH)
    
    # Generate grass positions for the animation
    grass_positions = [(x, random.randint(-2, 3)) for x in range(0, SCREEN_WIDTH, 10)]
    
    # Keep cherry blossoms and mountains for animation
    current_blossoms = cherry_blossoms.copy()
    
    for frame in range(fall_duration):
        # Clear screen
        screen.fill(BLUE)
        
        # Draw mountains
        for mountain in mountains:
            mountain.draw(screen)
        
        # Draw clouds
        for cloud in current_clouds:
            cloud.draw(screen)
        
        # Draw cherry blossoms
        for blossom in current_blossoms:
            blossom.update()
            blossom.draw(screen)
        
        draw_ground()
        
        # Draw all obstacles
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        # Update fall velocity with gravity (accelerating)
        fall_velocity = min(fall_velocity + gravity, max_fall_velocity)
        
        # Update player position (falling)
        player.y += fall_velocity
        
        # Move player toward center of hole
        if abs(player.x - hole_center_x) > x_move_speed:
            player.x += x_move_speed * x_move_direction
        
        # Rotate the player as it falls
        player.rotation += rotation_speed
        
        # Make the player appear to get smaller as it falls deeper
        if frame > fall_duration / 2:
            shrink_factor = 1 - (frame - fall_duration/2) / (fall_duration/2) * 0.7
            player.radius = player.normal_radius * shrink_factor
        
        # Draw player
        player.draw(screen)
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)
        
        # Add a small delay to make the animation more visible
        pygame.time.delay(10)

def main():
    # Show start screen with aesthetic UI
    screen.fill(BLUE)
    
    # Create mountains for start screen
    start_mountains = []
    for layer in range(3):  # 3 layers of mountains
        for _ in range(3):  # 3 mountains per layer
            start_mountains.append(Mountain(layer))
    
    # Draw mountains
    for mountain in start_mountains:
        mountain.draw(screen)
    
    # Create some clouds for the start screen
    start_clouds = [Cloud() for _ in range(5)]
    for cloud in start_clouds:
        cloud.x = random.randint(50, SCREEN_WIDTH - 100)  # Position clouds across the screen
        cloud.draw(screen)
    
    # Create cherry blossoms for start screen
    start_blossoms = [CherryBlossom() for _ in range(20)]
    for blossom in start_blossoms:
        blossom.draw(screen)
    
    # Need to initialize obstacles as empty for the first draw_ground call
    global obstacles, ground_patches
    obstacles = []
    
    # Initialize ground patches for the start screen
    ground_patches = []
    for _ in range(20):
        patch_x = random.randint(0, SCREEN_WIDTH)
        patch_y = SCREEN_HEIGHT - GROUND_HEIGHT + random.randint(10, GROUND_HEIGHT - 5)
        patch_size = random.randint(3, 8)
        patch_color = (101, 67, 33) if random.random() > 0.5 else (85, 107, 47)
        ground_patches.append((patch_x, patch_y, patch_size, patch_color))
    
    draw_ground()
    
    # Create a semi-transparent panel for the UI
    panel_width = 400
    panel_height = 200
    panel_x = (SCREEN_WIDTH - panel_width) // 2
    panel_y = (SCREEN_HEIGHT - panel_height) // 2
    
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 150))  # Semi-transparent black
    
    # Create a border for the panel
    border_width = 2
    pygame.draw.rect(panel, (255, 255, 255, 100), (border_width, border_width, 
                                                  panel_width - 2*border_width, 
                                                  panel_height - 2*border_width), 
                    border_width)
    
    # Add the panel to the screen
    screen.blit(panel, (panel_x, panel_y))
    
    # Create a larger, more elegant font for the title
    title_font = pygame.font.SysFont('Arial', 48, bold=True)
    regular_font = pygame.font.SysFont('Arial', 24)
    
    # Render text with a subtle shadow effect
    title_shadow = title_font.render("CHERRY RUNNER", True, (20, 20, 20))
    title_text = title_font.render("CHERRY RUNNER", True, (255, 223, 228))  # Cherry blossom color
    
    start_shadow = regular_font.render("Press SPACE to start", True, (20, 20, 20))
    start_text = regular_font.render("Press SPACE to start", True, WHITE)
    
    controls_shadow = regular_font.render("SPACE to jump, DOWN to duck", True, (20, 20, 20))
    controls_text = regular_font.render("SPACE to jump, DOWN to duck", True, WHITE)
    
    # Position text
    title_y = panel_y + 40
    start_y = panel_y + 110
    controls_y = panel_y + 150
    
    # Draw text shadows (slightly offset)
    screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 2, title_y + 2))
    screen.blit(start_shadow, (SCREEN_WIDTH // 2 - start_shadow.get_width() // 2 + 1, start_y + 1))
    screen.blit(controls_shadow, (SCREEN_WIDTH // 2 - controls_shadow.get_width() // 2 + 1, controls_y + 1))
    
    # Draw main text
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, title_y))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, start_y))
    screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, controls_y))
    
    # Add a small animated ball as a visual element
    ball_radius = 15
    ball_x = SCREEN_WIDTH // 2
    ball_y = panel_y + panel_height + 30
    
    # Draw a shadow under the ball
    pygame.draw.ellipse(screen, (20, 20, 20, 150), 
                      (ball_x - ball_radius + 5, ball_y + ball_radius - 5, 
                       ball_radius * 2, ball_radius // 2))
    
    # Draw the ball
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)
    
    # Add a line to show rotation
    line_end_x = ball_x + ball_radius * 0.8 * math.cos(pygame.time.get_ticks() * 0.005)
    line_end_y = ball_y + ball_radius * 0.8 * math.sin(pygame.time.get_ticks() * 0.005)
    pygame.draw.line(screen, BLACK, (ball_x, ball_y), (line_end_x, line_end_y), 3)
    
    pygame.display.update()
    
    # Animate the start screen
    start_time = pygame.time.get_ticks()
    
    # Wait for player to start game
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        
        # Every 100ms, update the animation
        if elapsed_time % 100 < 20:
            # Update cherry blossoms
            for blossom in start_blossoms:
                blossom.update()
            
            # Redraw the screen
            screen.fill(BLUE)
            
            # Draw mountains
            for mountain in start_mountains:
                mountain.draw(screen)
            
            # Draw clouds
            for cloud in start_clouds:
                cloud.draw(screen)
            
            # Draw cherry blossoms
            for blossom in start_blossoms:
                blossom.draw(screen)
            
            draw_ground()
            
            # Add the panel to the screen
            screen.blit(panel, (panel_x, panel_y))
            
            # Draw text shadows
            screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_shadow.get_width() // 2 + 2, title_y + 2))
            screen.blit(start_shadow, (SCREEN_WIDTH // 2 - start_shadow.get_width() // 2 + 1, start_y + 1))
            screen.blit(controls_shadow, (SCREEN_WIDTH // 2 - controls_shadow.get_width() // 2 + 1, controls_y + 1))
            
            # Draw main text
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, title_y))
            screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, start_y))
            screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, controls_y))
            
            # Update ball position for a subtle bounce effect
            bounce_offset = math.sin(elapsed_time * 0.005) * 5
            ball_y_pos = ball_y + bounce_offset
            
            # Draw a shadow under the ball
            shadow_width = ball_radius * 2 - abs(bounce_offset)
            pygame.draw.ellipse(screen, (20, 20, 20, 150), 
                              (ball_x - shadow_width//2, ball_y + ball_radius - 5, 
                               shadow_width, ball_radius // 2))
            
            # Draw the ball
            pygame.draw.circle(screen, RED, (ball_x, ball_y_pos), ball_radius)
            
            # Add a line to show rotation
            rotation = elapsed_time * 0.005
            line_end_x = ball_x + ball_radius * 0.8 * math.cos(rotation)
            line_end_y = ball_y_pos + ball_radius * 0.8 * math.sin(rotation)
            pygame.draw.line(screen, BLACK, (ball_x, ball_y_pos), (line_end_x, line_end_y), 3)
            
            pygame.display.update()
        
        clock.tick(FPS)
    
    # Start game loop
    while True:
        game_loop()

if __name__ == "__main__":
    main()
