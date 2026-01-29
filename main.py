import pygame
from classes import *
from towers import *
from images import *

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()

# sidebar area
sidebar = pygame.Rect(650, 0, 150, 600)

# Tower types available for placement
TOWER_TYPES = {
    'piper': {
        'class': Piper,
        'image': piper_image,
        'rect': pygame.Rect(sidebar.left + 10, sidebar.top + 60, 50, 50),
    },
    'spike': {
        'class': Spike,
        'image': spike_image,
        'rect': pygame.Rect(sidebar.left + 10, sidebar.top + 130, 50, 50),
    },
}

# placed towers
towers = []

# projectiles
projectiles = []

# dragging state
dragging = False
dragging_tower_type = None
drag_pos = (0, 0)

# Define a path as straight-line waypoints (avoid the sidebar area on the right)
path_points = [(50, 300), (300, 300), (300, 150), (600, 150)]
path = Path(path_points)

# Enemy management
enemies = []
spawn_interval = 1500  # milliseconds between spawns
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, spawn_interval)

# Health counter
health = 20

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
            # Check if clicked on any tower icon in the sidebar
            for tower_type, tower_data in TOWER_TYPES.items():
                if tower_data['rect'].collidepoint(mx, my):
                    dragging = True
                    dragging_tower_type = tower_type
                    drag_pos = (mx, my)
                    break
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                drag_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if dragging:
                mx, my = event.pos
                # only allow placement outside sidebar
                if mx < sidebar.left:
                    tower_class = TOWER_TYPES[dragging_tower_type]['class']
                    towers.append(tower_class((mx, my)))
                # stop dragging regardless
                dragging = False
                dragging_tower_type = None

    # update enemies (frame-based)
    for e in enemies:
        e.update()
    
    # check for enemies that reached the end
    for e in enemies:
        if e.reached_end and e.health > 0:
            health -= 1
            e.health = 0  # prevent multiple health loss from same enemy
    
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
    
    # draw health counter
    font = pygame.font.Font(None, 36)
    health_text = font.render(f"Health: {health}", True, (0, 0, 0))
    screen.blit(health_text, (sidebar.left + 10, 10))
    
    # draw tower palette icons
    for tower_type, tower_data in TOWER_TYPES.items():
        screen.blit(tower_data['image'], tower_data['rect'])

    # draw dragging preview
    if dragging and dragging_tower_type:
        mx, my = drag_pos
        tower_image = TOWER_TYPES[dragging_tower_type]['image']
        preview_rect = tower_image.get_rect(center=(mx, my))
        screen.blit(tower_image, preview_rect)

    pygame.display.flip()

pygame.quit()