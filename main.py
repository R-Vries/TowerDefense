import pygame
from classes import *
from towers import *

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()

# sidebar area
sidebar = pygame.Rect(650, 0, 150, 600)

# palette icon inside sidebar for BlueTower
palette_icon_rect = pygame.Rect(sidebar.left + 10, 20, 50, 50)

# placed towers
towers = []

# projectiles
projectiles = []

# dragging state
dragging = False
drag_type = None
drag_pos = (0, 0)

# Define a path as straight-line waypoints (avoid the sidebar area on the right)
path_points = [(50, 300), (300, 300), (300, 150), (600, 150)]
path = Path(path_points)

# Enemy management
enemies = []
spawn_interval = 1500  # milliseconds between spawns
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, spawn_interval)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_EVENT:
            # speed is pixels per frame; choose ~2-3 for smooth movement at 60 FPS
            enemies.append(Enemy(path, speed=2.5))
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # start dragging if clicked the palette icon
            if palette_icon_rect.collidepoint(mx, my):
                dragging = True
                drag_type = 'blue'
                drag_pos = (mx, my)
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                drag_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging:
                mx, my = event.pos
                # only allow placement outside sidebar
                if mx < sidebar.left:
                    if drag_type == 'blue':
                        towers.append(BlueTower((mx, my)))
                # stop dragging regardless
                dragging = False
                drag_type = None

    # update enemies (frame-based)
    for e in enemies:
        e.update()
    enemies = [e for e in enemies if e.is_alive()]

    # update towers and collect projectiles
    for tower in towers:
        new_projectiles = tower.update(enemies)
        projectiles.extend(new_projectiles)

    # update projectiles
    for projectile in projectiles:
        projectile.update()
    projectiles = [p for p in projectiles if p.is_active()]

    # draw
    screen.fill((255, 255, 255))

    path.draw(screen)

    # draw towers
    for tw in towers:
        tw.draw(screen)

    # draw projectiles
    for proj in projectiles:
        proj.draw(screen)

    # draw enemies
    for e in enemies:
        e.draw(screen)

    # sidebar
    pygame.draw.rect(screen, (200, 200, 200), sidebar)
    # draw palette icon (blue tower sample)
    pygame.draw.rect(screen, (180, 180, 180), palette_icon_rect)
    # draw a small blue tower in the icon
    sample_rect = pygame.Rect(0, 0, 36, 36)
    sample_rect.center = palette_icon_rect.center
    pygame.draw.rect(screen, (0, 0, 255), sample_rect)

    # draw dragging preview
    if dragging and drag_type == 'blue':
        mx, my = drag_pos
        preview_rect = pygame.Rect(0, 0, 40, 40)
        preview_rect.center = (mx, my)
        # semi-transparent preview: draw with a border and transparent fill not directly supported,
        # so draw a filled rect with lighter color and a black border
        pygame.draw.rect(screen, (100, 100, 255), preview_rect)
        pygame.draw.rect(screen, (0, 0, 0), preview_rect, 2)

    pygame.display.flip()

pygame.quit()