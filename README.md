# Pac-Man AI

A Pac-Man game in Python with Pygame, built for the Artificial Intelligence course at the
Technical University of Cluj-Napoca. In this version you play Pac-Man yourself (manual mode).
The ghosts, which hunt Pac-Man with search algorithms, arrive in Sprint 2, and an autonomous
Pac-Man driven by AI agents arrives in Sprint 3.

## Features

- The maze is loaded from a text file in `maps/`, and an invalid map is rejected with a message
  that says what is wrong and where (line and column).
- Pac-Man moves tile by tile with the arrow keys, stops at walls, goes through the warp tunnel and
  is animated in the direction he faces.
- Dots (10 points), energizers (50) and the bonus fruit (100), which appears after 70 and 170 dots
  for 9 seconds.
- Score and lives always visible, a win screen, and a new game without restarting the program.
- A start screen and sound effects, which can be muted.

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
| Enter | Start the game; start a new game after a win |
| Arrow keys | Move Pac-Man |
| M | Mute or unmute the sound |
| Close the window | Quit |

## Project structure

```
pacman/
├── maps/            classic.txt (the default map), small.txt (a small map for tests and demos)
├── assets/          sprites/, fonts/, sounds/ and ASSETS.md (source and licence of every file)
├── docs/            documentation.tex, documentation.bib, images/, documentation.pdf
├── results/         tables and charts of the experiments (Sprints 2 and 3)
└── src/pacman/
    ├── main.py      entry point of `uv run pacman`; reads the command-line options
    ├── config.py    every constant of the game, defined once
    ├── game.py      the game loop
    ├── model/       maze, Pac-Man, score: the rules of the game, no Pygame
    ├── search/      the ghosts' path finders, no Pygame
    ├── agents/      Pac-Man's controllers, no Pygame
    └── view/        drawing and sound: the only package that uses Pygame
```

## Team

| Member | Stories |
|---|---|
| Ariana Daboc | US1.0 project skeleton, US1.1 maze from a map file, US1.6 README and documentation |
| Roxana Marginean | US1.2 Pac-Man movement and animation, US1.5 sound effects and start screen |
| Diana Sighiartau | US1.3 dots, energizers, fruit, score and win, US1.4 asset pack and theme |
