# Snakey

Simple `pygame` snake game with:

- Smooth snake movement
- Difficulty selection (`Easy`, `Medium`, `Hard`)
- Animated menu cards with mode selection
- Arena themes (`Forest`, `Neon`, `Lava`, `Ice`)
- Power-ups (`speed boost`, `slow time`, `shield`, `double score`)
- Obstacles mode with rocks that increase over time
- Particles and screen shake for pickups, food, and crashes
- Apple food, score, best score, and speed HUD
- VS mode for local multiplayer

## Files

- `snake_game.py`: main loop, input handling, audio, and state transitions
- `snake_core.py`: drawing, board constants, HUD, overlays, and visual helpers
- `snake_session.py`: difficulty presets, game state, and run/session helpers
- `snake_audio.py`: sound effects and music helpers

## Controls

- `WASD` or arrow keys: move
- `C`, `O`, `V`: choose `Classic`, `Obstacles`, or `VS`
- `Left/Right`: move across menu cards
- `P`: pause
- `ESC`: open menu
- `SPACE` or `Enter`: start/resume from menu
- `R`: start a new game
- `1`, `2`, `3`: choose difficulty in menu
- `T`: cycle arena theme
- `Arrow keys`: red snake in `VS`
- `Mouse left/right`: green snake turn left/right in `VS`

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
