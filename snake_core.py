import math
import random

import pygame
from pygame import gfxdraw

# ------------- Settings -------------
CELL_SIZE = 28
GRID_WIDTH = 32
GRID_HEIGHT = 22
HUD_HEIGHT = 92
BASE_FPS = 8
MAX_FPS = 17

BOARD_WIDTH = GRID_WIDTH * CELL_SIZE
BOARD_HEIGHT = GRID_HEIGHT * CELL_SIZE
SCREEN_WIDTH = BOARD_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT + HUD_HEIGHT

# ------------- Colors -------------
COLOR_BG_TOP = (8, 17, 24)
COLOR_BG_BOTTOM = (18, 34, 22)
COLOR_GRID = (255, 255, 255, 18)
COLOR_PANEL = (7, 12, 18, 210)
COLOR_PANEL_BORDER = (90, 141, 108)
COLOR_SNAKE = (70, 214, 123)
COLOR_SNAKE_HEAD = (153, 255, 196)
COLOR_SNAKE_SHADOW = (10, 40, 20, 90)
COLOR_FOOD = (230, 76, 70)
COLOR_TEXT = (239, 247, 241)
COLOR_TEXT_DIM = (148, 176, 154)
COLOR_ACCENT = (255, 211, 107)


def _font(size, bold=False):
    return pygame.font.SysFont("arialroundedmtbold", size, bold=bold)


def draw_text(surface, text, size, x, y, color=COLOR_TEXT, bold=False):
    text_img = _font(size, bold=bold).render(text, True, color)
    surface.blit(text_img, (x, y))


def random_food_position(snake, blocked=None):
    blocked = blocked or set()
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake and pos not in blocked:
            return pos


def create_background_surface():
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        mix = y / SCREEN_HEIGHT
        color = (
            int(COLOR_BG_TOP[0] + (COLOR_BG_BOTTOM[0] - COLOR_BG_TOP[0]) * mix),
            int(COLOR_BG_TOP[1] + (COLOR_BG_BOTTOM[1] - COLOR_BG_TOP[1]) * mix),
            int(COLOR_BG_TOP[2] + (COLOR_BG_BOTTOM[2] - COLOR_BG_TOP[2]) * mix),
        )
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

    grid_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    for x in range(0, BOARD_WIDTH, CELL_SIZE):
        pygame.draw.line(grid_surface, COLOR_GRID, (x, 0), (x, BOARD_HEIGHT))
    for y in range(0, BOARD_HEIGHT, CELL_SIZE):
        pygame.draw.line(grid_surface, COLOR_GRID, (0, y), (BOARD_WIDTH, y))

    surface.blit(grid_surface, (0, 0))
    return surface


def draw_snake(surface, snake, tick):
    radius = CELL_SIZE // 2 - 3
    shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    for index, segment in enumerate(reversed(snake)):
        real_index = len(snake) - 1 - index
        center = (
            int(segment[0] * CELL_SIZE + CELL_SIZE // 2),
            int(segment[1] * CELL_SIZE + CELL_SIZE // 2),
        )
        shadow_center = (center[0] + 2, center[1] + 4)
        gfxdraw.filled_circle(
            shadow_surface,
            shadow_center[0],
            shadow_center[1],
            radius,
            COLOR_SNAKE_SHADOW,
        )

    surface.blit(shadow_surface, (0, 0))

    for index, segment in enumerate(reversed(snake)):
        real_index = len(snake) - 1 - index
        center = (
            int(segment[0] * CELL_SIZE + CELL_SIZE // 2),
            int(segment[1] * CELL_SIZE + CELL_SIZE // 2),
        )
        pulse = (math.sin((tick / 180) + real_index * 0.55) + 1) * 0.5
        if real_index == 0:
            color = COLOR_SNAKE_HEAD
            this_radius = radius + 1
        else:
            color = (
                min(255, int(COLOR_SNAKE[0] + pulse * 18)),
                min(255, int(COLOR_SNAKE[1] + pulse * 12)),
                min(255, int(COLOR_SNAKE[2] + pulse * 6)),
            )
            this_radius = max(7, radius - min(3, real_index // 5))

        gfxdraw.filled_circle(surface, center[0], center[1], this_radius, color)
        gfxdraw.aacircle(surface, center[0], center[1], this_radius, color)

        highlight = (center[0] - this_radius // 3, center[1] - this_radius // 3)
        gfxdraw.filled_circle(surface, highlight[0], highlight[1], max(2, this_radius // 3), (220, 255, 230))

        if real_index == 0:
            eye_offset_x = 4
            eye_offset_y = 5
            for eye_x in (-eye_offset_x, eye_offset_x):
                gfxdraw.filled_circle(surface, center[0] + eye_x, center[1] - eye_offset_y, 2, (18, 40, 22))


def draw_food(surface, food, tick):
    center = (food[0] * CELL_SIZE + CELL_SIZE // 2, food[1] * CELL_SIZE + CELL_SIZE // 2)
    bob = math.sin(tick / 140) * 1.4
    center = (center[0], int(center[1] + bob))
    radius = CELL_SIZE // 2 - 4

    glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    gfxdraw.filled_circle(glow_surface, center[0], center[1], radius + 7, (255, 90, 90, 40))
    surface.blit(glow_surface, (0, 0))

    gfxdraw.filled_circle(surface, center[0], center[1], radius, COLOR_FOOD)
    gfxdraw.aacircle(surface, center[0], center[1], radius, (150, 24, 24))

    stem_rect = pygame.Rect(center[0] - 2, center[1] - radius - 5, 4, 9)
    pygame.draw.rect(surface, (86, 58, 28), stem_rect, border_radius=2)
    pygame.draw.ellipse(surface, (66, 146, 73), (center[0] + 1, center[1] - radius - 7, 10, 6))
    pygame.draw.ellipse(surface, (255, 203, 203), (center[0] - 7, center[1] - 7, 6, 8))


def draw_hud(surface, score, best_score, speed, state):
    panel = pygame.Surface((SCREEN_WIDTH - 24, HUD_HEIGHT - 18), pygame.SRCALPHA)
    pygame.draw.rect(panel, COLOR_PANEL, panel.get_rect(), border_radius=18)
    pygame.draw.rect(panel, COLOR_PANEL_BORDER, panel.get_rect(), width=2, border_radius=18)
    surface.blit(panel, (12, BOARD_HEIGHT + 8))

    row_y_top = BOARD_HEIGHT + 18
    row_y_bottom = BOARD_HEIGHT + 50
    draw_text(surface, "Snakey", 26, 28, row_y_top, color=COLOR_TEXT, bold=True)
    draw_text(surface, f"Score {score}", 23, 28, row_y_bottom, color=COLOR_ACCENT, bold=True)
    draw_text(surface, f"Best {best_score}", 21, 180, row_y_bottom, color=COLOR_TEXT)
    draw_text(surface, f"Speed {speed}", 21, 308, row_y_bottom, color=COLOR_TEXT)
    draw_text(surface, f"Length {score + 3}", 21, 418, row_y_bottom, color=COLOR_TEXT)

    state_text = {
        "menu": "Menu  |  SPACE resume/start  |  R new game  |  1/2/3 difficulty",
        "playing": "WASD/arrows move  |  P pause  |  eat apples and avoid crashing",
        "paused": "Paused  |  SPACE to continue",
        "game_over": "Game Over  |  ESC menu  |  R restart",
    }[state]
    state_img = _font(18).render(state_text, True, COLOR_TEXT_DIM)
    state_rect = state_img.get_rect(topright=(SCREEN_WIDTH - 28, row_y_top + 4))
    surface.blit(state_img, state_rect)


def draw_overlay(surface, title, subtitle):
    overlay = pygame.Surface((SCREEN_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((4, 8, 12, 125))
    surface.blit(overlay, (0, 0))

    subtitle_lines = subtitle if isinstance(subtitle, (list, tuple)) else [subtitle]
    card_height = 140 + max(0, len(subtitle_lines) - 1) * 26
    card = pygame.Rect(0, 0, 540, card_height)
    card.center = (SCREEN_WIDTH // 2, BOARD_HEIGHT // 2)
    pygame.draw.rect(surface, (10, 19, 28), card, border_radius=24)
    pygame.draw.rect(surface, COLOR_PANEL_BORDER, card, width=2, border_radius=24)

    title_img = _font(42, bold=True).render(title, True, COLOR_TEXT)
    title_rect = title_img.get_rect(center=(card.centerx, card.y + 44))
    surface.blit(title_img, title_rect)

    line_y = card.y + 92
    for line in subtitle_lines:
        subtitle_img = _font(24).render(line, True, COLOR_TEXT_DIM)
        subtitle_rect = subtitle_img.get_rect(center=(card.centerx, line_y))
        surface.blit(subtitle_img, subtitle_rect)
        line_y += 26


def check_wall_collision(pos):
    x, y = pos
    return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT
