import pygame
import random
import sys
import os

pygame.init()

# Размеры
CELL = 40
COLS = 20
ROWS = 16
W = COLS * CELL
H = ROWS * CELL + 60  # +60 для панели счёта

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake Tax")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 24)
font_big = pygame.font.SysFont("consolas", 44, bold=True)

# Загрузка картинок из папки images/
def load(name):
    for ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        path = os.path.join("images", name + ext)
        if os.path.isfile(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, (CELL, CELL))
    return None

img_head = load("head")
img_body = load("body")
img_food = load("food")

# Заглушки если картинки нет
def draw_cell(x, y, img, color):
    rx = x * CELL
    ry = y * CELL + 60
    if img:
        screen.blit(img, (rx, ry))
    else:
        pygame.draw.rect(screen, color, (rx + 2, ry + 2, CELL - 4, CELL - 4), border_radius=6)

# Направление → угол поворота головы
def angle(d):
    return {(1,0): 270, (-1,0): 90, (0,-1): 0, (0,1): 180}[d]

# Игровые переменные
def new_game():
    cx, cy = COLS // 2, ROWS // 2
    snake = [(cx, cy), (cx-1, cy), (cx-2, cy)]
    direction = (1, 0)
    food = spawn_food(snake)
    return snake, direction, food, 0

def spawn_food(snake):
    free = [(c, r) for c in range(COLS) for r in range(ROWS) if (c, r) not in snake]
    return random.choice(free)

snake, direction, food, score = new_game()
next_dir = direction
hi = 0
alive = True
speed = 150  # миллисекунд между шагами
last_move = pygame.time.get_ticks()

# Главный цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            keys = {
                pygame.K_UP: (0,-1), pygame.K_w: (0,-1),
                pygame.K_DOWN: (0,1), pygame.K_s: (0,1),
                pygame.K_LEFT: (-1,0), pygame.K_a: (-1,0),
                pygame.K_RIGHT: (1,0), pygame.K_d: (1,0),
            }
            if event.key in keys:
                nd = keys[event.key]
                # нельзя развернуться на 180°
                if nd[0] + direction[0] != 0 or nd[1] + direction[1] != 0:
                    next_dir = nd
            if event.key == pygame.K_r and not alive:
                snake, direction, food, score = new_game()
                next_dir = direction
                alive = True
                speed = 150

    # Движение по таймеру
    now = pygame.time.get_ticks()
    if alive and now - last_move > speed:
        last_move = now
        direction = next_dir
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        # Проверка стен и тела
        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in snake[:-1]:
            alive = False
        else:
            snake.insert(0, head)
            if head == food:
                score += 10
                hi = max(hi, score)
                food = spawn_food(snake)
                speed = max(60, speed - 3)  # ускорение
            else:
                snake.pop()

    # Отрисовка
    screen.fill((15, 20, 30))

    # Панель счёта
    screen.blit(font.render(f"Счёт: {score}", True, (90, 230, 140)), (16, 18))
    screen.blit(font.render(f"Рекорд: {hi}", True, (150, 170, 150)), (200, 18))
    screen.blit(font.render("R — рестарт", True, (70, 90, 80)), (W - 190, 18))

    # Сетка
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(screen, (22, 30, 42),
                (c*CELL+1, r*CELL+61, CELL-2, CELL-2), border_radius=4)

    # Еда
    draw_cell(food[0], food[1], img_food, (220, 60, 60))

    # Тело
    for seg in snake[1:]:
        draw_cell(seg[0], seg[1], img_body, (50, 170, 90))

    # Голова (с поворотом)
    hx, hy = snake[0]
    if img_head:
        rotated = pygame.transform.rotate(img_head, angle(direction))
        screen.blit(rotated, (hx * CELL, hy * CELL + 60))
    else:
        draw_cell(hx, hy, None, (80, 220, 120))

    # Game Over
    if not alive:
        overlay = pygame.Surface((W, H - 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 60))
        screen.blit(font_big.render("GAME OVER", True, (230, 70, 70)),
            font_big.render("GAME OVER", True, (0,0,0)).get_rect(center=(W//2, H//2 - 20)))
        screen.blit(font.render(f"Счёт: {score}  |  Нажми R", True, (200, 200, 200)),
            font.render("x", True, (0,0,0)).get_rect(center=(W//2, H//2 + 30)))

    pygame.display.flip()
    clock.tick(60)