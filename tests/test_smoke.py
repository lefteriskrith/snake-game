import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.snake_core import (
    BOARD_HEIGHT,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    create_background_surface,
    draw_food,
    draw_hud,
    draw_menu_overlay,
    draw_obstacles,
    draw_power_up,
    draw_snake,
    draw_text_fit,
)
from src.snake_session import build_game_state


class RenderingSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_text_fit_stays_inside_requested_width(self):
        surface = pygame.Surface((220, 80), pygame.SRCALPHA)

        rect = draw_text_fit(
            surface,
            "Rocks grow in as your score climbs",
            18,
            10,
            10,
            140,
            min_size=10,
        )

        self.assertLessEqual(rect.width, 140)

    def test_menu_overlay_renders_all_modes_without_text_panel_crashes(self):
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for mode in ("classic", "obstacles", "vs"):
            with self.subTest(mode=mode):
                game = build_game_state(mode=mode)
                game.tick = 12
                surface.blit(create_background_surface(game.theme), (0, 0))
                draw_hud(surface, game, game.current_speed())
                draw_menu_overlay(surface, game)

                self.assertIsNotNone(surface.get_bounding_rect())

    def test_playfield_smoke_renders_active_game_layers(self):
        surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        game = build_game_state(mode="obstacles", theme="neon")
        game.state = "playing"
        game.power_up = (4, 4)
        game.power_up_type = "shield"

        surface.blit(create_background_surface(game.theme), (0, 0))
        draw_obstacles(surface, game.obstacles, game.tick, game.theme)
        draw_food(surface, game.food, game.tick)
        draw_power_up(surface, game.power_up, game.power_up_type, game.tick, game.theme)
        draw_snake(surface, game.snake, game.tick)
        draw_hud(surface, game, game.current_speed())

        self.assertGreater(surface.get_bounding_rect().height, BOARD_HEIGHT)


if __name__ == "__main__":
    unittest.main()
