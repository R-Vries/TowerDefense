import pygame
import math
from images import *


class Tower:
    def __init__(self, position, range, damage, fire_rate, image):
        self.position = position  # a pygame.Rect
        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate
        self.time_since_last_shot = 0  # frames since last shot
        self.image = image

    def upgrade(self):
        self.range += 10
        self.damage += 5
        self.fire_rate *= 0.9

    def draw(self, screen):
        screen.blit(self.image, self.position)

    def update(self, enemies):
        """Update tower state and return list of projectiles fired."""
        self.time_since_last_shot += 1
        projectiles = []
        
        # Find enemies in range
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            
            # Calculate distance to enemy
            dx = enemy.pos[0] - self.position.centerx
            dy = enemy.pos[1] - self.position.centery
            distance = math.hypot(dx, dy)
            
            # If enemy is in range and enough time has passed, fire
            if distance <= self.range and self.time_since_last_shot >= 60 / self.fire_rate:
                projectile = Projectile(
                    (self.position.centerx, self.position.centery),
                    enemy,
                    self.damage
                )
                projectiles.append(projectile)
                self.time_since_last_shot = 0
        
        return projectiles


class Piper(Tower):
    """Piper has slow reload and deals a lot of damage.""" 

    size = (40, 40)
    image = pygame.transform.scale(piper_image, size)
      
    def __init__(self, center_pos):
        rect = pygame.Rect(0, 0, 40, 40)
        rect.center = (int(center_pos[0]), int(center_pos[1]))
        image = piper_image
        image = pygame.transform.scale(image, self.size)
        super().__init__(rect, 100, 20, 1.0, image)


class Spike(Tower):
    """Spike has fast reload and deals moderate damage."""
    
    size = (40, 40)
    image = pygame.transform.scale(spike_image, size)
    
    def __init__(self, center_pos):
        rect = pygame.Rect(0, 0, 40, 40)
        rect.center = (int(center_pos[0]), int(center_pos[1]))
        image = spike_image
        image = pygame.transform.scale(image, self.size)
        super().__init__(rect, 80, 10, 2.0, image)


class Projectile:
    """A projectile fired by a tower that travels to its target."""
    def __init__(self, position, target, damage, speed=7):
        self.pos = list(position)
        self.target = target  # Reference to the target enemy
        self.damage = damage
        self.speed = speed  # pixels per frame
        self.has_hit = False
        self.radius = 3

    def update(self):
        """Move projectile towards target."""
        if self.has_hit:
            return
        
        # Calculate direction to target
        dx = self.target.pos[0] - self.pos[0]
        dy = self.target.pos[1] - self.pos[1]
        distance = math.hypot(dx, dy)
        
        if distance == 0:
            # Projectile reached target (or very close)
            if self.target.is_alive():
                self.target.take_damage(self.damage)
            self.has_hit = True
            return
        
        # Move towards target
        step = self.speed
        if step >= distance:
            # Hit the target
            if self.target.is_alive():
                self.target.take_damage(self.damage)
            self.has_hit = True
        else:
            # Move one step towards target
            nx = dx / distance
            ny = dy / distance
            self.pos[0] += nx * step
            self.pos[1] += ny * step

    def draw(self, screen):
        """Draw the projectile as a small circle."""
        pygame.draw.circle(screen, (0, 0, 0), (int(self.pos[0]), int(self.pos[1])), self.radius)

    def is_active(self):
        """Returns True if projectile is still in flight and hasn't hit."""
        return not self.has_hit