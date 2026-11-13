"""Draws the maze with pygame: walls, the ghost house door, dots and energizers."""

import pygame

from pacman import config
from pacman.model.maze import Maze, Tile


class MazeView:
    """Draws one maze. Walls never change, so they are drawn once and reused."""

    def __init__(self, maze: Maze) -> None:
        """Prepare the drawing; the maze is centred horizontally at the top of the screen."""
        self.maze = maze
        self.origin = ((config.SCREEN_WIDTH - maze.width * config.TILE_SIZE) // 2, 0)
        self.background = self._render_walls()

    def tile_centre(self, tile: Tile) -> tuple[int, int]:
        """Return the screen pixel at the centre of a tile."""
        x, y = tile
        half = config.TILE_SIZE // 2
        return (
            self.origin[0] + x * config.TILE_SIZE + half,
            self.origin[1] + y * config.TILE_SIZE + half,
        )

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the walls, then the dots and energizers that are still in the maze."""
        surface.blit(self.background, self.origin)
        for tile in self.maze.dots:
            pygame.draw.circle(surface, config.DOT_COLOUR, self.tile_centre(tile), config.DOT_RADIUS)
        for tile in self.maze.energizers:
            pygame.draw.circle(surface, config.DOT_COLOUR, self.tile_centre(tile), config.ENERGIZER_RADIUS)

    def _render_walls(self) -> pygame.Surface:
        """Draw the walls and the door once, on a separate image.

        Drawing about 1000 wall tiles every frame would waste time;
        copying one ready-made image (blit) is much cheaper.
        """
        size = config.TILE_SIZE
        image = pygame.Surface((self.maze.width * size, self.maze.height * size))
        image.fill(config.BACKGROUND_COLOUR)
        for y, row in enumerate(self.maze.rows):
            for x, char in enumerate(row):
                rect = pygame.Rect(x * size, y * size, size, size)
                if char == config.WALL:
                    pygame.draw.rect(image, config.WALL_COLOUR, rect)
                elif char == config.DOOR:
                    top = rect.centery - config.DOOR_THICKNESS // 2
                    pygame.draw.rect(image, config.DOOR_COLOUR, (rect.left, top, size, config.DOOR_THICKNESS))
        return image
