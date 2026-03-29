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
                    if event.key == pygame.K_1:
                        game.difficulty = "easy"
                    elif event.key == pygame.K_2:
                        game.difficulty = "medium"
                    elif event.key == pygame.K_3:
                        game.difficulty = "hard"
                    elif event.key == pygame.K_r:
                        game = build_game_state(game.difficulty, game.best_score)
                        game.state = "playing"
                        game.menu_resume_available = True
                        start_music(audio)
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if not game.menu_resume_available:
                            game = build_game_state(game.difficulty, game.best_score)
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
                elif event.key == pygame.K_SPACE:
                    if game.state == "paused":
                        game.state = "playing"
                        if audio.get("enabled"):
                            audio["music_channel"].unpause()
                elif event.key == pygame.K_p and game.state == "playing":
                    game.state = "paused"
                    if audio.get("enabled"):
                        audio["music_channel"].pause()
                elif event.key == pygame.K_r and game.state in ("game_over", "paused"):
                    game = build_game_state(game.difficulty, game.best_score)
                    game.state = "playing"
                    game.menu_resume_available = True
                    if audio.get("enabled"):
                        audio["music_channel"].stop()
                    start_music(audio)

        if game.state == "playing":
            start_music(audio)
            game.move_timer += dt
            while game.move_timer >= step_time:
                game.move_timer -= step_time
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

        render_progress = game.move_timer / step_time if game.state == "playing" else 1.0
        render_snake = interpolated_snake(game.previous_snake, game.snake, render_progress)

        screen.blit(background, (0, 0))
        draw_food(screen, game.food, game.tick)
        draw_snake(screen, render_snake, game.tick)
        draw_hud(screen, game.score, game.best_score, speed, game.state)

        if game.state == "menu":
            draw_overlay(
                screen,
                "Snakey",
                [
                    "Choose Difficulty: 1 Easy, 2 Medium, 3 Hard",
                    f"Current Selection: {settings.label}",
                    "Press SPACE to Resume" if game.menu_resume_available else "Press SPACE to Start",
                    "Press R to Start a New Game",
                    "Press ESC during play to return here",
                ],
            )
        elif game.state == "paused":
            draw_overlay(screen, "Paused", "Press SPACE to continue")
        elif game.state == "game_over":
            draw_overlay(screen, "Game Over", "Press ESC for menu or R to reset")

        pygame.display.flip()


if __name__ == "__main__":
    main()
