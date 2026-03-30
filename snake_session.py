from dataclasses import dataclass, field

from snake_core import BASE_FPS, MAX_FPS, random_food_position


@dataclass(frozen=True)
class Difficulty:
    label: str
    base_speed: float
    max_speed: float


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

    def current_settings(self):
        return DIFFICULTIES[self.difficulty]

    def current_speed(self):
        if self.mode == "vs":
            return DIFFICULTIES["easy"].base_speed + 0.5
        settings = self.current_settings()
        return min(settings.max_speed, settings.base_speed + self.score // 4)


DIFFICULTIES = {
    "easy": Difficulty("Easy", 1.5, 3.5),
    "medium": Difficulty("Medium", 6, 14),
    "hard": Difficulty("Hard", BASE_FPS, MAX_FPS),
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


def build_game_state(difficulty="easy", best_score=0, mode="classic"):
    snake, direction, food, score, pending_direction, move_timer = start_new_run()
    red_snake, red_direction, green_snake, green_direction = reset_vs_game()
    if mode == "vs":
        food = random_food_position(red_snake, blocked=set(green_snake))
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
        vs_red_snake=red_snake,
        vs_red_direction=red_direction,
        vs_red_pending_direction=red_direction,
        vs_red_previous_snake=list(red_snake),
        vs_green_snake=green_snake,
        vs_green_direction=green_direction,
        vs_green_pending_direction=green_direction,
        vs_green_previous_snake=list(green_snake),
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
