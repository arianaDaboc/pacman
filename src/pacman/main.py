"""Entry point: `uv run pacman`, `uv run pacman maps/other.txt`, or `uv run pacman maps/small.txt --test`."""

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
    parser.add_argument(
        "--test", action="store_true", help="small test map: only the file format is checked, not the game rules"
    )
    args = parser.parse_args()
    try:
        game = Game(args.map, full_validation=not args.test)
    except MapError as error:
        sys.exit(f"Invalid map: {error}")  # prints the message to stderr and exits with code 1
    game.run()


if __name__ == "__main__":
    main()
