"""The overlay drawn over the maze: the path each ghost follows and its target tile. Toggled with a key."""

import pygame

from pacman import config


class Overlay:
    """Draws each ghost's path as a line and its target as a square, both in the ghost's colour."""

    def __init__(self, maze_view) -> None:
        """Start hidden; the player shows it with the O key."""
        self.maze_view = maze_view
        self.visible = False

    def toggle(self) -> None:
        """Show or hide the overlay."""
        self.visible = not self.visible

    def draw(self, surface: pygame.Surface, ghosts) -> None:
        """Draw the paths and targets of all the ghosts, if the overlay is switched on."""
        if not self.visible:
            return
        for index, ghost in enumerate(ghosts):
            if ghost.target is None or ghost.in_house:
                continue  # frightened ghosts and ghosts in the house have no target
            colour = config.GHOST_COLOURS[ghost.name]
            self._draw_path(surface, ghost, colour, index)
            self._draw_target(surface, ghost.target, colour, index)

    def _draw_path(self, surface: pygame.Surface, ghost, colour, index: int) -> None:
        """Draw a line from the ghost through the tiles of its path.

        Each ghost's line is shifted by a few pixels, so paths that share a corridor stay visible.
        """
        shift = (index - (len(config.GHOST_NAMES) - 1) / 2) * config.OVERLAY_WIDTH
        half = config.TILE_SIZE // 2
        start = (
            self.maze_view.origin[0] + ghost.x * config.TILE_SIZE + half,
            self.maze_view.origin[1] + ghost.y * config.TILE_SIZE + half,
        )
        points = [start] + [self.maze_view.tile_centre(tile) for tile in ghost.path]
        for a, b in zip(points, points[1:]):
            if abs(a[0] - b[0]) > config.TILE_SIZE * 1.5:
                continue  # this step goes through the warp tunnel: no line across the whole maze
            pygame.draw.line(
                surface, colour, (a[0] + shift, a[1] + shift), (b[0] + shift, b[1] + shift), config.OVERLAY_WIDTH
            )

    def _draw_target(self, surface: pygame.Surface, tile, colour, index: int) -> None:
        """Draw a square outline on the tile. Each ghost's square is a bit smaller, so shared targets stay visible."""
        size = config.TILE_SIZE - 2 * index * config.OVERLAY_WIDTH
        rect = pygame.Rect(0, 0, size, size)
        rect.center = self.maze_view.tile_centre(tile)
        pygame.draw.rect(surface, colour, rect, config.OVERLAY_WIDTH)
