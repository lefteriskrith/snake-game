import random
from dataclasses import dataclass, field

from .snake_core import BASE_FPS, GRID_HEIGHT, GRID_WIDTH, MAX_FPS, random_food_position


@dataclass(frozen=True)
class Difficulty:
    label: str
    base_speed: float
    max_speed: float


@dataclass(frozen=True)
class Theme:
    label: str
    accent: tuple[int, int, int]


@dataclass
class GameState:
    snake: list[tuple[int, int]]
    direction: tuple[int, int]
    food: tuple[int, int]
    score: int
    pending_direction: tuple[int, int]
    move_timer: float
    previous_snake: list[tuple[int, int]] = field(default_factory=list)
    best_score: int = 0
    state: str = "menu"
    tick: int = 0
    difficulty: str = "easy"
    menu_resume_available: bool = False
    mode: str = "classic"
    theme: str = "neon"
    vs_red_snake: list[tuple[int, int]] = field(default_factory=list)
    vs_red_direction: tuple[int, int] = (1, 0)
    vs_red_pending_direction: tuple[int, int] = (1, 0)
    vs_red_previous_snake: list[tuple[int, int]] = field(default_factory=list)
    vs_green_snake: list[tuple[int, int]] = field(default_factory=list)
    vs_green_direction: tuple[int, int] = (0, 1)
    vs_green_pending_direction: tuple[int, int] = (0, 1)
    vs_green_previous_snake: list[tuple[int, int]] = field(default_factory=list)
    vs_winner: str = ""
    vs_survival_time: float = 0.0
    obstacle_mode: bool = False
    obstacles: list[tuple[int, int]] = field(default_factory=list)
    power_up: tuple[int, int] | None = None
    power_up_type: str = ""
    power_up_timer: float = 0.0
    active_power_up: str = ""
    active_power_up_timer: float = 0.0
    shield_charges: int = 0
    particles: list[dict] = field(default_factory=list)
    shake_timer: float = 0.0
    menu_card_index: int = 0

    def current_settings(self):
        return DIFFICULTIES[self.difficulty]

    def current_speed(self):
        if self.mode == "vs":
            return DIFFICULTIES["easy"].base_speed + 0.5
        settings = self.current_settings()
        speed = min(settings.max_speed, settings.base_speed + self.score // 4)
        if self.obstacle_mode:
            speed += 0.5
        if self.active_power_up == "speed_boost":
            speed += 2.0
        elif self.active_power_up == "slow_time":
            speed = max(1.0, speed - 2.0)
        return speed

    def current_theme(self):
        return THEMES[self.theme]


DIFFICULTIES = {
    "easy": Difficulty("Easy", 1.5, 3.5),
    "medium": Difficulty("Medium", 6, 14),
    "hard": Difficulty("Hard", BASE_FPS, MAX_FPS),
}

THEMES = {
    "forest": Theme("Forest", (116, 196, 141)),
    "neon": Theme("Neon", (106, 245, 236)),
    "lava": Theme("Lava", (255, 140, 82)),
    "ice": Theme("Ice", (165, 228, 255)),
}

THEME_ORDER = list(THEMES)
MODE_ORDER = ["classic", "obstacles", "vs"]
POWER_UP_TYPES = ("speed_boost", "slow_time", "shield", "double_score")
POWER_UP_DURATION = {
    "speed_boost": 6.0,
    "slow_time": 6.5,
    "double_score": 8.0,
}


def reset_game():
    snake = [(10, 12), (9, 12), (8, 12)]
    food = random_food_position(snake)
    return snake, (1, 0), food, 0


def start_new_run():
    snake, direction, food, score = reset_game()
    return snake, direction, food, score, direction, 0.0


def reset_vs_game():
    red_snake = [(7, 6), (6, 6), (5, 6)]
    green_snake = [(24, 15), (24, 14), (24, 13)]
    return red_snake, (1, 0), green_snake, (0, 1)


def obstacle_target(score):
    return min(18, score // 3)


def random_open_cell(*occupied_groups):
    occupied = set()
    for group in occupied_groups:
        if not group:
            continue
        if isinstance(group, set):
            occupied.update(group)
        elif isinstance(group, tuple) and len(group) == 2 and all(isinstance(value, int) for value in group):
            occupied.add(group)
        else:
            occupied.update(group)

    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in occupied:
            return pos


def generate_obstacles(count, snake, food, blocked=None):
    blocked_cells = set(blocked or set())
    blocked_cells.update(snake)
    blocked_cells.add(food)
    obstacles = []
    while len(obstacles) < count:
        pos = random_open_cell(blocked_cells)
        if pos in blocked_cells:
            continue
        if pos in obstacles:
            continue
        neighbors = abs(pos[0] - snake[0][0]) + abs(pos[1] - snake[0][1])
        if neighbors < 4:
            continue
        obstacles.append(pos)
        blocked_cells.add(pos)
    return obstacles


def maybe_spawn_power_up(snake, food, obstacles, score, active_power_up, current_power_up=None):
    if current_power_up or active_power_up or score < 2 or score % 3 != 0:
        return None, ""
    power_up_type = POWER_UP_TYPES[(score // 3 - 1) % len(POWER_UP_TYPES)]
    return random_open_cell(snake, {food}, obstacles), power_up_type


def build_game_state(difficulty="easy", best_score=0, mode="classic", theme="neon"):
    red_snake, red_direction, green_snake, green_direction = reset_vs_game()
    if mode == "vs":
        snake = [(10, 12), (9, 12), (8, 12)]
        direction = (1, 0)
        food = random_food_position(red_snake, blocked=set(green_snake))
        score = 0
        pending_direction = direction
        move_timer = 0.0
    else:
        snake, direction, food, score, pending_direction, move_timer = start_new_run()
    obstacle_mode = mode == "obstacles"
    obstacles = generate_obstacles(3, snake, food) if obstacle_mode else []
    return GameState(
        snake=snake,
        direction=direction,
        food=food,
        score=score,
        pending_direction=pending_direction,
        move_timer=move_timer,
        previous_snake=list(snake),
        best_score=best_score,
        difficulty=difficulty,
        mode=mode,
        theme=theme,
        vs_red_snake=red_snake,
        vs_red_direction=red_direction,
        vs_red_pending_direction=red_direction,
        vs_red_previous_snake=list(red_snake),
        vs_green_snake=green_snake,
        vs_green_direction=green_direction,
        vs_green_pending_direction=green_direction,
        vs_green_previous_snake=list(green_snake),
        obstacle_mode=obstacle_mode,
        obstacles=obstacles,
        menu_card_index=MODE_ORDER.index(mode) if mode in MODE_ORDER else 0,
    )


def interpolated_snake(previous_snake, current_snake, progress):
    if not previous_snake:
        return current_snake

    progress = max(0.0, min(1.0, progress))
    previous_segments = list(previous_snake)
    while len(previous_segments) < len(current_snake):
        previous_segments.append(previous_segments[-1])

    render_snake = []
    for index, segment in enumerate(current_snake):
        start_x, start_y = previous_segments[index]
        end_x, end_y = segment
        render_snake.append(
            (
                start_x + (end_x - start_x) * progress,
                start_y + (end_y - start_y) * progress,
            )
        )

    return render_snake
