"""Entry point: `uv run pacman` (or `uv run pacman maps/other.txt` for another map)."""

import argparse
import sys
from pathlib import Path

from pacman import config
from pacman.game import Game
from pacman.model.maze import MapError


def main() -> None:
    """Read the optional map path, create the game and run its loop."""
    parser = argparse.ArgumentParser(prog="pacman", description="Pac-Man with AI agents.")
    parser.add_argument("map", nargs="?", type=Path, default=config.MAP_PATH, help="map file to play")
    args = parser.parse_args()
    try:
        game = Game(args.map)
    except MapError as error:
        sys.exit(f"Invalid map: {error}")  # prints the message to stderr and exits with code 1
    game.run()


if __name__ == "__main__":
    main()
