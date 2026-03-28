# snake-game

Simple Python `pygame` snake game (MVP), private repo: `snake-game`.

## Features

- Snake moves on a grid
- Food appears as a red apple with stem and shine
- Game over when snake hits the wall or itself (no wrapping)
- Score display
- Restart with `R`

## Controls

- Arrow keys: move
- R: restart after game-over

## Requirements

- Python 3.10+
- pygame

Install:

```bash
pip install pygame
```

## Development

Run:

```bash
python skate_game.py
```

## Changelog

### 2026-03-28
- Added `snake_core.py` module for game logic & rendering helpers
- Implemented wall collision (no wall-wrapping)
- Updated snake rendering to nice circles
- Updated food to red apple style
- Added `draw_walls` and game-over logic
- Added README and repository setup instructions
