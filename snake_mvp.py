import pygame
import random
import sys

# ------------- Settings -------------
# Μέγεθος αρχικών κελιών (pixels)
# Μεγαλύτερο παράθυρο και πιο ευκρινή φιδάκια.
CELL_SIZE = 24

# Πόσα κελιά οριζόντια και κάθετα
GRID_WIDTH = 34
GRID_HEIGHT = 24

# Αρχική ταχύτητα frame rate
FPS = 6

# ------------- Colors -------------
COLOR_BG = (0, 0, 0)
COLOR_SNAKE = (46, 204, 113)
COLOR_FOOD = (231, 76, 60)
COLOR_TEXT = (236, 240, 241)

# ------------- Helper Functions -------------

def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont(None, size)
    text_img = font.render(text, True, COLOR_TEXT)
    surface.blit(text_img, (x, y))


def random_food_position(snake):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake:
            return pos

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

            # wrap around (εικόνα "στο δρόμο")
            head = (head[0] % GRID_WIDTH, head[1] % GRID_HEIGHT)

            # σύγκρουση με τον εαυτό του
            if head in snake:
                game_over = True

            snake.insert(0, head)

            if head == food:
                score += 1
                food = random_food_position(snake)
            else:
                snake.pop()

        # ------------- Draw -------------
        screen.fill(COLOR_BG)

        # Σχέδιο φαγητού (κύκλος για πιο "φιδίσιο" look)
        food_center = (food[0] * CELL_SIZE + CELL_SIZE // 2, food[1] * CELL_SIZE + CELL_SIZE // 2)
        food_radius = CELL_SIZE // 2 - 2
        pygame.draw.circle(screen, COLOR_FOOD, food_center, food_radius)

        # Σχέδιο φιδιού (στρογγυλές διαστάσεις και μικρό offset για smooth)
        snake_radius = CELL_SIZE // 2 - 2
        for segment in snake:
            segment_center = (segment[0] * CELL_SIZE + CELL_SIZE // 2, segment[1] * CELL_SIZE + CELL_SIZE // 2)
            pygame.draw.circle(screen, COLOR_SNAKE, segment_center, snake_radius)


        draw_text(screen, f"Score: {score}", 28, 8, GRID_HEIGHT * CELL_SIZE + 4)

        if game_over:
            draw_text(screen, "Game Over! Press R to restart", 32, 80, GRID_HEIGHT * CELL_SIZE + 4)

        pygame.display.flip()
        clock.tick(FPS + score // 5)


if __name__ == "__main__":
    main()