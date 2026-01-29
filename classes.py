import pygame
import math

class Path:
    """A simple polyline path defined by a list of (x, y) waypoints.

    Points are stored as tuples of floats: (x, y).
    """
    def __init__(self, points):
        if not points or len(points) < 2:
            raise ValueError("Path requires at least two points")
        # normalize to tuples of floats
        self.points = [(float(p[0]), float(p[1])) for p in points]

    def draw(self, screen):
        # draw path (polyline)
        pygame.draw.lines(screen, (0, 180, 0), False, [(int(p[0]), int(p[1])) for p in self.points], 6)
        # draw start and end markers
        pygame.draw.circle(screen, (0, 0, 0), (int(self.points[0][0]), int(self.points[0][1])), 6)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.points[-1][0]), int(self.points[-1][1])), 6)


class Enemy:
    def __init__(self, path: Path, speed=2.0, radius=10, health=100, color=(200, 40, 40)):
        """speed is interpreted as pixels per frame (not per second)."""
        self.path = path
        self.pos = [self.path.points[0][0], self.path.points[0][1]]
        self.current_wp = 1 # current waypoint focus
        self.speed = float(speed)  # pixels per frame
        self.radius = radius
        self.health = health
        self.max_health = health
        self.color = color
        self.reached_end = False

    def update(self):
        """Move the enemy along the path by a fixed amount each frame."""
        if self.reached_end:
            return
        if self.current_wp >= len(self.path.points):
            self.reached_end = True
            return

        # target x, target y  
        tx, ty = self.path.points[self.current_wp]
        dx = tx - self.pos[0]
        dy = ty - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.current_wp += 1
            if self.current_wp >= len(self.path.points):
                self.reached_end = True
            return

        step = self.speed
        if step >= dist:
            # snap to waypoint and advance
            self.pos[0] = tx
            self.pos[1] = ty
            self.current_wp += 1
            if self.current_wp >= len(self.path.points):
                self.reached_end = True
        else:
            nx = dx / dist
            ny = dy / dist
            self.pos[0] += nx * step
            self.pos[1] += ny * step

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        
        # Draw health bar above enemy
        if self.health < self.max_health:
            bar_width = 20
            bar_height = 4
            bar_x = int(self.pos[0]) - bar_width // 2
            bar_y = int(self.pos[1]) - self.radius - 8
            
            # Background (red)
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Health (green)
            health_ratio = self.health / self.max_health
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, int(bar_width * health_ratio), bar_height))

    def take_damage(self, damage):
        """Reduce health by damage amount."""
        self.health -= damage
        if self.health <= 0:
            self.reached_end = True

    def is_alive(self):
        return not self.reached_end and self.health > 0