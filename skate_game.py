import math
import pygame
import random
import sys
from array import array
from snake_core import (
    BASE_FPS,
    MAX_FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    random_food_position,
    random_bonus_position,
    draw_snake,
    draw_food,
    draw_bonus,
    draw_obstacles,
    draw_walls,
    draw_hud,
    draw_overlay,
    create_background_surface,
    check_wall_collision,
    create_obstacles,
    obstacle_positions,
    check_obstacle_collision,
    update_obstacles,
)

# ------------- Main Game Loop -------------


def reset_game():
    snake = [(10, 12), (9, 12), (8, 12)]
    obstacles = create_obstacles()
    food = random_food_position(snake, obstacle_positions(obstacles))
    return snake, (1, 0), food, 0, obstacles, None


def make_tone(frequency, duration_ms, volume=0.25, sample_rate=22050):
    total_samples = int(sample_rate * (duration_ms / 1000))
    attack = max(1, int(total_samples * 0.12))
    release = max(1, int(total_samples * 0.22))
    samples = array("h")

    for index in range(total_samples):
        if index < attack:
            envelope = index / attack
        elif index > total_samples - release:
            envelope = max(0.0, (total_samples - index) / release)
        else:
            envelope = 1.0

        wave = (
            math.sin((2 * math.pi * frequency * index) / sample_rate)
            + 0.35 * math.sin((2 * math.pi * frequency * 2 * index) / sample_rate)
        )
        samples.append(int(32767 * volume * envelope * wave * 0.7))

    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_music_loop(sample_rate=22050):
    notes = [
        (196.00, 320),
        (246.94, 320),
        (293.66, 640),
        (220.00, 320),
        (246.94, 320),
        (329.63, 640),
        (174.61, 320),
        (220.00, 320),
        (261.63, 640),
    ]
    samples = array("h")

    for frequency, duration_ms in notes:
        total_samples = int(sample_rate * (duration_ms / 1000))
        attack = max(1, int(total_samples * 0.18))
        release = max(1, int(total_samples * 0.28))

        for index in range(total_samples):
            if index < attack:
                envelope = index / attack
            elif index > total_samples - release:
                envelope = max(0.0, (total_samples - index) / release)
            else:
                envelope = 1.0

            t = index / sample_rate
            wave = (
                math.sin(2 * math.pi * frequency * t)
                + 0.45 * math.sin(2 * math.pi * (frequency / 2) * t)
                + 0.20 * math.sin(2 * math.pi * (frequency * 1.5) * t)
            ) / 1.65
            samples.append(int(32767 * 0.11 * envelope * wave))

    return pygame.mixer.Sound(buffer=samples.tobytes())


def setup_audio():
    audio = {"enabled": False}
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        audio["enabled"] = True
        audio["turn"] = make_tone(420, 70, 0.10)
        audio["eat"] = make_tone(760, 140, 0.18)
        audio["crash"] = make_tone(140, 320, 0.20)
        audio["music"] = make_music_loop()
        audio["music_channel"] = pygame.mixer.Channel(0)
        audio["sfx_channel"] = pygame.mixer.Channel(1)
        audio["music_channel"].set_volume(0.38)
        audio["sfx_channel"].set_volume(0.65)
    except pygame.error:
        return audio

    return audio


def start_music(audio):
    if audio.get("enabled") and not audio["music_channel"].get_busy():
        audio["music_channel"].play(audio["music"], loops=-1)


def play_sound(audio, name):
    if audio.get("enabled"):
        audio["sfx_channel"].play(audio[name])


def bonus_blocked_cells(snake, obstacles, food):
    blocked = set(snake)
    blocked.update(obstacle_positions(obstacles))
    if food:
        blocked.add(food)
    return blocked


def spawn_bonus(snake, obstacles, food):
    return {
        "kind": random.choice(("shield", "score", "slow")),
        "pos": random_bonus_position(snake, bonus_blocked_cells(snake, obstacles, food)),
        "ttl": 90,
    }


def main():
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("snake-game")
    clock = pygame.time.Clock()
    background = create_background_surface()
    audio = setup_audio()

    snake, direction, food, score, obstacles, bonus = reset_game()
    pending_direction = direction
    best_score = 0
    state = "start"
    move_timer = 0.0
    tick = 0
    bonus_cooldown = 10
    slow_steps = 0
    shield_steps = 0

    while True:
        dt = clock.tick(60) / 1000
        tick += 1
        speed = min(MAX_FPS, BASE_FPS + score // 4)
        if slow_steps > 0:
            speed = max(BASE_FPS, speed - 3)
        step_time = 1 / speed

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    if pending_direction != (0, -1):
                        play_sound(audio, "turn")
                    pending_direction = (0, -1)
                    if state == "start":
                        state = "playing"
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    if pending_direction != (0, 1):
                        play_sound(audio, "turn")
                    pending_direction = (0, 1)
                    if state == "start":
                        state = "playing"
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    if pending_direction != (-1, 0):
                        play_sound(audio, "turn")
                    pending_direction = (-1, 0)
                    if state == "start":
                        state = "playing"
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    if pending_direction != (1, 0):
                        play_sound(audio, "turn")
                    pending_direction = (1, 0)
                    if state == "start":
                        state = "playing"
                elif event.key == pygame.K_SPACE:
                    if state == "start":
                        state = "playing"
                        start_music(audio)
                    elif state == "paused":
                        state = "playing"
                        if audio.get("enabled"):
                            audio["music_channel"].unpause()
                elif event.key == pygame.K_p and state == "playing":
                    state = "paused"
                    if audio.get("enabled"):
                        audio["music_channel"].pause()
                elif event.key == pygame.K_r and state in ("game_over", "paused", "start"):
                    snake, direction, food, score, obstacles, bonus = reset_game()
                    pending_direction = direction
                    move_timer = 0.0
                    state = "start"
                    bonus_cooldown = 10
                    slow_steps = 0
                    shield_steps = 0
                    if audio.get("enabled"):
                        audio["music_channel"].stop()

        if state == "playing":
            start_music(audio)
            move_timer += dt
            while move_timer >= step_time:
                move_timer -= step_time
                direction = pending_direction
                head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

                hit_danger = check_wall_collision(head) or head in snake or check_obstacle_collision(head, obstacles)
                if hit_danger and shield_steps <= 0:
                    best_score = max(best_score, score)
                    state = "game_over"
                    play_sound(audio, "crash")
                    if audio.get("enabled"):
                        audio["music_channel"].stop()
                    break
                elif hit_danger and shield_steps > 0:
                    shield_steps = 0
                    play_sound(audio, "turn")
                    continue

                snake.insert(0, head)

                if head == food:
                    score += 1
                    best_score = max(best_score, score)
                    play_sound(audio, "eat")
                    blocked = obstacle_positions(obstacles)
                    if bonus:
                        blocked.add(bonus["pos"])
                    food = random_food_position(snake, blocked)
                else:
                    snake.pop()

                update_obstacles(obstacles, snake, food)
                if snake[0] in obstacle_positions(obstacles) and shield_steps <= 0:
                    best_score = max(best_score, score)
                    state = "game_over"
                    play_sound(audio, "crash")
                    if audio.get("enabled"):
                        audio["music_channel"].stop()
                    break
                elif snake[0] in obstacle_positions(obstacles) and shield_steps > 0:
                    shield_steps = 0

                if food in obstacle_positions(obstacles):
                    blocked = obstacle_positions(obstacles)
                    if bonus:
                        blocked.add(bonus["pos"])
                    food = random_food_position(snake, blocked)

                if bonus and snake[0] == bonus["pos"]:
                    if bonus["kind"] == "shield":
                        shield_steps = 12
                    elif bonus["kind"] == "score":
                        score += 3
                        best_score = max(best_score, score)
                    elif bonus["kind"] == "slow":
                        slow_steps = 18
                    play_sound(audio, "eat")
                    bonus = None
                    bonus_cooldown = 18

                if bonus:
                    bonus["ttl"] -= 1
                    if bonus["ttl"] <= 0:
                        bonus = None
                        bonus_cooldown = 10
                else:
                    bonus_cooldown -= 1
                    if bonus_cooldown <= 0 and score >= 2:
                        bonus = spawn_bonus(snake, obstacles, food)
                        bonus_cooldown = 20

                if shield_steps > 0:
                    shield_steps -= 1
                if slow_steps > 0:
                    slow_steps -= 1

        screen.blit(background, (0, 0))
        draw_walls(screen)
        draw_obstacles(screen, obstacles, tick)
        draw_food(screen, food, tick)
        draw_bonus(screen, bonus, tick)
        draw_snake(screen, snake, tick)
        active_bonus = None
        if shield_steps > 0:
            active_bonus = "shield"
        elif slow_steps > 0:
            active_bonus = "slow"
        elif bonus:
            active_bonus = f"spawned {bonus['kind']}"
        draw_hud(screen, score, best_score, speed, state, len(obstacles), active_bonus, shield_steps)

        if state == "start":
            draw_overlay(screen, "snake-game", "Blue shield blocks one hit, gold gives score, green slows danger")
        elif state == "paused":
            draw_overlay(screen, "Paused", "Take a breath, then SPACE to continue")
        elif state == "game_over":
            draw_overlay(screen, "Crashed", "A wall, body, or obstacle got you. Press R to reset")

        pygame.display.flip()


if __name__ == "__main__":
    main()
