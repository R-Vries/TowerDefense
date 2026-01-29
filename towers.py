import pygame
import math

class Tower:
    def __init__(self, position, range, damage, fire_rate, color=(120, 120, 120)):
        self.position = position # a pygame.Rect
        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate
        self.color = color
        self.time_since_last_shot = 0  # frames since last shot

    def upgrade(self):
        self.range += 10
        self.damage += 5
        self.fire_rate *= 0.9

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.position)

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


class BlueTower(Tower):
    """A specific tower type (blue)."""
    def __init__(self, center_pos, range=100, damage=20, fire_rate=1.0, size=40):
        rect = pygame.Rect(0, 0, size, size)
        rect.center = (int(center_pos[0]), int(center_pos[1]))
        super().__init__(rect, range, damage, fire_rate, color=(0, 0, 255))

    # Inherit draw from Tower (blue rect). Additional behavior can be added later.


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
        pygame.draw.circle(screen, (255, 255, 0), (int(self.pos[0]), int(self.pos[1])), self.radius)

    def is_active(self):
        """Returns True if projectile is still in flight and hasn't hit."""
        return not self.has_hit