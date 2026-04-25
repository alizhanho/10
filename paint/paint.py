import pygame

import math

pygame.init()

WIDTH, HEIGHT = 800, 600

toolbar_height = 60

WHITE = (255, 255, 255)

BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT + toolbar_height))

pygame.display.set_caption("Paint")

FONT = pygame.font.Font(None, 24)

clock = pygame.time.Clock()

canvas = pygame.Surface((WIDTH, HEIGHT))

canvas.fill(WHITE)

# ===== ИКОНКИ =====

tool_icons = {

    "brush": pygame.image.load("img/brush.png"),

    "clear": pygame.image.load("img/clear.png"),

    "eraser": pygame.image.load("img/eraser.png"),

    "save": pygame.image.load("img/save.png")

}

# ===== КНОПКИ =====

tool_buttons = {}

x_offset = 10

for tool in tool_icons:

    tool_buttons[tool] = pygame.Rect(x_offset, HEIGHT + 10, 40, 40)

    x_offset += 50

color_buttons = {

    (0, 0, 0): pygame.Rect(300, HEIGHT + 10, 40, 40),

    (255, 0, 0): pygame.Rect(350, HEIGHT + 10, 40, 40),

    (0, 255, 0): pygame.Rect(400, HEIGHT + 10, 40, 40),

    (0, 0, 255): pygame.Rect(450, HEIGHT + 10, 40, 40),

    (255, 255, 0): pygame.Rect(500, HEIGHT + 10, 40, 40),

    (255, 165, 0): pygame.Rect(550, HEIGHT + 10, 40, 40),

    (128, 0, 128): pygame.Rect(600, HEIGHT + 10, 40, 40),

    (255, 255, 255): pygame.Rect(650, HEIGHT + 10, 40, 40)

}

# ===== СОСТОЯНИЯ =====

running = True

drawing = False

mode = "pen"

color = BLACK

size = 5

last_pos = None

start_pos = None

shapes = []

# ===== РИСОВАНИЕ ФИГУР =====

def draw_rect(start, end):

    rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))

    pygame.draw.rect(canvas, color, rect)

def draw_circle(start, end):

    radius = int(math.hypot(end[0] - start[0], end[1] - start[1]))

    pygame.draw.circle(canvas, color, start, radius)

def save_image():

    pygame.image.save(canvas, "drawing.png")

def draw_toolbar():

    pygame.draw.rect(screen, (200, 200, 200), (0, HEIGHT, WIDTH, toolbar_height))

    for tool, rect in tool_buttons.items():

        screen.blit(pygame.transform.scale(tool_icons[tool], (40, 40)), rect.topleft)

    for color_value, rect in color_buttons.items():

        pygame.draw.rect(screen, color_value, rect)

        pygame.draw.rect(screen, BLACK, rect, 2)

def redraw_screen():

    screen.fill(WHITE)

    screen.blit(canvas, (0, 0))

    draw_toolbar()

    text = FONT.render(

        "P-Кисть  R-Прямоугольник  C-Круг  E-Ластик",

        True,

        BLACK

    )

    screen.blit(text, (10, HEIGHT - 20))

# ===== ГЛАВНЫЙ ЦИКЛ =====

while running:

    redraw_screen()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ===== КЛАВИШИ =====

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_p:

                mode = "pen"

            elif event.key == pygame.K_r:

                mode = "rect"

            elif event.key == pygame.K_c:

                mode = "circle"

            elif event.key == pygame.K_e:

                mode = "eraser"

        # ===== НАЖАТИЕ МЫШИ =====

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.pos[1] > HEIGHT:

                for tool, rect in tool_buttons.items():

                    if rect.collidepoint(event.pos):

                        if tool == "brush":

                            mode = "pen"

                        elif tool == "clear":

                            canvas.fill(WHITE)

                        elif tool == "eraser":

                            mode = "eraser"

                        elif tool == "save":

                            save_image()

                for color_value, rect in color_buttons.items():

                    if rect.collidepoint(event.pos):

                        color = color_value

            else:

                drawing = True

                start_pos = event.pos

                last_pos = event.pos

        # ===== ОТПУСКАНИЕ МЫШИ =====

        elif event.type == pygame.MOUSEBUTTONUP:

            drawing = False

            if mode == "rect":

                draw_rect(start_pos, event.pos)

            elif mode == "circle":

                draw_circle(start_pos, event.pos)

        # ===== ДВИЖЕНИЕ МЫШИ =====

        elif event.type == pygame.MOUSEMOTION:

            if drawing and mode == "pen":

                pygame.draw.line(canvas, color, last_pos, event.pos, size)

                last_pos = event.pos

            elif drawing and mode == "eraser":

                pygame.draw.line(canvas, WHITE, last_pos, event.pos, size * 3)

                last_pos = event.pos

    pygame.display.flip()

    clock.tick(60)

pygame.quit()