import pygame, sys, random
from pygame.locals import *

pygame.init()
pygame.mixer.init()

W, H = 400, 600
SCREEN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Verdana", 20)

# --- Загрузка ресурсов ---
def load(file, size):
    return pygame.transform.scale(pygame.image.load(file).convert_alpha(), size)

bg        = pygame.transform.scale(pygame.image.load("AnimatedStreet.png"), (W, H))
go_bg     = pygame.transform.scale(pygame.image.load("game_over_bg.png"), (W, H))
coin_snd  = pygame.mixer.Sound("coin_sound.mp3")
crash_snd = pygame.mixer.Sound("crash.mp3")

player_img   = load("Player.png", (90, 100))
enemy_img    = load("Enemy.png",  (90, 100))
coin_frames  = [load(f"coin{i}.png", (40, 40)) for i in range(1, 5)]

LANES = [50, 150, 250, 350]

# --- Сброс игры ---
def reset():
    return {
        "speed":      5,
        "score":      0,
        "coins":      0,
        "bg_y1":      0,
        "bg_y2":      -H,
        "player":     player_img.get_rect(center=(W//2, H - 150)),
        "enemy":      enemy_img.get_rect(center=(random.choice(LANES), -100)),
        "coin":       coin_frames[0].get_rect(center=(random.choice(LANES), -300)),
        "coin_frame": 0.0,
    }

g = reset()

INC_SPEED = USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

def hb(rect, dx=40, dy=20):
    return rect.inflate(-dx, -dy)

# --- Главный цикл ---
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit(); sys.exit()
        if event.type == INC_SPEED and g["speed"] < 15:
            g["speed"] += 0.5

    # Управление
    keys = pygame.key.get_pressed()
    if keys[K_LEFT]  and g["player"].left  > 0: g["player"].x -= 5
    if keys[K_RIGHT] and g["player"].right < W: g["player"].x += 5

    # Прокрутка фона
    g["bg_y1"] += g["speed"]; g["bg_y2"] += g["speed"]
    if g["bg_y1"] >= H: g["bg_y1"] = -H
    if g["bg_y2"] >= H: g["bg_y2"] = -H

    # Движение врага
    g["enemy"].y += g["speed"]
    if g["enemy"].top > H:
        g["score"] += 1
        g["enemy"].center = (random.choice(LANES), -100)

    # Движение и анимация монетки
    g["coin"].y += g["speed"]
    if g["coin"].top > H:
        g["coin"].center = (random.choice(LANES), -300)
    g["coin_frame"] = (g["coin_frame"] + 0.2) % 4
    coin_img = coin_frames[int(g["coin_frame"])]

    # Подбор монетки
    if hb(g["player"]).colliderect(hb(g["coin"], 10, 10)):
        g["coins"] += 1
        coin_snd.play()
        g["coin"].center = (random.choice(LANES), -300)

    # Столкновение с врагом → Game Over
    if hb(g["player"]).colliderect(hb(g["enemy"])):
        crash_snd.play()
        while True:
            SCREEN.blit(go_bg, (0, 0))
            SCREEN.blit(font.render(f"Score: {g['score']}", True, (255,255,255)), (165, 240))
            SCREEN.blit(font.render(f"Coins: {g['coins']}", True, (255,255,255)), (165, 270))
            SCREEN.blit(font.render("R — Restart", True, (255,255,255)), (140, 460))
            SCREEN.blit(font.render("ESC — Exit",  True, (255,255,255)), (148, 495))
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_r:
                        g = reset()
                    if event.key == K_ESCAPE:
                        pygame.quit(); sys.exit()
            if g["score"] == 0:
                break

    # Отрисовка
    SCREEN.blit(bg, (0, g["bg_y1"]))
    SCREEN.blit(bg, (0, g["bg_y2"]))
    SCREEN.blit(player_img, g["player"])
    SCREEN.blit(enemy_img,  g["enemy"])
    SCREEN.blit(coin_img,   g["coin"])
    SCREEN.blit(font.render(f"Score: {g['score']}", True, (0,0,0)), (10, 10))
    SCREEN.blit(font.render(f"Coins: {g['coins']}", True, (0,0,0)), (10, 40))

    pygame.display.update()
    clock.tick(60)