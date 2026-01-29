import pygame
from classes import *

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()
t1 = Tower(pygame.Rect(100, 100, 50, 50), range=100, damage=20, fire_rate=1.0)

sidebar = pygame.Rect(650, 0, 150, 600)

# Define a path as straight-line waypoints (avoid the sidebar area on the right)
path_points = [(50, 300), (300, 300), (300, 150), (600, 150)]
path = Path(path_points)

# Enemy management
enemies = []
spawn_interval = 1500  # milliseconds between spawns
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, spawn_interval)

def draw_path(screen, path):
    # draw path (polyline)
    pygame.draw.lines(screen, (0, 180, 0), False, [(int(p[0]), int(p[1])) for p in path.points], 6)
    # draw start and end markers
    pygame.draw.circle(screen, (0, 0, 0), (int(path.points[0][0]), int(path.points[0][1])), 6)
    pygame.draw.circle(screen, (0, 0, 0), (int(path.points[-1][0]), int(path.points[-1][1])), 6)


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_EVENT:
            # speed is pixels per frame; choose ~2-3 for smooth movement at 60 FPS
            enemies.append(Enemy(path, speed=2.5))

    # update enemies (frame-based)
    for e in enemies:
        e.update()
    enemies = [e for e in enemies if e.is_alive()]

    # draw
    screen.fill((255, 255, 255))

    draw_path(screen, path)

    # draw enemies
    for e in enemies:
        e.draw(screen)

    # draw tower
    t1.draw(screen)

    # sidebar
    pygame.draw.rect(screen, (200, 200, 200), sidebar)

    pygame.display.flip()

pygame.quit()