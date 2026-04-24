import pygame
import random
import sys
import os

# ─────────────────────────────────────────────
#  НАСТРОЙКИ
# ─────────────────────────────────────────────
CELL = 39         # размер одной клетки (пикселей)
COLS = 20          # колонок
ROWS = 16          # рядов
W    = COLS * CELL # ширина игрового поля
H    = ROWS * CELL # высота игрового поля
UI_H = 60          # высота панели сверху

FPS_START = 8      # начальная скорость

# Цвета (fallback, если нет картинок)
CLR_BG       = (15,  20,  30)
CLR_GRID     = (25,  32,  45)
CLR_HEAD     = (80, 220, 120)
CLR_BODY     = (50, 170,  90)
CLR_FOOD     = (230,  60,  60)
CLR_UI_BG    = (10,  14,  22)
CLR_TEXT     = (200, 220, 200)
CLR_SCORE    = (90, 230, 140)
CLR_GAMEOVER = (230,  70,  70)

# ─────────────────────────────────────────────
#  ПАПКА С КАРТИНКАМИ
#
#  Положи файлы рядом со скриптом в папку  images/
#  Названия файлов (можно .png / .jpg / .jpeg / .bmp):
#
#    images/head.png   — голова змейки
#    images/body.png   — тело змейки
#    images/food.png   — еда (яблоко)
#
# ─────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

EXTENSIONS = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]

def find_image(name):
    """Ищет файл images/<name>.<ext> и возвращает путь или None."""
    for ext in EXTENSIONS:
        path = os.path.join(IMAGES_DIR, name + ext)
        if os.path.isfile(path):
            return path
    return None

# ─────────────────────────────────────────────
#  ЗАГРУЗКА И МАСШТАБ ИЗОБРАЖЕНИЯ
# ─────────────────────────────────────────────
def load_img(path, size):
    if not path:
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception as e:
        print(f"[!] Не удалось загрузить '{path}': {e}")
        return None

# ─────────────────────────────────────────────
#  ФОЛЛБЭК-ПОВЕРХНОСТИ (если картинки нет)
# ─────────────────────────────────────────────
def make_fallback(color, size, shape="rect"):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    r = size // 2
    if shape == "circle":
        pygame.draw.circle(surf, color, (r, r), r - 2)
        pygame.draw.circle(surf, (*color[:3], 100), (r, r), r - 2, 3)
    else:
        pad = 3
        pygame.draw.rect(surf, color, (pad, pad, size - pad*2, size - pad*2), border_radius=8)
    return surf

# ─────────────────────────────────────────────
#  КЛАСС ЗМЕЙКИ
# ─────────────────────────────────────────────
class Snake:
    DIRS = {
        pygame.K_UP:    (0, -1),
        pygame.K_DOWN:  (0,  1),
        pygame.K_LEFT:  (-1, 0),
        pygame.K_RIGHT: (1,  0),
        pygame.K_w:     (0, -1),
        pygame.K_s:     (0,  1),
        pygame.K_a:     (-1, 0),
        pygame.K_d:     (1,  0),
    }

    def __init__(self):
        self.reset()

    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body      = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir  = (1, 0)
        self.grow      = False

    def handle_key(self, key):
        if key in self.DIRS:
            nd = self.DIRS[key]
            if (nd[0] + self.direction[0], nd[1] + self.direction[1]) != (0, 0):
                self.next_dir = nd

    def step(self):
        self.direction = self.next_dir
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            return False
        if new_head in self.body[:-1]:
            return False

        self.body.insert(0, new_head)
        if self.grow:
            self.grow = False
        else:
            self.body.pop()
        return True

    def eat(self, food):
        return self.body[0] == food

# ─────────────────────────────────────────────
#  ОТРИСОВКА ОДНОЙ КЛЕТКИ
# ─────────────────────────────────────────────
def draw_cell(surf, col, row, img, fallback, angle=0):
    x = col * CELL
    y = row * CELL + UI_H
    sprite = img if img else fallback
    if angle:
        sprite = pygame.transform.rotate(sprite, angle)
    rect = sprite.get_rect(center=(x + CELL // 2, y + CELL // 2))
    surf.blit(sprite, rect)

def dir_to_angle(d):
    return {(1, 0): 270, (-1, 0): 90, (0, -1): 0, (0, 1): 180}.get(d, 0)

# ─────────────────────────────────────────────
#  ГЛАВНАЯ ФУНКЦИЯ
# ─────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("Snake Tax")
    screen = pygame.display.set_mode((W, H + UI_H))
    clock  = pygame.time.Clock()

    font_big   = pygame.font.SysFont("consolas", 42, bold=True)
    font_med   = pygame.font.SysFont("consolas", 26)
    font_small = pygame.font.SysFont("consolas", 18)

    # создаём папку images/ если её нет
    os.makedirs(IMAGES_DIR, exist_ok=True)

    # автозагрузка картинок из images/
    head_path = find_image("head")
    body_path = find_image("body")
    food_path = find_image("food")

    print("\n=== Snake Tax — загрузка картинок ===")
    print(f"  Папка: {IMAGES_DIR}")
    print(f"  head -> {'найдено: ' + head_path if head_path else 'НЕ НАЙДЕНО (цветной квадрат)'}")
    print(f"  body -> {'найдено: ' + body_path if body_path else 'НЕ НАЙДЕНО (цветной квадрат)'}")
    print(f"  food -> {'найдено: ' + food_path if food_path else 'НЕ НАЙДЕНО (цветной круг)'}")
    print()

    img_head = load_img(head_path, (CELL, CELL))
    img_body = load_img(body_path, (CELL, CELL))
    img_food = load_img(food_path, (CELL, CELL))

    fb_head = make_fallback(CLR_HEAD, CELL, "rect")
    fb_body = make_fallback(CLR_BODY, CELL, "rect")
    fb_food = make_fallback(CLR_FOOD, CELL, "circle")

    # сетка (кэш)
    grid_surf = pygame.Surface((W, H))
    grid_surf.fill(CLR_BG)
    for c in range(COLS):
        for r in range(ROWS):
            rect = pygame.Rect(c*CELL + 1, r*CELL + 1, CELL - 2, CELL - 2)
            pygame.draw.rect(grid_surf, CLR_GRID, rect, border_radius=4)

    snake = Snake()
    score = 0
    hi    = 0
    fps   = FPS_START
    alive = True

    def spawn_food():
        free = [(c, r) for c in range(COLS) for r in range(ROWS)
                if (c, r) not in snake.body]
        return random.choice(free) if free else (0, 0)

    food = spawn_food()

    MOVE_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_EVENT, 1000 // fps)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if alive:
                    snake.handle_key(event.key)
                if event.key == pygame.K_r:
                    snake.reset()
                    score = 0
                    fps   = FPS_START
                    pygame.time.set_timer(MOVE_EVENT, 1000 // fps)
                    food  = spawn_food()
                    alive = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

            if event.type == MOVE_EVENT and alive:
                alive = snake.step()
                if alive and snake.eat(food):
                    score += 10
                    hi = max(hi, score)
                    snake.grow = True
                    food = spawn_food()
                    if score % 50 == 0:
                        fps = min(fps + 1, 25)
                        pygame.time.set_timer(MOVE_EVENT, 1000 // fps)

        # отрисовка
        screen.fill(CLR_UI_BG)

        score_txt = font_med.render(f"СЧЁТ: {score}", True, CLR_SCORE)
        hi_txt    = font_small.render(f"РЕКОРД: {hi}", True, CLR_TEXT)
        tip_txt   = font_small.render("R — рестарт  |  ESC — выход", True, (80, 100, 90))
        screen.blit(score_txt, (16, 8))
        screen.blit(hi_txt,    (16, 36))
        screen.blit(tip_txt,   (W - tip_txt.get_width() - 12, 22))

        screen.blit(grid_surf, (0, UI_H))

        draw_cell(screen, food[0], food[1], img_food, fb_food)

        for seg in snake.body[1:]:
            draw_cell(screen, seg[0], seg[1], img_body, fb_body)

        head  = snake.body[0]
        angle = dir_to_angle(snake.direction)
        draw_cell(screen, head[0], head[1], img_head, fb_head, angle=angle)

        if not alive:
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, UI_H))

            go   = font_big.render("GAME OVER", True, CLR_GAMEOVER)
            sub  = font_med.render(f"Счёт: {score}", True, CLR_TEXT)
            hint = font_small.render("Нажми  R  чтобы начать заново", True, (150, 180, 150))

            cx = W // 2
            cy = H // 2 + UI_H
            screen.blit(go,   go.get_rect(center=(cx, cy - 40)))
            screen.blit(sub,  sub.get_rect(center=(cx, cy + 10)))
            screen.blit(hint, hint.get_rect(center=(cx, cy + 50)))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()