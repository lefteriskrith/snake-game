import pygame
import sys
from snake_core import (
    CELL_SIZE,
    GRID_WIDTH,
    GRID_HEIGHT,
    FPS,
    COLOR_BG,
    draw_text,
    random_food_position,
    draw_snake,
    draw_food,
    draw_walls,
    check_wall_collision,
)

# ------------- Main Game Loop -------------

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE + 60))  # μεγαλύτερο ύψος για πληροφορίες
    pygame.display.set_caption("Snake MVP")
    clock = pygame.time.Clock()

    snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction = (1, 0)
    food = random_food_position(snake)
    score = 0
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1):
                    direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    direction = (1, 0)
                elif event.key == pygame.K_r and game_over:
                    return main()  # restart

        if not game_over:
            head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            # σύγκρουση με τοίχο
            if check_wall_collision(head):
                game_over = True
            # σύγκρουση με το σώμα
            elif head in snake:
                game_over = True
            else:
                snake.insert(0, head)

                if head == food:
                    score += 1
                    food = random_food_position(snake)
                else:
                    snake.pop()

        # ------------- Draw -------------
        screen.fill(COLOR_BG)
        draw_walls(screen)
        draw_food(screen, food)
        draw_snake(screen, snake)

        draw_text(screen, f"Score: {score}", 28, 8, GRID_HEIGHT * CELL_SIZE + 4)

        if game_over:
            draw_text(screen, "Game Over! Press R to restart", 32, 80, GRID_HEIGHT * CELL_SIZE + 4)

        pygame.display.flip()
        clock.tick(FPS + score // 5)


if __name__ == "__main__":
    main()