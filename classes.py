import pygame
import math

class Tower:
    def __init__(self, position, range, damage, fire_rate):
        self.position = position # a rect
        self.range = range
        self.damage = damage
        self.fire_rate = fire_rate

    def upgrade(self):
        self.range += 10
        self.damage += 5
        self.fire_rate *= 0.9

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 0, 255), self.position)


class Path:
    """A simple polyline path defined by a list of (x, y) waypoints.

    Points are stored as tuples of floats: (x, y).
    """
    def __init__(self, points):
        if not points or len(points) < 2:
            raise ValueError("Path requires at least two points")
        # normalize to tuples of floats
        self.points = [(float(p[0]), float(p[1])) for p in points]


class Enemy:
    def __init__(self, path: Path, speed=2.0, radius=10, color=(200, 40, 40)):
        """speed is interpreted as pixels per frame (not per second)."""
        self.path = path
        self.pos = [self.path.points[0][0], self.path.points[0][1]]
        self.current_wp = 1 # current waypoint focus
        self.speed = float(speed)  # pixels per frame
        self.radius = radius
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

    def is_alive(self):
        return not self.reached_end