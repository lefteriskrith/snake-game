import math
import random

import pygame
from pygame import gfxdraw

# ------------- Settings -------------
CELL_SIZE = 28
GRID_WIDTH = 34
GRID_HEIGHT = 24
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
COLOR_WALL = (39, 70, 51)
COLOR_WALL_EDGE = (94, 158, 111)
COLOR_ACCENT = (255, 211, 107)
COLOR_DANGER = (255, 96, 96)
COLOR_DANGER_EDGE = (255, 186, 186)
COLOR_DANGER_MOVING = (255, 136, 66)
COLOR_DANGER_MOVING_EDGE = (255, 211, 166)
COLOR_BONUS_SHIELD = (90, 205, 255)
COLOR_BONUS_GOLD = (255, 218, 92)
COLOR_BONUS_SLOW = (162, 255, 142)


def _font(size, bold=False):
    return pygame.font.SysFont("arialroundedmtbold", size, bold=bold)


def draw_text(surface, text, size, x, y, color=COLOR_TEXT, bold=False):
    text_img = _font(size, bold=bold).render(text, True, color)
    surface.blit(text_img, (x, y))


def random_food_position(snake, blocked=None):
    blocked = blocked or set()
    while True:
        pos = (random.randint(1, GRID_WIDTH - 2), random.randint(1, GRID_HEIGHT - 2))
        if pos not in snake and pos not in blocked:
            return pos


def random_bonus_position(snake, blocked=None):
    return random_food_position(snake, blocked)


def create_obstacles():
    return [
        {"type": "static", "pos": (6, 6)},
        {"type": "static", "pos": (27, 6)},
        {"type": "static", "pos": (6, 17)},
        {"type": "static", "pos": (27, 17)},
        {"type": "moving", "pos": [12, 9], "axis": "x", "min": 12, "max": 21, "dir": 1, "period": 3, "timer": 0},
        {"type": "moving", "pos": [21, 14], "axis": "x", "min": 12, "max": 21, "dir": -1, "period": 4, "timer": 0},
        {"type": "moving", "pos": [17, 8], "axis": "y", "min": 8, "max": 15, "dir": 1, "period": 5, "timer": 0},
    ]


def obstacle_positions(obstacles):
    positions = set()
    for obstacle in obstacles:
        pos = obstacle["pos"]
        positions.add(tuple(pos) if isinstance(pos, list) else pos)
    return positions


def check_obstacle_collision(pos, obstacles):
    return pos in obstacle_positions(obstacles)


def update_obstacles(obstacles, snake, food):
    occupied = set(snake)
    if food:
        occupied.add(food)

    for obstacle in obstacles:
        if obstacle["type"] != "moving":
            continue

        obstacle["timer"] += 1
        if obstacle["timer"] < obstacle["period"]:
            continue

        obstacle["timer"] = 0
        axis = obstacle["axis"]
        current_x, current_y = obstacle["pos"]
        delta_x = obstacle["dir"] if axis == "x" else 0
        delta_y = obstacle["dir"] if axis == "y" else 0
        next_pos = (current_x + delta_x, current_y + delta_y)
        next_axis_value = next_pos[0] if axis == "x" else next_pos[1]

        if next_axis_value < obstacle["min"] or next_axis_value > obstacle["max"] or next_pos in occupied:
            obstacle["dir"] *= -1
            delta_x = obstacle["dir"] if axis == "x" else 0
            delta_y = obstacle["dir"] if axis == "y" else 0
            next_pos = (current_x + delta_x, current_y + delta_y)
            next_axis_value = next_pos[0] if axis == "x" else next_pos[1]
            if next_axis_value < obstacle["min"] or next_axis_value > obstacle["max"] or next_pos in occupied:
                continue

        obstacle["pos"][0] = next_pos[0]
        obstacle["pos"][1] = next_pos[1]


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


def draw_board_frame(surface):
    pygame.draw.rect(surface, COLOR_WALL, (0, 0, BOARD_WIDTH, CELL_SIZE))
    pygame.draw.rect(surface, COLOR_WALL, (0, BOARD_HEIGHT - CELL_SIZE, BOARD_WIDTH, CELL_SIZE))
    pygame.draw.rect(surface, COLOR_WALL, (0, 0, CELL_SIZE, BOARD_HEIGHT))
    pygame.draw.rect(surface, COLOR_WALL, (BOARD_WIDTH - CELL_SIZE, 0, CELL_SIZE, BOARD_HEIGHT))

    pygame.draw.line(surface, COLOR_WALL_EDGE, (0, CELL_SIZE), (BOARD_WIDTH, CELL_SIZE), 2)
    pygame.draw.line(surface, COLOR_WALL_EDGE, (0, BOARD_HEIGHT - CELL_SIZE), (BOARD_WIDTH, BOARD_HEIGHT - CELL_SIZE), 2)
    pygame.draw.line(surface, COLOR_WALL_EDGE, (CELL_SIZE, 0), (CELL_SIZE, BOARD_HEIGHT), 2)
    pygame.draw.line(surface, COLOR_WALL_EDGE, (BOARD_WIDTH - CELL_SIZE, 0), (BOARD_WIDTH - CELL_SIZE, BOARD_HEIGHT), 2)


def draw_snake(surface, snake, tick):
    radius = CELL_SIZE // 2 - 3
    shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    for index, segment in enumerate(reversed(snake)):
        real_index = len(snake) - 1 - index
        center = (
            segment[0] * CELL_SIZE + CELL_SIZE // 2,
            segment[1] * CELL_SIZE + CELL_SIZE // 2,
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
            segment[0] * CELL_SIZE + CELL_SIZE // 2,
            segment[1] * CELL_SIZE + CELL_SIZE // 2,
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


def draw_bonus(surface, bonus, tick):
    if not bonus:
        return

    center = (bonus["pos"][0] * CELL_SIZE + CELL_SIZE // 2, bonus["pos"][1] * CELL_SIZE + CELL_SIZE // 2)
    bob = math.sin((tick / 70) + center[0]) * 2.0
    center = (center[0], int(center[1] + bob))
    radius = CELL_SIZE // 2 - 5
    kind = bonus["kind"]

    if kind == "shield":
        main_color = COLOR_BONUS_SHIELD
        glow_color = (116, 221, 255, 44)
    elif kind == "score":
        main_color = COLOR_BONUS_GOLD
        glow_color = (255, 224, 110, 48)
    else:
        main_color = COLOR_BONUS_SLOW
        glow_color = (170, 255, 142, 42)

    glow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    gfxdraw.filled_circle(glow_surface, center[0], center[1], radius + 8, glow_color)
    surface.blit(glow_surface, (0, 0))

    gfxdraw.filled_circle(surface, center[0], center[1], radius, main_color)
    gfxdraw.aacircle(surface, center[0], center[1], radius, (245, 250, 255))
    gfxdraw.filled_circle(surface, center[0] - 3, center[1] - 3, max(2, radius // 3), (255, 255, 255))

    if kind == "shield":
        pygame.draw.circle(surface, (235, 250, 255), center, radius - 4, width=2)
    elif kind == "score":
        points = []
        for point_index in range(10):
            angle = (math.tau / 10) * point_index - math.pi / 2
            distance = radius - 1 if point_index % 2 == 0 else radius // 2
            points.append((int(center[0] + math.cos(angle) * distance), int(center[1] + math.sin(angle) * distance)))
        pygame.draw.polygon(surface, (90, 64, 10), points)
    else:
        pygame.draw.line(surface, (20, 80, 40), (center[0] - 6, center[1]), (center[0] + 6, center[1]), 3)
        pygame.draw.line(surface, (20, 80, 40), (center[0], center[1] - 6), (center[0], center[1] + 6), 3)


def draw_obstacles(surface, obstacles, tick):
    shadow_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for obstacle in obstacles:
        pos = obstacle["pos"]
        grid_x, grid_y = tuple(pos) if isinstance(pos, list) else pos
        center_x = grid_x * CELL_SIZE + CELL_SIZE // 2
        center_y = grid_y * CELL_SIZE + CELL_SIZE // 2

        if obstacle["type"] == "static":
            radius = CELL_SIZE // 2 - 5
            gfxdraw.filled_circle(shadow_surface, center_x + 2, center_y + 4, radius + 1, (0, 0, 0, 70))
        else:
            radius = CELL_SIZE // 2 - 6
            bob = math.sin((tick / 90) + grid_x) * 1.5
            center_y = int(center_y + bob)
            glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            gfxdraw.filled_circle(glow, center_x, center_y, radius + 7, (255, 116, 66, 44))
            surface.blit(glow, (0, 0))
            gfxdraw.filled_circle(shadow_surface, center_x + 2, center_y + 4, radius + 1, (0, 0, 0, 85))

    surface.blit(shadow_surface, (0, 0))

    for obstacle in obstacles:
        pos = obstacle["pos"]
        grid_x, grid_y = tuple(pos) if isinstance(pos, list) else pos
        center_x = grid_x * CELL_SIZE + CELL_SIZE // 2
        center_y = grid_y * CELL_SIZE + CELL_SIZE // 2

        if obstacle["type"] == "static":
            radius = CELL_SIZE // 2 - 5
            points = []
            for point_index in range(10):
                angle = (math.tau / 10) * point_index + (grid_x * 0.2)
                distance = radius + 3 if point_index % 2 == 0 else radius - 3
                points.append(
                    (
                        int(center_x + math.cos(angle) * distance),
                        int(center_y + math.sin(angle) * distance),
                    )
                )
            pygame.draw.polygon(surface, COLOR_DANGER, points)
            pygame.draw.polygon(surface, COLOR_DANGER_EDGE, points, width=2)
            pygame.draw.circle(surface, (255, 240, 240), (center_x - 3, center_y - 4), 3)
        else:
            radius = CELL_SIZE // 2 - 6
            bob = math.sin((tick / 90) + grid_x) * 1.5
            center_y = int(center_y + bob)
            gfxdraw.filled_circle(surface, center_x, center_y, radius, COLOR_DANGER_MOVING)
            gfxdraw.aacircle(surface, center_x, center_y, radius, COLOR_DANGER_MOVING_EDGE)
            for spoke in range(4):
                angle = (math.pi / 2) * spoke + (tick / 35)
                start = (int(center_x + math.cos(angle) * 2), int(center_y + math.sin(angle) * 2))
                end = (int(center_x + math.cos(angle) * (radius + 2)), int(center_y + math.sin(angle) * (radius + 2)))
                pygame.draw.line(surface, (120, 34, 14), start, end, 2)
            gfxdraw.filled_circle(surface, center_x - 3, center_y - 3, max(2, radius // 3), (255, 233, 220))


def draw_hud(surface, score, best_score, speed, state, obstacle_count, active_bonus=None, shield_steps=0):
    panel = pygame.Surface((SCREEN_WIDTH - 24, HUD_HEIGHT - 18), pygame.SRCALPHA)
    pygame.draw.rect(panel, COLOR_PANEL, panel.get_rect(), border_radius=18)
    pygame.draw.rect(panel, COLOR_PANEL_BORDER, panel.get_rect(), width=2, border_radius=18)
    surface.blit(panel, (12, BOARD_HEIGHT + 8))

    row_y_top = BOARD_HEIGHT + 18
    row_y_bottom = BOARD_HEIGHT + 50
    draw_text(surface, "snake-game", 26, 28, row_y_top, color=COLOR_TEXT, bold=True)
    draw_text(surface, f"Score {score}", 23, 28, row_y_bottom, color=COLOR_ACCENT, bold=True)
    draw_text(surface, f"Best {best_score}", 21, 180, row_y_bottom, color=COLOR_TEXT)
    draw_text(surface, f"Speed {speed}", 21, 308, row_y_bottom, color=COLOR_TEXT)
    draw_text(surface, f"Danger {obstacle_count}", 21, 418, row_y_bottom, color=COLOR_TEXT)

    bonus_label = "None"
    if active_bonus:
        bonus_label = active_bonus.replace("_", " ").title()
    elif shield_steps > 0:
        bonus_label = f"Shield {shield_steps}"
    draw_text(surface, f"Bonus {bonus_label}", 21, 570, row_y_bottom, color=COLOR_TEXT)

    state_text = {
        "start": "SPACE starts the run",
        "playing": "WASD/arrows move  |  P pause  |  red hazards are bad",
        "paused": "Paused  |  SPACE to continue",
        "game_over": "Game over  |  R to retry",
    }[state]
    state_img = _font(18).render(state_text, True, COLOR_TEXT_DIM)
    state_rect = state_img.get_rect(topright=(SCREEN_WIDTH - 28, row_y_top + 4))
    surface.blit(state_img, state_rect)


def draw_overlay(surface, title, subtitle):
    overlay = pygame.Surface((SCREEN_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((4, 8, 12, 125))
    surface.blit(overlay, (0, 0))

    card = pygame.Rect(0, 0, 420, 140)
    card.center = (SCREEN_WIDTH // 2, BOARD_HEIGHT // 2)
    pygame.draw.rect(surface, (10, 19, 28), card, border_radius=24)
    pygame.draw.rect(surface, COLOR_PANEL_BORDER, card, width=2, border_radius=24)

    title_img = _font(42, bold=True).render(title, True, COLOR_TEXT)
    title_rect = title_img.get_rect(center=(card.centerx, card.y + 44))
    surface.blit(title_img, title_rect)

    subtitle_img = _font(24).render(subtitle, True, COLOR_TEXT_DIM)
    subtitle_rect = subtitle_img.get_rect(center=(card.centerx, card.y + 92))
    surface.blit(subtitle_img, subtitle_rect)


def draw_walls(surface):
    draw_board_frame(surface)


def check_wall_collision(pos):
    x, y = pos
    return x <= 0 or x >= GRID_WIDTH - 1 or y <= 0 or y >= GRID_HEIGHT - 1
