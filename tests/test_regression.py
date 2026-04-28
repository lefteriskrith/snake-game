import unittest
from unittest.mock import patch

from src.snake_game import rotate_left, rotate_right
from src.snake_session import (
    build_game_state,
    generate_obstacles,
    interpolated_snake,
    maybe_spawn_power_up,
    obstacle_target,
)


class RotationTests(unittest.TestCase):
    def test_rotate_left_turns_clockwise_screen_up_to_left(self):
        self.assertEqual(rotate_left((0, -1)), (-1, 0))

    def test_rotate_right_turns_clockwise_screen_up_to_right(self):
        self.assertEqual(rotate_right((0, -1)), (1, 0))


class GameStateTests(unittest.TestCase):
    def test_build_game_state_keeps_best_score_across_new_run(self):
        game = build_game_state(difficulty="hard", best_score=12, mode="classic")

        self.assertEqual(game.best_score, 12)
        self.assertEqual(game.difficulty, "hard")
        self.assertEqual(game.mode, "classic")
        self.assertEqual(game.state, "menu")

    def test_classic_speed_scales_with_score_and_caps_at_max(self):
        game = build_game_state(difficulty="medium")

        self.assertEqual(game.current_speed(), 6)

        game.score = 11
        self.assertEqual(game.current_speed(), 8)

        game.score = 99
        self.assertEqual(game.current_speed(), 14)

    def test_vs_mode_uses_fixed_speed_bonus(self):
        game = build_game_state(mode="vs")
        game.score = 999

        self.assertEqual(game.current_speed(), 2.0)

    def test_vs_mode_food_avoids_both_snakes(self):
        forced_food = (3, 4)
        with patch("src.snake_session.random_food_position", return_value=forced_food) as random_food:
            game = build_game_state(mode="vs")

        self.assertEqual(game.food, forced_food)
        self.assertNotIn(game.food, game.vs_red_snake)
        self.assertNotIn(game.food, game.vs_green_snake)
        random_food.assert_called_once_with(game.vs_red_snake, blocked=set(game.vs_green_snake))

    def test_obstacles_mode_starts_with_obstacles_and_theme(self):
        game = build_game_state(mode="obstacles", theme="lava")

        self.assertTrue(game.obstacle_mode)
        self.assertEqual(game.theme, "lava")
        self.assertEqual(len(game.obstacles), 3)
        self.assertTrue(all(obstacle not in game.snake for obstacle in game.obstacles))
        self.assertNotIn(game.food, game.obstacles)


class ProgressionHelpersTests(unittest.TestCase):
    def test_obstacle_target_scales_with_score_and_caps(self):
        self.assertEqual(obstacle_target(0), 0)
        self.assertEqual(obstacle_target(9), 3)
        self.assertEqual(obstacle_target(999), 18)

    def test_generate_obstacles_respects_snake_food_and_blocked_cells(self):
        snake = [(10, 10), (9, 10), (8, 10)]
        food = (15, 10)
        blocked = {(20, 20)}

        with patch(
            "src.snake_session.random_open_cell",
            side_effect=[(10, 11), (15, 10), (20, 20), (3, 3), (7, 7)],
        ):
            obstacles = generate_obstacles(2, snake, food, blocked=blocked)

        self.assertEqual(obstacles, [(3, 3), (7, 7)])

    def test_maybe_spawn_power_up_cycles_types_every_three_points(self):
        snake = [(10, 10), (9, 10), (8, 10)]
        food = (5, 5)
        obstacles = [(7, 7)]

        with patch("src.snake_session.random_open_cell", return_value=(4, 4)):
            power_up, power_up_type = maybe_spawn_power_up(snake, food, obstacles, 3, "")
        self.assertEqual((power_up, power_up_type), ((4, 4), "speed_boost"))

        with patch("src.snake_session.random_open_cell", return_value=(6, 6)):
            power_up, power_up_type = maybe_spawn_power_up(snake, food, obstacles, 6, "")
        self.assertEqual((power_up, power_up_type), ((6, 6), "slow_time"))


class InterpolationTests(unittest.TestCase):
    def test_interpolated_snake_clamps_progress(self):
        previous = [(1, 1), (0, 1)]
        current = [(2, 1), (1, 1)]

        self.assertEqual(interpolated_snake(previous, current, -1.0), previous)
        self.assertEqual(interpolated_snake(previous, current, 2.0), current)

    def test_interpolated_snake_handles_growth_by_reusing_last_previous_segment(self):
        previous = [(5, 5), (4, 5)]
        current = [(6, 5), (5, 5), (4, 5)]

        self.assertEqual(
            interpolated_snake(previous, current, 0.5),
            [(5.5, 5.0), (4.5, 5.0), (4.0, 5.0)],
        )


if __name__ == "__main__":
    unittest.main()
