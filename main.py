import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 1200, 900
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)

# Load PNG images and resize them
bg_image = pygame.image.load('Images/bg.png')
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

enemy_image = pygame.image.load('Images/Enemy.png')
enemy_image = pygame.transform.scale(enemy_image, (100, 100))  # Adjust size as needed

ship_upgrade_image = pygame.image.load('Images/ship_with_upgrade.png')
ship_upgrade_image = pygame.transform.scale(ship_upgrade_image, (100, 100))  # Adjust size as needed

ship_without_upgrade_image = pygame.image.load('Images/ship_without_upgrade.png')
ship_without_upgrade_image = pygame.transform.scale(ship_without_upgrade_image, (100, 100))  # Adjust size as needed

upgrade_image = pygame.image.load('Images/Upgrade.png')
upgrade_image = pygame.transform.scale(upgrade_image, (100, 100))  # Adjust size as needed

xp_image = pygame.image.load('Images/XP.png')
xp_image = pygame.transform.scale(xp_image, (100, 100))  # Adjust size as needed

# Sounds
gameOver = pygame.mixer.Sound('Sounds/game_over.mp3')
bulletShoot = pygame.mixer.Sound('Sounds/BulletShoot.mp3')
pickUpXpItem = pygame.mixer.Sound('Sounds/pickUpXpItem.mp3')
defetedEnemy = pygame.mixer.Sound('Sounds/defetedEnemy.mp3')
upgradeItemStart = pygame.mixer.Sound('Sounds/upgradeItem.mp3')
XpMinus = pygame.mixer.Sound('Sounds/XpMinus.mp3')
backgroundMusic = pygame.mixer.Sound('Sounds/BackgroundMusic.mp3')
enemyBulletShoot = pygame.mixer.Sound('Sounds/BulletShoot.mp3')  # Define enemy bullet shooting sound

# Set initial volume levels
volume_once = 0.8  # Example volume level for "once" sound
volume_sometimes = 0.5  # Example volume level for "sometimes" sound
background_volume = 0.3  # Adjust background music volume here

# Set volume for background music
backgroundMusic.set_volume(background_volume)

# Function to play sounds
def play_sound(sound):
    sound.play()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = ship_without_upgrade_image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.move_direction = 1
        self.move_counter = 0
        self.double_shooter = False
        self.upgraded = False
        self.upgrade_timer = 0
        self.score = 0
        self.health = 6

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.clamp_ip(window.get_rect())
        
        # Add slight back-and-forth movement
        self.move_counter += 1
        if self.move_counter % 20 == 0:
            self.move_direction *= -1
        self.rect.x += self.move_direction

        # Check if player is upgraded
        if self.upgraded:
            self.upgrade_timer += 1
            if self.upgrade_timer >= 900:  # 15 seconds (60 frames per second * 15)
                self.downgrade()
        
        # Update speed if player is upgraded
        if self.upgraded:
            self.speed = 8  # Increase speed when upgraded
        else:
            self.speed = 5  # Reset speed if not upgraded

    def upgrade(self):
        self.upgraded = True
        self.original_image = ship_upgrade_image
        self.image = self.original_image.copy()
        self.double_shooter = True
        self.upgrade_timer = 0

    def downgrade(self):
        self.upgraded = False
        self.original_image = ship_without_upgrade_image
        self.image = self.original_image.copy()
        self.double_shooter = False


    def shoot(self):
        if self.double_shooter:  # Double shoot when upgraded
            bullet1 = Bullet(self.rect.left, self.rect.top)
            bullet2 = Bullet(self.rect.right, self.rect.top)
            all_sprites.add(bullet1, bullet2)
            bullets.add(bullet1, bullet2)
        else:
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
        play_sound(bulletShoot)  # Play shooting sound

# Define the bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

# Define the enemy bullet class
class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(RED)  # Color of the enemy bullet
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 5  # Adjust speed as needed for enemy bullets

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

# Define the enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(1, 2)
        self.shoot_probability = 0.01  # Adjust this probability as needed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = -self.rect.height
            self.speed = random.randint(1, 2)
            
        if self.rect.top > HEIGHT:  # If enemy passes player's position
            play_sound(XpMinus)  # Play XP minus sound

        # Randomly decide whether to shoot
        if random.random() <= self.shoot_probability:
            self.shoot()

    def shoot(self):
        # Create a bullet shot by the enemy
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(bullet)
        enemy_bullets.add(bullet)
        play_sound(enemyBulletShoot)  # Play shooting sound

class UpgradeCube(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = upgrade_image  # Use the loaded Upgrade.png image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(4, 6)  # Increase speed to make it harder to get upgrades

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = -self.rect.height
            self.speed = random.randint(4, 6)  # Randomize speed to add variability in movement

# Define the XP triangle class
class XPTriangle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = xp_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = random.randint(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = -self.rect.height
            self.speed = random.randint(1, 3)

# Create sprite groups
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
upgrade_cubes = pygame.sprite.Group()
xp_triangles = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()  # Sprite group for enemy bullets

# Create player
player = Player()
all_sprites.add(player)

# Play background music
def play_background_music():
    backgroundMusic.play(-1)  # -1 loops the music indefinitely

play_background_music()

# Main game loop
running = True
clock = pygame.time.Clock()
spawn_counter = 0
upgrade_spawn_counter = 0
xp_triangle_spawn_counter = 0
upgrade_spawn_interval = 900  # Increase this value to make yellow upgrade cubes spawn less frequently
xp_triangle_spawn_interval = 900  # Increase this value to make XP triangles spawn less frequently

# Set up font for displaying score and health
font = pygame.font.Font(None, 36)

# Flag to indicate if the game is over
game_over = False

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.shoot()
            elif event.key == pygame.K_r and game_over:
                # Reset the game
                all_sprites.empty()
                bullets.empty()
                enemies.empty()
                upgrade_cubes.empty()
                xp_triangles.empty()
                player = Player()
                all_sprites.add(player)
                spawn_counter = 0
                upgrade_spawn_counter = 0
                xp_triangle_spawn_counter = 0
                player.score = 0
                player.health = 6
                game_over = False
                play_background_music()  # Restart background music

    # Update
    if not game_over:
        all_sprites.update()

        # Spawn enemies
        spawn_counter += 1
        if spawn_counter == 60:  # Spawn every second (60 frames per second)
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            spawn_counter = 0

        # Spawn upgrade cubes
        upgrade_spawn_counter += 1
        if upgrade_spawn_counter == upgrade_spawn_interval:  # Adjust the interval
            upgrade_cube = UpgradeCube()
            all_sprites.add(upgrade_cube)
            upgrade_cubes.add(upgrade_cube)
            upgrade_spawn_counter = 0

        # Spawn XP triangles
        xp_triangle_spawn_counter += 1
        if xp_triangle_spawn_counter == xp_triangle_spawn_interval:  # Adjust the interval
            xp_triangle = XPTriangle()
            all_sprites.add(xp_triangle)
            xp_triangles.add(xp_triangle)
            xp_triangle_spawn_counter = 0

        # Collision detection with upgrade cubes
        upgrade_hits = pygame.sprite.spritecollide(player, upgrade_cubes, True)
        if upgrade_hits:
            player.upgrade()
            play_sound(upgradeItemStart)  # Play upgrade item start sound

        # Collision detection with XP triangles
        xp_triangle_hits = pygame.sprite.spritecollide(player, xp_triangles, True)
        for xp_triangle in xp_triangle_hits:
            if player.health < 6:
                player.health += 1
                if player.health > 6:
                    player.health = 6
                play_sound(pickUpXpItem)  # Play pick up XP item sound

        # Collision detection with enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            player.score += 1
            play_sound(defetedEnemy)  # Play defeated enemy sound

        # Collision detection with player
        for enemy in enemies:
            if pygame.sprite.collide_rect(player, enemy):
                player.health -= 1
                enemy.kill()
                if player.health <= 0:
                    game_over = True
                    play_sound(gameOver)  # Play game over sound

        # Collision detection with enemy bullets
        bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if bullet_hits:
            player.health -= 1
            play_sound(XpMinus)  # Play XP minus sound
            if player.health <= 0:
                game_over = True
                play_sound(gameOver)  # Play game over sound


        # Collision detection with player
        for enemy in enemies:
            if pygame.sprite.collide_rect(player, enemy):
                player.health -= 1
                enemy.kill()
                if player.health <= 0:
                    game_over = True
                    play_sound(gameOver)  # Play game over sound
    
    if game_over:
        enemies.empty()
        backgroundMusic.stop()  # Stop background music when game over

    # Draw
    window.fill((0, 0, 0))
    window.blit(bg_image, (0, 0))  # Draw background image

    all_sprites.draw(window)  # Draw all sprites

    # Display score
    score_text = font.render(f"Score: {player.score}", True, WHITE)
    window.blit(score_text, (WIDTH - 150, 10))

    # Display health bar
    pygame.draw.rect(window, GRAY, (10, 10, 200, 30))
    health_width = player.health * 33.33
    if player.health >= 4:
        color = GREEN
    elif player.health >= 2:
        color = ORANGE
    else:
        color = RED
    pygame.draw.rect(window, color, (10, 10, health_width, 30))

    # Display hx indicator
    hx_text = font.render(f"HX: {player.health}", True, WHITE)
    window.blit(hx_text, (220, 10))

    # Display upgrade timer
    if player.upgraded:
        upgrade_timer_text = font.render(f"Upgrade: {15 - player.upgrade_timer // 60}", True, WHITE)
        window.blit(upgrade_timer_text, (10, 50))

    # Check if player failed
    if game_over:
        fail_text = font.render("Fail", True, RED)
        window.blit(fail_text, (WIDTH // 2 - 50, HEIGHT // 2))

        play_again_text = font.render("Press 'R' to play again", True, WHITE)
        window.blit(play_again_text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
