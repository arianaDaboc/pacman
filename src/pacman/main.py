"""Entry point: `uv run pacman`."""

from pacman.game import Game


def main() -> None:
    """Create the game and run its loop."""
    Game().run()


if __name__ == "__main__":
    main()
