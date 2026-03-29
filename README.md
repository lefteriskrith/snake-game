# Snakey

Simple `pygame` snake game with:

- Smooth snake movement
- Difficulty selection (`Easy`, `Medium`, `Hard`)
- Menu with resume/new game flow
- Apple food, score, best score, and speed HUD

## Files

- `snake_game.py`: main loop, input handling, audio, and state transitions
- `snake_core.py`: drawing, board constants, HUD, overlays, and visual helpers
- `snake_session.py`: difficulty presets, game state, and run/session helpers
- `snake_audio.py`: sound effects and music helpers

## Controls

- `WASD` or arrow keys: move
- `P`: pause
- `ESC`: open menu
- `SPACE` or `Enter`: start/resume from menu
- `R`: start a new game
- `1`, `2`, `3`: choose difficulty in menu

## Requirements

- Python 3.10+
- `pygame`

Install:

```bash
pip install pygame
```

Run:

```bash
python snake_game.py
```
