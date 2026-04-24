import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FONT = pygame.font.Font(None, 24)

toolbar_height = 60

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT + toolbar_height)
)

pygame.display.set_caption("Paint")

canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill(WHITE)

# ================= ИКОНКИ =================

tool_icons = {
    "brush": pygame.image.load("img/brush.png"),
    "clear": pygame.image.load("img/clear.png"),
    "cursor": pygame.image.load("img/cursor.png"),
    "eraser": pygame.image.load("img/eraser.png"),
    "save": pygame.image.load("img/save.png")
}

# ================= КНОПКИ =================

tool_buttons = {}

x_offset = 10

for tool in tool_icons:

    tool_buttons[tool] = pygame.Rect(
        x_offset,
        HEIGHT + 10,
        40,
        40
    )

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

clock = pygame.time.Clock()

running = True
drawing = False

moving = False
selected_shape = None
offset_x = 0
offset_y = 0

last_pos = None

mode = "pen"

color = BLACK
size = 5

start_pos = None

shapes = []

# ================= ФУНКЦИИ =================

def draw_toolbar():

    pygame.draw.rect(
        screen,
        (200, 200, 200),
        (0, HEIGHT, WIDTH, toolbar_height)
    )

    for tool, rect in tool_buttons.items():

        screen.blit(
            pygame.transform.scale(
                tool_icons[tool],
                (40, 40)
            ),
            rect.topleft
        )

    for color_value, rect in color_buttons.items():

        pygame.draw.rect(
            screen,
            color_value,
            rect
        )

        pygame.draw.rect(
            screen,
            BLACK,
            rect,
            2
        )


def draw_circle(surface, color, center, radius):

    pygame.draw.circle(
        surface,
        color,
        center,
        radius,
        0
    )

    shapes.append(
        ["circle", color, list(center), radius]
    )


def draw_rect(surface, color, start, end):

    rect = pygame.Rect(
        start,
        (
            end[0] - start[0],
            end[1] - start[1]
        )
    )

    pygame.draw.rect(
        surface,
        color,
        rect,
        0
    )

    shapes.append(
        ["rect", color, rect]
    )


def save_image():

    pygame.image.save(
        canvas,
        "drawing.png"
    )


def redraw_canvas():

    screen.fill(WHITE)

    screen.blit(canvas, (0, 0))

    draw_toolbar()

    instruction_text = FONT.render(
        "P-Кисть  R-Прямоугольник  C-Круг  E-Ластик  Cursor-Перемещение",
        True,
        BLACK
    )

    screen.blit(
        instruction_text,
        (10, HEIGHT - 20)
    )


# ================= ГЛАВНЫЙ ЦИКЛ =================

while running:

    redraw_canvas()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.pos[1] > HEIGHT:

                for tool, rect in tool_buttons.items():

                    if rect.collidepoint(event.pos):

                        if tool == "brush":
                            mode = "pen"

                        elif tool == "clear":
                            canvas.fill(WHITE)
                            shapes.clear()

                        elif tool == "eraser":
                            mode = "eraser"

                        elif tool == "save":
                            save_image()

                        elif tool == "cursor":
                            mode = "move"

                for color_value, rect in color_buttons.items():

                    if rect.collidepoint(event.pos):

                        color = color_value

            else:

                if mode == "move":

                    for shape in reversed(shapes):

                        if shape[0] == "rect":

                            rect = shape[2]

                            if rect.collidepoint(event.pos):

                                selected_shape = shape
                                moving = True

                                offset_x = event.pos[0] - rect.x
                                offset_y = event.pos[1] - rect.y

                                break

                        elif shape[0] == "circle":

                            center = shape[2]
                            radius = shape[3]

                            dx = event.pos[0] - center[0]
                            dy = event.pos[1] - center[1]

                            if dx * dx + dy * dy <= radius * radius:

                                selected_shape = shape
                                moving = True

                                offset_x = event.pos[0] - center[0]
                                offset_y = event.pos[1] - center[1]

                                break

                else:

                    drawing = True
                    last_pos = event.pos
                    start_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:

            drawing = False
            moving = False
            selected_shape = None

            if mode == "rect":

                draw_rect(
                    canvas,
                    color,
                    start_pos,
                    event.pos
                )

            elif mode == "circle":

                radius = int(
                    (
                        (event.pos[0] - start_pos[0]) ** 2
                        +
                        (event.pos[1] - start_pos[1]) ** 2
                    ) ** 0.5
                )

                draw_circle(
                    canvas,
                    color,
                    start_pos,
                    radius
                )

        elif event.type == pygame.MOUSEMOTION:

            if moving and selected_shape:

                if selected_shape[0] == "rect":

                    rect = selected_shape[2]

                    rect.x = event.pos[0] - offset_x
                    rect.y = event.pos[1] - offset_y

                elif selected_shape[0] == "circle":

                    selected_shape[2][0] = event.pos[0] - offset_x
                    selected_shape[2][1] = event.pos[1] - offset_y

            elif drawing and mode == "pen":

                pygame.draw.line(
                    canvas,
                    color,
                    last_pos,
                    event.pos,
                    size
                )

                last_pos = event.pos

            elif drawing and mode == "eraser":

                pygame.draw.line(
                    canvas,
                    WHITE,
                    last_pos,
                    event.pos,
                    size
                )

                last_pos = event.pos

    pygame.display.flip()

    clock.tick(60)

pygame.quit()