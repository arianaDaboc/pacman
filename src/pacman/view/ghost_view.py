"""Draws the ghosts with their sprites."""

import pygame

from pacman import config


class GhostView:
    """One sprite per ghost, scaled to the tile size once."""

    def __init__(self, maze_view) -> None:
        """Load the four ghost sprites."""
        self.maze_view = maze_view
        size = (config.TILE_SIZE, config.TILE_SIZE)
        self.images = {
            name: pygame.transform.scale(
                pygame.image.load(config.SPRITES_DIR / f"ghost_{colour}.png").convert_alpha(), size
            )
            for name, colour in config.GHOST_SPRITES.items()
        }

    def draw(self, surface: pygame.Surface, ghosts) -> None:
        """Draw every ghost at its position (between tiles while it moves)."""
        for ghost in ghosts:
            x = self.maze_view.origin[0] + ghost.x * config.TILE_SIZE
            y = self.maze_view.origin[1] + ghost.y * config.TILE_SIZE
            surface.blit(self.images[ghost.name], (round(x), round(y)))
