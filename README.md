# Pac-Man AI

You play Pac-Man with the keyboard, against four ghosts that hunt him along paths found with
DFS, BFS, A* or greedy best-first search, chosen while the game runs. An autonomous Pac-Man driven
by AI agents arrives in Sprint 3.

## Features

- The maze is loaded from a text file in `maps/`, and an invalid map is rejected with a message
  that says what is wrong and where (line and column).
- Pac-Man moves tile by tile with the arrow keys, stops at walls, goes through the warp tunnel and
  is animated in the direction he faces.
- Dots (10 points), energizers (50) and the bonus fruit (100), which appears after 70 and 170 dots
  for 9 seconds.
- Score and lives always visible, a win screen, and a new game without restarting the program.
- A start screen and sound effects, which can be muted.
- Four ghosts with their own personalities: Blinky chases Pac-Man, Pinky aims four tiles ahead of
  him, Inky uses Blinky to cut him off, and Clyde runs to his corner when he gets close.
- Ghost states: scatter and chase on a timer, frightened (blue, flashing at the end) after an
  energizer, and eaten (the eyes go back to the house). Eaten ghosts give 200, 400, 800 and 1600
  points; being caught costs 500 points and a life.
- A control panel next to the maze: choose the ghosts' search algorithm, see each ghost's state,
  path length and expanded nodes, and show their paths and targets over the maze.
- A comparison of the four searches on 30 fixed pairs: `uv run python -m pacman.experiments.search_comparison`
  (results in `results/`).

## How to run

You need [uv](https://docs.astral.sh/uv/). It installs Python 3.12 and Pygame by itself.

```bash
git clone https://github.com/arianaDaboc/pacman.git
cd pacman
uv sync
uv run pacman
```

Other maps:

```bash
uv run pacman maps/other.txt          # any map that follows the rules of the game
uv run pacman maps/small.txt --test   # small test map: only the file format is checked
```

## Controls

| Key | Action |
|---|---|
| Enter | Start the game; start a new game after a win or a game over |
| Arrow keys | Move Pac-Man |
| 1, 2, 3, 4 (or click in the panel) | Ghost search: DFS, BFS, A*, greedy best-first |
| O | Show or hide the ghosts' paths and targets |
| M | Mute or unmute the sound |
| Close the window | Quit |

## Project structure

```
pacman/
├── maps/            classic.txt (the default map), small.txt (a small map for tests and demos)
├── assets/          sprites/, fonts/, sounds/ and ASSETS.md (source and licence of every file)
├── docs/            documentation.tex, documentation.bib, images/, documentation.pdf
├── results/         search_comparison.csv and .tex (Sprint 2), agent experiments (Sprint 3)
└── src/pacman/
    ├── main.py      entry point of `uv run pacman`; reads the command-line options
    ├── config.py    every constant of the game, defined once
    ├── game.py      the game loop
    ├── model/       maze, Pac-Man, ghosts, personalities, ghost states, score: no Pygame
    ├── search/      DFS, BFS, A*, greedy best-first: no Pygame
    ├── experiments/ the search comparison of Sprint 2: no Pygame
    ├── agents/      Pac-Man's controllers, no Pygame
    └── view/        drawing, control panel, overlay and sound: the only package that uses Pygame
```

## Team

| Member | Stories |
|---|---|
| Ariana Daboc | US1.0 project skeleton, US1.1 maze from a map file, US1.6 README and documentation, US2.2 DFS and BFS, US2.6 control panel, US2.8 search comparison |
| Roxana Marginean | US1.2 Pac-Man movement and animation, US1.5 sound effects and start screen, US2.3 A*, US2.5 ghost states |
| Diana Sighiartau | US1.3 dots, energizers, fruit, score and win, US1.4 asset pack and theme, US2.1 ghosts, US2.4 ghost personalities, US2.7 greedy best-first |
