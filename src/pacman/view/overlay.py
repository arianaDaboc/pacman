"""The overlay drawn over the maze: where each ghost is heading. Toggled with a key."""

import pygame

from pacman import config


class Overlay:
    """Marks each ghost's target tile with a square in the ghost's colour."""

    def __init__(self, maze_view) -> None:
        """Start hidden; the player shows it with the O key."""
        self.maze_view = maze_view
        self.visible = False

    def toggle(self) -> None:
        """Show or hide the overlay."""
        self.visible = not self.visible

    def draw(self, surface: pygame.Surface, ghosts) -> None:
        """Draw the targets of all the ghosts, if the overlay is switched on."""
        if not self.visible:
            return
        for index, ghost in enumerate(ghosts):
            if ghost.target is not None and not ghost.in_house:
                self._draw_target(surface, ghost.target, config.GHOST_COLOURS[ghost.name], index)

    def _draw_target(self, surface: pygame.Surface, tile, colour, index: int) -> None:
        """Draw a square outline on the tile. Each ghost's square is a bit smaller, so shared targets stay visible."""
        size = config.TILE_SIZE - 2 * index * config.OVERLAY_WIDTH
        rect = pygame.Rect(0, 0, size, size)
        rect.center = self.maze_view.tile_centre(tile)
        pygame.draw.rect(surface, colour, rect, config.OVERLAY_WIDTH)
