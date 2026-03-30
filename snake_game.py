import pygame
import sys
from snake_core import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    random_food_position,
    draw_snake,
    draw_food,
    draw_hud,
    draw_overlay,
    create_background_surface,
    check_wall_collision,
)
from snake_audio import play_sound, setup_audio, start_music
from snake_session import build_game_state, interpolated_snake

# ------------- Main Game Loop -------------


def rotate_left(direction):
    return direction[1], -direction[0]


def rotate_right(direction):
    return -direction[1], direction[0]


def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snakey")
    clock = pygame.time.Clock()
    background = create_background_surface()
    audio = setup_audio()

    game = build_game_state()

    while True:
        dt = clock.tick(60) / 1000
        game.tick += 1
        settings = game.current_settings()
        speed = game.current_speed()
        step_time = 1 / speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game.state == "menu":
                    if event.key == pygame.K_c:
                        game.mode = "classic"
                        game.menu_resume_available = False
                    elif event.key == pygame.K_v:
                        game.mode = "vs"
                        game.menu_resume_available = False
                    elif event.key == pygame.K_1 and game.mode == "classic":
                        game.difficulty = "easy"
                    elif event.key == pygame.K_2 and game.mode == "classic":
                        game.difficulty = "medium"
                    elif event.key == pygame.K_3 and game.mode == "classic":
                        game.difficulty = "hard"
                    elif event.key == pygame.K_r:
                        game = build_game_state(game.difficulty, game.best_score, game.mode)
                        game.state = "playing"
                        game.menu_resume_available = True
                        start_music(audio)
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if not game.menu_resume_available:
                            game = build_game_state(game.difficulty, game.best_score, game.mode)
                        game.state = "playing"
                        if audio.get("enabled"):
                            if game.menu_resume_available:
                                audio["music_channel"].unpause()
                            else:
                                start_music(audio)
                        game.menu_resume_available = True
                    continue

                if event.key == pygame.K_ESCAPE and game.state in ("playing", "paused", "game_over"):
                    game.menu_resume_available = game.state in ("playing", "paused")
                    game.state = "menu"
                    if audio.get("enabled") and audio["music_channel"].get_busy():
                        audio["music_channel"].pause()
                    continue

                if event.key == pygame.K_SPACE:
                    if game.state == "paused":
                        game.state = "playing"
                        if audio.get("enabled"):
                            audio["music_channel"].unpause()
                    continue

                if event.key == pygame.K_p and game.state == "playing":
                    game.state = "paused"
                    if audio.get("enabled"):
                        audio["music_channel"].pause()
                    continue

                if event.key == pygame.K_r and game.state in ("game_over", "paused"):
                    game = build_game_state(game.difficulty, game.best_score, game.mode)
                    game.state = "playing"
                    game.menu_resume_available = True
                    if audio.get("enabled"):
                        audio["music_channel"].stop()
                    start_music(audio)
                    continue

                if game.mode == "classic":
                    if event.key in (pygame.K_UP, pygame.K_w) and game.direction != (0, 1):
                        if game.pending_direction != (0, -1):
                            play_sound(audio, "turn")
                        game.pending_direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and game.direction != (0, -1):
                        if game.pending_direction != (0, 1):
                            play_sound(audio, "turn")
                        game.pending_direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and game.direction != (1, 0):
                        if game.pending_direction != (-1, 0):
                            play_sound(audio, "turn")
                        game.pending_direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and game.direction != (-1, 0):
                        if game.pending_direction != (1, 0):
                            play_sound(audio, "turn")
                        game.pending_direction = (1, 0)
                else:
                    if event.key == pygame.K_UP and game.vs_red_direction != (0, 1):
                        if game.vs_red_pending_direction != (0, -1):
                            play_sound(audio, "turn")
                        game.vs_red_pending_direction = (0, -1)
                    elif event.key == pygame.K_DOWN and game.vs_red_direction != (0, -1):
                        if game.vs_red_pending_direction != (0, 1):
                            play_sound(audio, "turn")
                        game.vs_red_pending_direction = (0, 1)
                    elif event.key == pygame.K_LEFT and game.vs_red_direction != (1, 0):
                        if game.vs_red_pending_direction != (-1, 0):
                            play_sound(audio, "turn")
                        game.vs_red_pending_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and game.vs_red_direction != (-1, 0):
                        if game.vs_red_pending_direction != (1, 0):
                            play_sound(audio, "turn")
                        game.vs_red_pending_direction = (1, 0)
            if event.type == pygame.MOUSEBUTTONDOWN and game.mode == "vs" and game.state == "playing":
                if event.button == 1:
                    game.vs_green_pending_direction = rotate_left(game.vs_green_direction)
                    play_sound(audio, "turn")
                elif event.button == 3:
                    game.vs_green_pending_direction = rotate_right(game.vs_green_direction)
                    play_sound(audio, "turn")

        if game.state == "playing":
            start_music(audio)
            game.move_timer += dt
            if game.mode == "vs":
                game.vs_survival_time += dt
            while game.move_timer >= step_time:
                game.move_timer -= step_time
                if game.mode == "classic":
                    game.direction = game.pending_direction
                    game.previous_snake = list(game.snake)
                    head = (
                        game.snake[0][0] + game.direction[0],
                        game.snake[0][1] + game.direction[1],
                    )

                    hit_danger = check_wall_collision(head) or head in game.snake
                    if hit_danger:
                        game.best_score = max(game.best_score, game.score)
                        game.state = "game_over"
                        play_sound(audio, "crash")
                        if audio.get("enabled"):
                            audio["music_channel"].stop()
                        break

                    game.snake.insert(0, head)

                    if head == game.food:
                        game.score += 1
                        game.best_score = max(game.best_score, game.score)
                        play_sound(audio, "eat")
                        game.food = random_food_position(game.snake)
                    else:
                        game.snake.pop()
                else:
                    game.vs_red_direction = game.vs_red_pending_direction
                    game.vs_green_direction = game.vs_green_pending_direction
                    game.vs_red_previous_snake = list(game.vs_red_snake)
                    game.vs_green_previous_snake = list(game.vs_green_snake)

                    red_head = (
                        game.vs_red_snake[0][0] + game.vs_red_direction[0],
                        game.vs_red_snake[0][1] + game.vs_red_direction[1],
                    )
                    green_head = (
                        game.vs_green_snake[0][0] + game.vs_green_direction[0],
                        game.vs_green_snake[0][1] + game.vs_green_direction[1],
                    )

                    red_crash = check_wall_collision(red_head) or red_head in game.vs_red_snake
                    green_crash = check_wall_collision(green_head) or green_head in game.vs_green_snake
                    red_tags_green = (
                        red_head == green_head
                        or red_head in game.vs_green_snake
                        or green_head in game.vs_red_snake
                    )

                    if red_crash:
                        game.vs_winner = "Green wins"
                    elif green_crash or red_tags_green:
                        game.vs_winner = "Red wins"
                    else:
                        game.vs_winner = ""

                    if game.vs_winner:
                        game.state = "game_over"
                        play_sound(audio, "crash")
                        if audio.get("enabled"):
                            audio["music_channel"].stop()
                        break

                    red_ate = red_head == game.food
                    green_ate = green_head == game.food
                    game.vs_red_snake.insert(0, red_head)
                    if not red_ate:
                        game.vs_red_snake.pop()
                    game.vs_green_snake.insert(0, green_head)
                    if not green_ate:
                        game.vs_green_snake.pop()

                    if red_ate or green_ate:
                        play_sound(audio, "eat")
                        game.food = random_food_position(
                            game.vs_red_snake,
                            blocked=set(game.vs_green_snake),
                        )

        render_progress = game.move_timer / step_time if game.state == "playing" else 1.0
        render_snake = interpolated_snake(game.previous_snake, game.snake, render_progress)
        render_red_snake = interpolated_snake(game.vs_red_previous_snake, game.vs_red_snake, render_progress)
        render_green_snake = interpolated_snake(game.vs_green_previous_snake, game.vs_green_snake, render_progress)

        screen.blit(background, (0, 0))
        if game.mode == "classic":
            draw_food(screen, game.food, game.tick)
            draw_snake(screen, render_snake, game.tick, palette="green")
        else:
            draw_food(screen, game.food, game.tick)
            draw_snake(screen, render_green_snake, game.tick, palette="green")
            draw_snake(screen, render_red_snake, game.tick, palette="red")
        draw_hud(screen, game, speed)

        if game.state == "menu":
            if game.mode == "classic":
                menu_lines = [
                    "Choose Mode: C Classic, V VS",
                    "Choose Difficulty: 1 Easy, 2 Medium, 3 Hard",
                    f"Current Selection: {settings.label}",
                    "Press SPACE to Resume" if game.menu_resume_available else "Press SPACE to Start",
                    "Press R to Start a New Game",
                    "Press ESC during play to return here",
                ]
            else:
                menu_lines = [
                    "Choose Mode: C Classic, V VS",
                    "Red snake uses arrows",
                    "Green snake turns with mouse: left click = left, right click = right",
                    "Eat the apple to grow bigger",
                    "If red touches green, green loses",
                    "Press SPACE to Resume" if game.menu_resume_available else "Press SPACE to Start",
                    "Press R to Start a New Match",
                ]
            draw_overlay(screen, "Snakey", menu_lines)
        elif game.state == "paused":
            paused_text = "Press SPACE to continue"
            if game.mode == "vs":
                paused_text = "Press SPACE to continue the VS match"
            draw_overlay(screen, "Paused", paused_text)
        elif game.state == "game_over":
            if game.mode == "vs":
                draw_overlay(
                    screen,
                    game.vs_winner or "Game Over",
                    [
                        f"Survival Time: {game.vs_survival_time:.1f} seconds",
                        "Press ESC for menu or R to reset",
                    ],
                )
            else:
                draw_overlay(screen, "Game Over", "Press ESC for menu or R to reset")

        pygame.display.flip()


if __name__ == "__main__":
    main()
