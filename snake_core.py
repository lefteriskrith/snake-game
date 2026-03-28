import pygame
import random

# ------------- Settings -------------
CELL_SIZE = 24
GRID_WIDTH = 34
GRID_HEIGHT = 24
FPS = 6

# ------------- Colors -------------
COLOR_BG = (0, 0, 0)
COLOR_SNAKE = (46, 204, 113)
COLOR_FOOD = (231, 76, 60)
COLOR_TEXT = (236, 240, 241)
COLOR_WALL = (52, 73, 94)


def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont(None, size)
    text_img = font.render(text, True, COLOR_TEXT)
    surface.blit(text_img, (x, y))


def random_food_position(snake):
    while True:
        pos = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
        if pos not in snake:
            return pos


def draw_snake(surface, snake):
    snake_radius = CELL_SIZE // 2 - 2
    for i, segment in enumerate(snake):
        center = (segment[0] * CELL_SIZE + CELL_SIZE // 2, segment[1] * CELL_SIZE + CELL_SIZE // 2)
        # περισσότερο φωτισμένο κεφάλι
        color = (124, 255, 188) if i == 0 else COLOR_SNAKE
        pygame.gfxdraw.filled_circle(surface, center[0], center[1], snake_radius, color)
        pygame.gfxdraw.aacircle(surface, center[0], center[1], snake_radius, color)


def draw_food(surface, food):
    food_center = (food[0] * CELL_SIZE + CELL_SIZE // 2, food[1] * CELL_SIZE + CELL_SIZE // 2)
    food_radius = CELL_SIZE // 2 - 3

    pygame.gfxdraw.filled_circle(surface, food_center[0], food_center[1], food_radius, COLOR_FOOD)
    pygame.gfxdraw.aacircle(surface, food_center[0], food_center[1], food_radius, (150, 20, 30))

    # κοτσάνι και λέπι για μήλο
    stem_rect = pygame.Rect(food_center[0] - 3, food_center[1] - 12, 6, 8)
    pygame.draw.rect(surface, (48, 80, 38), stem_rect)
    shine_rect = pygame.Rect(food_center[0] - 6, food_center[1] - 6, 5, 4)
    pygame.draw.ellipse(surface, (250, 200, 200), shine_rect)


def draw_walls(surface):
    top_rect = pygame.Rect(0, 0, GRID_WIDTH * CELL_SIZE, CELL_SIZE)
    bottom_rect = pygame.Rect(0, (GRID_HEIGHT - 1) * CELL_SIZE, GRID_WIDTH * CELL_SIZE, CELL_SIZE)
    left_rect = pygame.Rect(0, 0, CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
    right_rect = pygame.Rect((GRID_WIDTH - 1) * CELL_SIZE, 0, CELL_SIZE, GRID_HEIGHT * CELL_SIZE)

    pygame.draw.rect(surface, COLOR_WALL, top_rect)
    pygame.draw.rect(surface, COLOR_WALL, bottom_rect)
    pygame.draw.rect(surface, COLOR_WALL, left_rect)
    pygame.draw.rect(surface, COLOR_WALL, right_rect)


def check_wall_collision(pos):
    x, y = pos
    return x <= 0 or x >= GRID_WIDTH - 1 or y <= 0 or y >= GRID_HEIGHT - 1
