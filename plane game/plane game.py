import pygame
import random

# 初始化 Pygame 的核心模块
pygame.init()

# 屏幕大小
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)   
GREEN = (0, 255, 0)  
HEART_COLOR = (255, 100, 100)
FAST_ENEMY_COLOR = (255, 165, 0)
BOSS_ENEMY_COLOR = (128, 0, 128)
ULTIMATE_BOSS_COLOR = (255, 0, 255)
LASER_COLOR = (0, 255, 255)

# 创建屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
pygame.display.set_caption("飞机大战")

# 游戏变量
player_width = 50
player_height = 60
player_x = SCREEN_WIDTH // 2 - player_width // 2
player_y = SCREEN_HEIGHT - player_height - 20
player_speed = 8

bullet_width = 5
bullet_height = 15
bullets = []
laser_bullets = []
bullet_speed = -10
laser_speed = -15
bullet_cooldown = 10
laser_cooldown = 50
bullet_timer = 0
laser_timer = 0

enemy_width = 40
enemy_height = 40
enemies = []
enemy_speed = 8
fast_enemy_speed = 10
boss_enemy_speed = 6
ultimate_boss_speed = 1
spawn_rate = 1000
pygame.time.set_timer(pygame.USEREVENT + 1, spawn_rate)

health_packs = []
health_pack_width = 30
health_pack_height = 30
health_pack_chance = 0.1

lives = 3
max_lives = 5
game_over = False
score = 0
escaped_enemies = 0
max_escaped = 15
difficulty_increment_score = 20  # 每 20 分增加一次难度
level = 1
ultimate_boss_spawn_score = 100  # 在得分达到一定值时才会生成终极 Boss

# 子弹类
class Bullet:
    def __init__(self, x, y, bullet_type="normal"):
        self.x = x
        self.y = y
        self.type = bullet_type

    def move(self):
        self.y += laser_speed if self.type == "laser" else bullet_speed

    def draw(self):
        color = LASER_COLOR if self.type == "laser" else YELLOW
        width = bullet_width * 2 if self.type == "laser" else bullet_width
        pygame.draw.rect(screen, color, (self.x, self.y, width, bullet_height))

# 敌人类
class Enemy:
    def __init__(self, x, y, speed, enemy_type="normal"):
        self.x = x
        self.y = y
        self.speed = speed
        self.type = enemy_type

    def move(self):
        self.y += self.speed
        if self.type == "boss":
            # Boss 敌机左右摇摆  
            self.x += random.choice([-4, 4])

    def draw(self):
        if self.type == "normal":
            pygame.draw.circle(screen, RED, (self.x + enemy_width // 2, self.y + enemy_height // 2), enemy_width // 2)
        elif self.type == "fast":
            pygame.draw.polygon(screen, FAST_ENEMY_COLOR, [
                (self.x, self.y + enemy_height),
                (self.x + enemy_width // 2, self.y),
                (self.x + enemy_width, self.y + enemy_height),
            ])
        elif self.type == "boss":
            pygame.draw.rect(screen, BOSS_ENEMY_COLOR, (self.x, self.y, enemy_width * 2, enemy_height))
        elif self.type == "ultimate":
            pygame.draw.polygon(screen, ULTIMATE_BOSS_COLOR, [
                (self.x, self.y + enemy_height),
                (self.x + enemy_width // 2, self.y),
                (self.x + enemy_width, self.y + enemy_height),
                (self.x + enemy_width // 2, self.y - 30)
            ])

# 血包类
class HealthPack:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y += 2  

    def draw(self):
        pygame.draw.circle(screen, HEART_COLOR, (self.x + health_pack_width // 2, self.y + health_pack_height // 2), health_pack_width // 2)

# 绘制玩家飞机
def draw_player(x, y):
    pygame.draw.polygon(screen, BLUE, [
        (x, y + player_height), 
        (x + player_width // 2, y), 
        (x + player_width, y + player_height)
    ])
    pygame.draw.polygon(screen, WHITE, [
        (x + 5, y + player_height // 2),
        (x + player_width // 2, y + player_height // 2 - 10),
        (x + player_width - 5, y + player_height // 2)
    ])

# 绘制生命值
def draw_lives(lives):
    for i in range(lives):
        pygame.draw.circle(screen, HEART_COLOR, (20 + i * 30, 20), 10)

# 显示分数和状态
def draw_status(score, escaped):
    font = pygame.font.SysFont(None, 30)
    score_text = font.render(f"Score: {score}", True, WHITE)
    escaped_text = font.render(f"Escaped: {escaped}/{max_escaped}", True, RED if escaped >= max_escaped - 5 else WHITE)
    screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
    screen.blit(escaped_text, (SCREEN_WIDTH - 150, 50))

# 显示游戏结束画面
def game_over_screen(score):
    font = pygame.font.SysFont(None, 60)
    game_over_text = font.render("GAME OVER", True, RED)
    score_text = font.render(f"Your Score: {score}", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50))
    screen.blit(score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20))

# 生成敌人
def spawn_enemy():
    global level
    if score >= difficulty_increment_score * level:
        enemy_type = random.choice(["normal", "fast", "boss"]) if score < ultimate_boss_spawn_score else "ultimate"
    else:
        enemy_type = random.choice(["normal", "fast"])
    x = random.randint(0, SCREEN_WIDTH - enemy_width)
    speed = enemy_speed if enemy_type == "normal" else fast_enemy_speed if enemy_type == "fast" else boss_enemy_speed if enemy_type == "boss" else ultimate_boss_speed
    enemies.append(Enemy(x, -enemy_height, speed, enemy_type))

# 生成血包
def spawn_health_pack():
    if random.random() < health_pack_chance:
        x = random.randint(0, SCREEN_WIDTH - health_pack_width)
        health_packs.append(HealthPack(x, -health_pack_height))

# 游戏主循环
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT + 1 and not game_over:
            spawn_enemy()
            spawn_health_pack()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < SCREEN_HEIGHT - player_height:
        player_y += player_speed
    if keys[pygame.K_SPACE] and bullet_timer == 0:
        bullets.append(Bullet(player_x + player_width // 2 - bullet_width // 2, player_y))
        bullet_timer = bullet_cooldown
    if keys[pygame.K_LSHIFT] and laser_timer == 0:
        laser_bullets.append(Bullet(player_x + player_width // 2 - bullet_width, player_y, bullet_type="laser"))
        laser_timer = laser_cooldown

    if bullet_timer > 0:
        bullet_timer -= 1
    if laser_timer > 0:
        laser_timer -= 1

    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()
        if bullet.y < 0:
            bullets.remove(bullet)

    for bullet in laser_bullets[:]:
        bullet.move()
        bullet.draw()
        if bullet.y < 0:
            laser_bullets.remove(bullet)

    for enemy in enemies[:]:
        enemy.move()
        enemy.draw()
        if enemy.y > SCREEN_HEIGHT:
            enemies.remove(enemy)
            escaped_enemies += 1
            if escaped_enemies >= max_escaped:
                game_over = True
        for bullet in bullets[:]:
            if bullet.x > enemy.x and bullet.x < enemy.x + enemy_width and bullet.y > enemy.y and bullet.y < enemy.y + enemy_height:
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 10
                break  # 退出当前循环避免出错
        for bullet in laser_bullets[:]:
            if bullet.x > enemy.x and bullet.x < enemy.x + enemy_width and bullet.y > enemy.y and bullet.y < enemy.y + enemy_height:
                laser_bullets.remove(bullet)
                enemies.remove(enemy)
                score += 20
                break
        if player_x < enemy.x + enemy_width and player_x + player_width > enemy.x and player_y < enemy.y + enemy_height and player_y + player_height > enemy.y:
            enemies.remove(enemy)
            lives -= 1
            if lives <= 0:
                game_over = True

    for health_pack in health_packs[:]:
        health_pack.move()
        health_pack.draw()
        if health_pack.y > SCREEN_HEIGHT:
            health_packs.remove(health_pack)
        elif player_x < health_pack.x < player_x + player_width and player_y < health_pack.y < player_y + player_height:
            lives += 1
            if lives > max_lives:
                lives = max_lives
            health_packs.remove(health_pack)

    draw_player(player_x, player_y)
    draw_lives(lives)
    draw_status(score, escaped_enemies)

    if game_over:
        game_over_screen(score)

    pygame.display.update()
    clock.tick(60)

pygame.quit()







