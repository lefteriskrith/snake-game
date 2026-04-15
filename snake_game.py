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
    draw_menu_overlay,
    draw_obstacles,
    draw_power_up,
    draw_particles,
)
from snake_audio import play_sound, setup_audio, start_music
from snake_session import (
    MODE_ORDER,
    POWER_UP_DURATION,
    THEME_ORDER,
    build_game_state,
    generate_obstacles,
    interpolated_snake,
    maybe_spawn_power_up,
    obstacle_target,
)

# ------------- Main Game Loop -------------


def rotate_left(direction):
    return direction[1], -direction[0]


def rotate_right(direction):
    return -direction[1], direction[0]


def cycle_value(options, current, step):
    index = options.index(current)
    return options[(index + step) % len(options)]


def emit_particles(game, cell, color, amount=12, speed=1.0):
    center_x = cell[0] * 28 + 14
    center_y = cell[1] * 28 + 14
    for index in range(amount):
        angle = (index / max(1, amount)) * 6.28318
        velocity = 0.7 + (index % 4) * 0.25
        game.particles.append(
            {
                "x": center_x,
                "y": center_y,
                "vx": pygame.math.Vector2(velocity * speed, 0).rotate_rad(angle).x,
                "vy": pygame.math.Vector2(velocity * speed, 0).rotate_rad(angle).y,
                "life": 1.0,
                "radius": 2 + (index % 3),
                "color": color,
            }
        )


def update_particles(game, dt):
    active_particles = []
    for particle in game.particles:
        particle["x"] += particle["vx"] * 60 * dt
        particle["y"] += particle["vy"] * 60 * dt
        particle["vy"] += 0.04
        particle["life"] -= dt * 1.7
        particle["radius"] = max(0.8, particle["radius"] - dt * 2.2)
        if particle["life"] > 0:
            active_particles.append(particle)
    game.particles = active_particles


def refresh_obstacles(game):
    if not game.obstacle_mode:
        return
    target = max(3, obstacle_target(game.score))
    game.obstacles = generate_obstacles(target, game.snake, game.food)
    if game.power_up in game.obstacles:
        game.power_up = None
        game.power_up_type = ""
        game.power_up_timer = 0.0


def trigger_shake(game, duration=0.22):
    game.shake_timer = max(game.shake_timer, duration)


def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snakey")
    clock = pygame.time.Clock()
    audio = setup_audio()

    game = build_game_state()
    background_theme = None
    background = None

    while True:
        dt = clock.tick(60) / 1000
        game.tick += 1
        if background_theme != game.theme:
            background = create_background_surface(game.theme)
            background_theme = game.theme
        speed = game.current_speed()
        step_time = 1 / speed
        update_particles(game, dt)
        if game.shake_timer > 0:
            game.shake_timer = max(0.0, game.shake_timer - dt)
        if game.active_power_up_timer > 0:
            game.active_power_up_timer = max(0.0, game.active_power_up_timer - dt)
            if game.active_power_up_timer == 0:
                if game.active_power_up == "shield":
                    game.shield_charges = 0
                game.active_power_up = ""
        if game.power_up and game.mode != "vs":
            game.power_up_timer += dt
            if game.power_up_timer >= 8.0:
                game.power_up = None
                game.power_up_type = ""
                game.power_up_timer = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game.state == "menu":
                    if event.key == pygame.K_c:
                        game.mode = "classic"
                        game.menu_card_index = MODE_ORDER.index("classic")
                        game.menu_resume_available = False
                        game.obstacle_mode = False
                    elif event.key == pygame.K_v:
                        game.mode = "vs"
                        game.menu_card_index = MODE_ORDER.index("vs")
                        game.menu_resume_available = False
                    elif event.key == pygame.K_o:
                        game.mode = "obstacles"
                        game.menu_card_index = MODE_ORDER.index("obstacles")
                        game.menu_resume_available = False
                    elif event.key == pygame.K_1 and game.mode == "classic":
                        game.difficulty = "easy"
                    elif event.key == pygame.K_2 and game.mode in ("classic", "obstacles"):
                        game.difficulty = "medium"
                    elif event.key == pygame.K_3 and game.mode in ("classic", "obstacles"):
                        game.difficulty = "hard"
                    elif event.key == pygame.K_1 and game.mode == "obstacles":
                        game.difficulty = "easy"
                    elif event.key == pygame.K_LEFT:
                        game.menu_card_index = (game.menu_card_index - 1) % len(MODE_ORDER)
                        game.mode = MODE_ORDER[game.menu_card_index]
                        game.menu_resume_available = False
                    elif event.key == pygame.K_RIGHT:
                        game.menu_card_index = (game.menu_card_index + 1) % len(MODE_ORDER)
                        game.mode = MODE_ORDER[game.menu_card_index]
                        game.menu_resume_available = False
                    elif event.key == pygame.K_t:
                        game.theme = cycle_value(THEME_ORDER, game.theme, 1)
                    elif event.key == pygame.K_r:
                        game = build_game_state(game.difficulty, game.best_score, game.mode, game.theme)
                        game.state = "playing"
                        game.menu_resume_available = True
                        start_music(audio)
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if not game.menu_resume_available:
                            game = build_game_state(game.difficulty, game.best_score, game.mode, game.theme)
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
                    game = build_game_state(game.difficulty, game.best_score, game.mode, game.theme)
                    game.state = "playing"
                    game.menu_resume_available = True
                    if audio.get("enabled"):
                        audio["music_channel"].stop()
                    start_music(audio)
                    continue

                if game.mode in ("classic", "obstacles"):
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
                if game.mode in ("classic", "obstacles"):
                    game.direction = game.pending_direction
                    game.previous_snake = list(game.snake)
                    head = (
                        game.snake[0][0] + game.direction[0],
                        game.snake[0][1] + game.direction[1],
                    )

                    obstacle_hit = head in game.obstacles
                    hit_danger = check_wall_collision(head) or head in game.snake or obstacle_hit
                    if hit_danger and game.shield_charges:
                        game.shield_charges = 0
                        game.active_power_up = ""
                        game.active_power_up_timer = 0.0
                        emit_particles(game, head, (164, 255, 190), amount=18, speed=1.4)
                        trigger_shake(game, 0.12)
                        continue
                    if hit_danger:
                        game.best_score = max(game.best_score, game.score)
                        game.state = "game_over"
                        play_sound(audio, "crash")
                        emit_particles(game, game.snake[0], (255, 100, 94), amount=24, speed=1.8)
                        trigger_shake(game, 0.26)
                        if audio.get("enabled"):
                            audio["music_channel"].stop()
                        break

                    game.snake.insert(0, head)

                    if head == game.food:
                        gained_score = 2 if game.active_power_up == "double_score" else 1
                        game.score += gained_score
                        game.best_score = max(game.best_score, game.score)
                        play_sound(audio, "eat")
                        emit_particles(game, head, (255, 214, 107), amount=14, speed=1.2)
                        trigger_shake(game, 0.08)
                        blocked_cells = set(game.obstacles)
                        game.food = random_food_position(game.snake, blocked=blocked_cells)
                        refresh_obstacles(game)
                        if game.mode != "vs":
                            game.power_up, game.power_up_type = maybe_spawn_power_up(
                                game.snake,
                                game.food,
                                game.obstacles,
                                game.score,
                                game.active_power_up,
                                game.power_up,
                            )
                            game.power_up_timer = 0.0
                    else:
                        game.snake.pop()

                    if game.power_up and head == game.power_up:
                        game.active_power_up = game.power_up_type
                        game.active_power_up_timer = POWER_UP_DURATION.get(game.power_up_type, 0.0)
                        if game.power_up_type == "shield":
                            game.shield_charges = 1
                            game.active_power_up_timer = 12.0
                        emit_particles(game, head, (160, 224, 255), amount=18, speed=1.5)
                        trigger_shake(game, 0.1)
                        play_sound(audio, "turn")
                        game.power_up = None
                        game.power_up_type = ""
                        game.power_up_timer = 0.0
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
                        emit_particles(game, red_head, (255, 126, 112), amount=18, speed=1.5)
                        emit_particles(game, green_head, (122, 255, 166), amount=18, speed=1.5)
                        trigger_shake(game, 0.24)
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
                        emit_particles(game, game.food, (255, 214, 107), amount=16, speed=1.25)
                        game.food = random_food_position(
                            game.vs_red_snake,
                            blocked=set(game.vs_green_snake),
                        )

        render_progress = game.move_timer / step_time if game.state == "playing" else 1.0
        render_snake = interpolated_snake(game.previous_snake, game.snake, render_progress)
        render_red_snake = interpolated_snake(game.vs_red_previous_snake, game.vs_red_snake, render_progress)
        render_green_snake = interpolated_snake(game.vs_green_previous_snake, game.vs_green_snake, render_progress)

        shake_x = 0
        shake_y = 0
        if game.shake_timer > 0:
            shake_x = int((pygame.time.get_ticks() // 24) % 3 - 1) * 4
            shake_y = int((pygame.time.get_ticks() // 16) % 3 - 1) * 3

        screen.blit(background, (shake_x, shake_y))
        if game.mode == "obstacles":
            draw_obstacles(screen, game.obstacles, game.tick, game.theme)
        if game.mode == "classic":
            draw_food(screen, game.food, game.tick)
            draw_power_up(screen, game.power_up, game.power_up_type, game.tick, game.theme)
            draw_snake(screen, render_snake, game.tick, palette="green")
        elif game.mode == "obstacles":
            draw_food(screen, game.food, game.tick)
            draw_power_up(screen, game.power_up, game.power_up_type, game.tick, game.theme)
            draw_snake(screen, render_snake, game.tick, palette="green")
        else:
            draw_food(screen, game.food, game.tick)
            draw_snake(screen, render_green_snake, game.tick, palette="green")
            draw_snake(screen, render_red_snake, game.tick, palette="red")
        draw_particles(screen, game.particles)
        draw_hud(screen, game, speed)

        if game.state == "menu":
            draw_menu_overlay(screen, game)
        elif game.state == "paused":
            paused_text = "Press SPACE to continue"
            if game.mode == "vs":
                paused_text = "Press SPACE to continue the VS match"
            elif game.mode == "obstacles":
                paused_text = "Press SPACE to continue the obstacle run"
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
            elif game.mode == "obstacles":
                draw_overlay(
                    screen,
                    "Obstacle Run Over",
                    [
                        f"Final Score: {game.score}",
                        f"Rocks Survived: {len(game.obstacles)}",
                        "Press ESC for menu or R to reset",
                    ],
                )
            else:
                draw_overlay(screen, "Game Over", "Press ESC for menu or R to reset")

        pygame.display.flip()


if __name__ == "__main__":
    main()
