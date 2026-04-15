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
COLOR_GRID = (255, 255, 255, 18)
COLOR_PANEL = (7, 12, 18, 210)
COLOR_PANEL_BORDER = (90, 141, 108)
COLOR_SNAKE = (70, 214, 123)
COLOR_SNAKE_HEAD = (153, 255, 196)
COLOR_SNAKE_SHADOW = (10, 40, 20, 90)
COLOR_RED_SNAKE = (224, 70, 70)
COLOR_RED_SNAKE_HEAD = (255, 151, 151)
COLOR_RED_SNAKE_SHADOW = (55, 10, 10, 90)
COLOR_FOOD = (230, 76, 70)
COLOR_TEXT = (239, 247, 241)
COLOR_TEXT_DIM = (148, 176, 154)
COLOR_ACCENT = (255, 211, 107)

THEME_VISUALS = {
    "forest": {
        "bg_top": (8, 17, 24),
        "bg_bottom": (18, 34, 22),
        "panel": (7, 12, 18, 210),
        "border": (90, 141, 108),
        "accent": (255, 211, 107),
        "grid": (255, 255, 255, 18),
        "glow": (116, 196, 141, 60),
    },
    "neon": {
        "bg_top": (6, 10, 28),
        "bg_bottom": (18, 6, 38),
        "panel": (15, 9, 32, 225),
        "border": (76, 238, 226),
        "accent": (255, 98, 196),
        "grid": (103, 245, 255, 24),
        "glow": (121, 62, 255, 72),
    },
    "lava": {
        "bg_top": (35, 10, 5),
        "bg_bottom": (66, 23, 6),
        "panel": (42, 11, 6, 228),
        "border": (255, 132, 68),
        "accent": (255, 205, 99),
        "grid": (255, 190, 110, 20),
        "glow": (255, 120, 45, 68),
    },
    "ice": {
        "bg_top": (8, 28, 42),
        "bg_bottom": (18, 60, 88),
        "panel": (8, 24, 34, 218),
        "border": (138, 225, 255),
        "accent": (193, 243, 255),
        "grid": (210, 242, 255, 26),
        "glow": (167, 229, 255, 70),
    },
}


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


def _theme_colors(theme):
    return THEME_VISUALS.get(theme, THEME_VISUALS["forest"])


def create_background_surface(theme="forest"):
    colors = _theme_colors(theme)
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        mix = y / SCREEN_HEIGHT
        color = (
            int(colors["bg_top"][0] + (colors["bg_bottom"][0] - colors["bg_top"][0]) * mix),
            int(colors["bg_top"][1] + (colors["bg_bottom"][1] - colors["bg_top"][1]) * mix),
            int(colors["bg_top"][2] + (colors["bg_bottom"][2] - colors["bg_top"][2]) * mix),
        )
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

    for orb_x, orb_y, radius in ((85, 96, 120), (SCREEN_WIDTH - 110, 140, 160), (SCREEN_WIDTH // 2, BOARD_HEIGHT - 50, 180)):
        glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(glow, colors["glow"], (orb_x, orb_y), radius)
        surface.blit(glow, (0, 0))

    grid_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    for x in range(0, BOARD_WIDTH, CELL_SIZE):
        pygame.draw.line(grid_surface, colors["grid"], (x, 0), (x, BOARD_HEIGHT))
    for y in range(0, BOARD_HEIGHT, CELL_SIZE):
        pygame.draw.line(grid_surface, colors["grid"], (0, y), (BOARD_WIDTH, y))

    surface.blit(grid_surface, (0, 0))
    return surface


def draw_snake(surface, snake, tick, palette="green"):
    palettes = {
        "green": {
            "body": COLOR_SNAKE,
            "head": COLOR_SNAKE_HEAD,
            "shadow": COLOR_SNAKE_SHADOW,
            "highlight": (220, 255, 230),
            "eye": (18, 40, 22),
        },
        "red": {
            "body": COLOR_RED_SNAKE,
            "head": COLOR_RED_SNAKE_HEAD,
            "shadow": COLOR_RED_SNAKE_SHADOW,
            "highlight": (255, 224, 224),
            "eye": (70, 18, 18),
        },
    }
    colors = palettes[palette]
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
            colors["shadow"],
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
            color = colors["head"]
            this_radius = radius + 1
        else:
            color = (
                min(255, int(colors["body"][0] + pulse * 18)),
                min(255, int(colors["body"][1] + pulse * 12)),
                min(255, int(colors["body"][2] + pulse * 6)),
            )
            this_radius = max(7, radius - min(3, real_index // 5))

        gfxdraw.filled_circle(surface, center[0], center[1], this_radius, color)
        gfxdraw.aacircle(surface, center[0], center[1], this_radius, color)

        highlight = (center[0] - this_radius // 3, center[1] - this_radius // 3)
        gfxdraw.filled_circle(surface, highlight[0], highlight[1], max(2, this_radius // 3), colors["highlight"])

        if real_index == 0:
            eye_offset_x = 4
            eye_offset_y = 5
            for eye_x in (-eye_offset_x, eye_offset_x):
                gfxdraw.filled_circle(surface, center[0] + eye_x, center[1] - eye_offset_y, 2, colors["eye"])


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


def draw_obstacles(surface, obstacles, tick, theme="forest"):
    if not obstacles:
        return
    colors = _theme_colors(theme)
    pulse = (math.sin(tick / 180) + 1) * 0.5
    for obstacle in obstacles:
        rect = pygame.Rect(
            obstacle[0] * CELL_SIZE + 4,
            obstacle[1] * CELL_SIZE + 4,
            CELL_SIZE - 8,
            CELL_SIZE - 8,
        )
        fill = (
            min(255, int(colors["border"][0] + pulse * 18)),
            min(255, int(colors["border"][1] + pulse * 14)),
            min(255, int(colors["border"][2] + pulse * 8)),
        )
        pygame.draw.rect(surface, (8, 12, 18), rect.move(2, 4), border_radius=8)
        pygame.draw.rect(surface, fill, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_TEXT, rect, width=1, border_radius=8)


def draw_power_up(surface, power_up, power_up_type, tick, theme="forest"):
    if not power_up or not power_up_type:
        return
    colors = _theme_colors(theme)
    center = (power_up[0] * CELL_SIZE + CELL_SIZE // 2, power_up[1] * CELL_SIZE + CELL_SIZE // 2)
    bob = math.sin(tick / 90) * 2
    center = (center[0], int(center[1] + bob))
    glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(glow, colors["glow"], center, CELL_SIZE // 2 + 8)
    surface.blit(glow, (0, 0))

    badge_colors = {
        "speed_boost": (255, 208, 78),
        "slow_time": (128, 209, 255),
        "shield": (166, 255, 184),
        "double_score": (255, 114, 175),
    }
    labels = {
        "speed_boost": "S",
        "slow_time": "T",
        "shield": "H",
        "double_score": "2",
    }
    color = badge_colors[power_up_type]
    gfxdraw.filled_circle(surface, center[0], center[1], CELL_SIZE // 2 - 5, color)
    gfxdraw.aacircle(surface, center[0], center[1], CELL_SIZE // 2 - 5, COLOR_TEXT)
    draw_text(surface, labels[power_up_type], 24, center[0] - 8, center[1] - 16, color=(14, 20, 24), bold=True)


def draw_particles(surface, particles):
    for particle in particles:
        radius = max(1, int(particle["radius"]))
        pos = (int(particle["x"]), int(particle["y"]))
        color = particle["color"]
        particle_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        alpha = max(18, min(255, int(particle["life"] * 255)))
        pygame.draw.circle(
            particle_surface,
            (color[0], color[1], color[2], alpha),
            (radius * 2, radius * 2),
            radius,
        )
        surface.blit(particle_surface, (pos[0] - radius * 2, pos[1] - radius * 2))


def draw_hud(surface, game, speed):
    colors = _theme_colors(game.theme)
    panel = pygame.Surface((SCREEN_WIDTH - 24, HUD_HEIGHT - 18), pygame.SRCALPHA)
    pygame.draw.rect(panel, colors["panel"], panel.get_rect(), border_radius=18)
    pygame.draw.rect(panel, colors["border"], panel.get_rect(), width=2, border_radius=18)
    surface.blit(panel, (12, BOARD_HEIGHT + 8))

    row_y_top = BOARD_HEIGHT + 18
    row_y_bottom = BOARD_HEIGHT + 50
    draw_text(surface, "Snakey", 26, 28, row_y_top, color=COLOR_TEXT, bold=True)
    if game.mode == "classic":
        draw_text(surface, f"Score {game.score}", 23, 28, row_y_bottom, color=colors["accent"], bold=True)
        draw_text(surface, f"Best {game.best_score}", 21, 180, row_y_bottom, color=COLOR_TEXT)
        draw_text(surface, f"Speed {speed}", 21, 308, row_y_bottom, color=COLOR_TEXT)
        draw_text(surface, f"Length {game.score + 3}", 21, 418, row_y_bottom, color=COLOR_TEXT)
        state_text = {
            "menu": "Classic  |  C classic  |  V VS  |  SPACE resume/start  |  R new game  |  1/2/3 difficulty",
            "playing": "Classic  |  WASD/arrows move  |  P pause",
            "paused": "Classic paused  |  SPACE to continue",
            "game_over": "Classic game over  |  ESC menu  |  R restart",
        }[game.state]
    elif game.mode == "obstacles":
        draw_text(surface, f"Score {game.score}", 23, 28, row_y_bottom, color=colors["accent"], bold=True)
        draw_text(surface, f"Best {game.best_score}", 21, 180, row_y_bottom, color=COLOR_TEXT)
        draw_text(surface, f"Rocks {len(game.obstacles)}", 21, 308, row_y_bottom, color=COLOR_TEXT)
        draw_text(surface, f"Power {game.active_power_up or 'none'}", 21, 430, row_y_bottom, color=COLOR_TEXT)
        state_text = {
            "menu": "Obstacles  |  O mode  |  T theme  |  SPACE resume/start  |  R new run",
            "playing": "Obstacles  |  avoid rocks  |  collect power-ups  |  P pause",
            "paused": "Obstacles paused  |  SPACE to continue",
            "game_over": "Obstacles over  |  ESC menu  |  R restart",
        }[game.state]
    else:
        draw_text(surface, "VS Mode", 23, 28, row_y_bottom, color=colors["accent"], bold=True)
        draw_text(surface, f"Time {game.vs_survival_time:.1f}s", 21, 160, row_y_bottom, color=COLOR_TEXT)
        draw_text(surface, f"Red {len(game.vs_red_snake)}", 21, 318, row_y_bottom, color=COLOR_RED_SNAKE_HEAD)
        draw_text(surface, f"Green {len(game.vs_green_snake)}", 21, 436, row_y_bottom, color=COLOR_SNAKE_HEAD)
        state_text = {
            "menu": "VS  |  C classic  |  V VS  |  SPACE resume/start  |  R new match",
            "playing": "VS  |  Red: arrows  |  Green: left click turn left, right click turn right",
            "paused": "VS paused  |  SPACE to continue",
            "game_over": "VS ended  |  ESC menu  |  R restart",
        }[game.state]
    state_img = _font(18).render(state_text, True, COLOR_TEXT_DIM)
    state_rect = state_img.get_rect(topright=(SCREEN_WIDTH - 28, row_y_top + 4))
    surface.blit(state_img, state_rect)
    draw_text(surface, game.current_theme().label, 19, SCREEN_WIDTH - 130, row_y_bottom, color=colors["accent"], bold=True)


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


def draw_menu_overlay(surface, game):
    colors = _theme_colors(game.theme)
    overlay = pygame.Surface((SCREEN_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((3, 8, 12, 118))
    surface.blit(overlay, (0, 0))

    title_offset = math.sin(game.tick / 18) * 4
    draw_text(surface, "Snakey", 54, 36, 42 + int(title_offset), color=COLOR_TEXT, bold=True)
    draw_text(surface, "Arcade remix: themes, power-ups, VS and obstacle runs", 21, 40, 100, color=COLOR_TEXT_DIM)

    card_specs = [
        ("classic", "Classic", "Pure run with difficulty scaling", "WASD or arrows"),
        ("obstacles", "Obstacles", "Rocks grow in as your score climbs", "Power-ups enabled"),
        ("vs", "VS Duel", "Red arrows vs green mouse turns", "Fast local battle"),
    ]
    card_width = 188
    card_height = 180
    top = 160
    left = 32
    gap = 18
    for index, (mode_key, title, line_one, line_two) in enumerate(card_specs):
        x = left + index * (card_width + gap)
        selected = game.menu_card_index == index
        active = game.mode == mode_key
        pulse = 0
        if selected:
            pulse = math.sin(game.tick / 14 + index) * 5
        rect = pygame.Rect(x, top + int(pulse), card_width, card_height)
        fill = (15, 20, 28, 228) if not selected else colors["panel"]
        border = colors["border"] if (selected or active) else (78, 90, 102)
        pygame.draw.rect(surface, fill, rect, border_radius=22)
        pygame.draw.rect(surface, border, rect, width=3 if selected else 2, border_radius=22)
        if active:
            ribbon = pygame.Rect(rect.x + 14, rect.y + 14, 72, 26)
            pygame.draw.rect(surface, colors["accent"], ribbon, border_radius=13)
            draw_text(surface, "ACTIVE", 16, ribbon.x + 10, ribbon.y + 3, color=(18, 26, 30), bold=True)
        draw_text(surface, title, 30, rect.x + 18, rect.y + 54, color=COLOR_TEXT, bold=True)
        draw_text(surface, line_one, 18, rect.x + 18, rect.y + 98, color=COLOR_TEXT_DIM)
        draw_text(surface, line_two, 18, rect.x + 18, rect.y + 124, color=COLOR_TEXT_DIM)
        footer = "SPACE to launch" if selected else "Use left/right"
        draw_text(surface, footer, 18, rect.x + 18, rect.y + 150, color=colors["accent"])

    theme_box = pygame.Rect(40, 380, 548, 88)
    pygame.draw.rect(surface, (10, 16, 24, 220), theme_box, border_radius=20)
    pygame.draw.rect(surface, colors["border"], theme_box, width=2, border_radius=20)
    draw_text(surface, "Theme", 26, theme_box.x + 20, theme_box.y + 18, color=COLOR_TEXT, bold=True)
    draw_text(surface, f"{game.current_theme().label} arena", 24, theme_box.x + 140, theme_box.y + 20, color=colors["accent"], bold=True)
    draw_text(surface, "T cycles themes, 1/2/3 changes difficulty, ENTER/SPACE starts, R resets", 18, theme_box.x + 20, theme_box.y + 52, color=COLOR_TEXT_DIM)


def check_wall_collision(pos):
    x, y = pos
    return x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT
