import pygame
from classes import *
from towers import *
from images import *

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Tower Defense")

clock = pygame.time.Clock()

# Game states
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"

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

# Start button
start_button = pygame.Rect(300, 250, 200, 100)

def draw_menu():
    """Draw the main menu screen."""
    screen.fill((255, 255, 255))
    
    font_title = pygame.font.Font(None, 72)
    font_button = pygame.font.Font(None, 48)
    
    title_text = font_title.render("Tower Defense", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(400, 100))
    screen.blit(title_text, title_rect)
    
    # Draw start button
    pygame.draw.rect(screen, (100, 200, 100), start_button)
    pygame.draw.rect(screen, (0, 0, 0), start_button, 3)
    
    button_text = font_button.render("START", True, (0, 0, 0))
    button_text_rect = button_text.get_rect(center=start_button.center)
    screen.blit(button_text, button_text_rect)
    
    pygame.display.flip()

def draw_game_over(final_health):
    """Draw the game over screen."""
    screen.fill((255, 255, 255))
    
    font_title = pygame.font.Font(None, 72)
    font_subtitle = pygame.font.Font(None, 48)
    
    title_text = font_title.render("GAME OVER", True, (200, 0, 0))
    title_rect = title_text.get_rect(center=(400, 150))
    screen.blit(title_text, title_rect)
    
    # Draw start button (to return to menu)
    pygame.draw.rect(screen, (100, 200, 100), start_button)
    pygame.draw.rect(screen, (0, 0, 0), start_button, 3)
    
    button_text = font_subtitle.render("PLAY AGAIN", True, (0, 0, 0))
    button_text_rect = button_text.get_rect(center=start_button.center)
    screen.blit(button_text, button_text_rect)
    
    pygame.display.flip()

def init_game():
    """Initialize game variables."""
    return {
        'towers': [],
        'projectiles': [],
        'enemies': [],
        'dragging': False,
        'dragging_tower_type': None,
        'drag_pos': (0, 0),
        'health': 20,
        'path': Path([(50, 300), (300, 300), (300, 150), (600, 150)]),
    }

def draw_game_objects(game_data):
    """Draw path, towers, projectiles and enemies."""
    # path
    game_data['path'].draw(screen)

    # draw towers
    for tw in game_data['towers']:
        tw.draw(screen)

    # draw projectiles
    for proj in game_data['projectiles']:
        proj.draw(screen)

    # draw enemies
    for e in game_data['enemies']:
        e.draw(screen)

# Game state
current_state = MENU
game_data = init_game()

SPAWN_EVENT = pygame.USEREVENT + 1

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif current_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if start_button.collidepoint(mx, my):
                    current_state = PLAYING
                    game_data = init_game()
                    pygame.time.set_timer(SPAWN_EVENT, 1500)
        elif current_state == GAME_OVER:
            pygame.time.set_timer(SPAWN_EVENT, 0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if start_button.collidepoint(mx, my):
                    current_state = PLAYING
                    game_data = init_game()
                    pygame.time.set_timer(SPAWN_EVENT, 1500)
        elif current_state == PLAYING:
            if event.type == SPAWN_EVENT:
                # speed is pixels per frame; choose ~2-3 for smooth movement at 60 FPS
                game_data['enemies'].append(Enemy(game_data['path'], speed=2.5))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Check if clicked on any tower icon in the sidebar
                for tower_type, tower_data in TOWER_TYPES.items():
                    if tower_data['rect'].collidepoint(mx, my):
                        game_data['dragging'] = True
                        game_data['dragging_tower_type'] = tower_type
                        game_data['drag_pos'] = (mx, my)
                        break
            elif event.type == pygame.MOUSEMOTION:
                if game_data['dragging']:
                    game_data['drag_pos'] = event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if game_data['dragging']:
                    mx, my = event.pos
                    # only allow placement outside sidebar
                    if mx < sidebar.left:
                        tower_class = TOWER_TYPES[game_data['dragging_tower_type']]['class']
                        game_data['towers'].append(tower_class((mx, my)))
                    # stop dragging regardless
                    game_data['dragging'] = False
                    game_data['dragging_tower_type'] = None

    if current_state == MENU:
        draw_menu()
    elif current_state == GAME_OVER:
        draw_game_over(game_data['health'])
    elif current_state == PLAYING:
        # update enemies (frame-based)
        for e in game_data['enemies']:
            e.update()
        
        # check for enemies that reached the end
        for e in game_data['enemies']:
            if e.reached_end and e.health > 0:
                game_data['health'] -= 1
                e.health = 0  # prevent multiple health loss from same enemy
        
        game_data['enemies'] = [e for e in game_data['enemies'] if e.is_alive()]

        # Check if health dropped to 0 or below
        if game_data['health'] <= 0:
            current_state = GAME_OVER
            pygame.time.set_timer(SPAWN_EVENT, 0)

        # update towers and collect projectiles
        for tower in game_data['towers']:
            new_projectiles = tower.update(game_data['enemies'])
            game_data['projectiles'].extend(new_projectiles)

        # update projectiles
        for projectile in game_data['projectiles']:
            projectile.update()
        game_data['projectiles'] = [p for p in game_data['projectiles'] if p.is_active()]

        # draw
        screen.fill((255, 255, 255))

        draw_game_objects(game_data)

        # sidebar
        pygame.draw.rect(screen, (200, 200, 200), sidebar)
        
        # draw health counter
        font = pygame.font.Font(None, 36)
        health_text = font.render(f"Health: {game_data['health']}", True, (0, 0, 0))
        screen.blit(health_text, (sidebar.left + 10, 10))
        
        # draw tower palette icons
        for tower_type, tower_data in TOWER_TYPES.items():
            screen.blit(tower_data['image'], tower_data['rect'])

        # draw dragging preview
        if game_data['dragging'] and game_data['dragging_tower_type']:
            mx, my = game_data['drag_pos']
            tower_image = TOWER_TYPES[game_data['dragging_tower_type']]['image']
            preview_rect = tower_image.get_rect(center=(mx, my))
            screen.blit(tower_image, preview_rect)

        pygame.display.flip()

pygame.quit()