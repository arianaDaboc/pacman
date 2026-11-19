"""The four ghost personalities: each one is a rule that chooses the tile its ghost hunts. No pygame here."""

import math

from pacman import config
from pacman.model.maze import Maze, Tile


def ahead(pacman, tiles: int) -> Tile:
    """Return the tile that is `tiles` tiles in front of Pac-Man, in the direction he faces.

    The result can be a wall or even outside the maze; the game then aims the ghost
    at the closest corridor tile (see closest_walkable in pacman.search.path_finder).
    """
    x, y = pacman.tile
    dx, dy = pacman.facing
    return (x + tiles * dx, y + tiles * dy)


class Personality:
    """Base class: each ghost owns one personality, which gives its corner and its chase target."""

    def __init__(self, maze: Maze) -> None:
        """Remember the scatter corner of this ghost (Table 5)."""
        self.corner = self.find_corner(maze)

    def find_corner(self, maze: Maze) -> Tile:
        """Return the corner tile of the maze that belongs to this ghost."""
        raise NotImplementedError

    def target(self, ghost, pacman, ghosts) -> Tile:
        """Return the tile the ghost hunts while it chases Pac-Man.

        `ghosts` is the list of all four ghosts, with Blinky first (Inky needs him).
        """
        raise NotImplementedError


class Blinky(Personality):
    """The direct pursuer: hunts the tile Pac-Man is on."""

    def find_corner(self, maze: Maze) -> Tile:
        """Return the top-right corner."""
        return (maze.width - 1, 0)  # top-right

    def target(self, ghost, pacman, ghosts) -> Tile:
        """Return the tile Pac-Man is on."""
        return pacman.tile


class Pinky(Personality):
    """The ambusher: hunts the tile four tiles in front of Pac-Man."""

    def find_corner(self, maze: Maze) -> Tile:
        """Return the top-left corner."""
        return (0, 0)  # top-left

    def target(self, ghost, pacman, ghosts) -> Tile:
        """Return the tile four tiles in front of Pac-Man."""
        return ahead(pacman, config.PINKY_AHEAD)


class Inky(Personality):
    """The unpredictable one: his target depends on both Pac-Man and Blinky."""

    def find_corner(self, maze: Maze) -> Tile:
        """Return the bottom-right corner."""
        return (maze.width - 1, maze.height - 1)  # bottom-right

    def target(self, ghost, pacman, ghosts) -> Tile:
        """Return Blinky's position mirrored through the tile two tiles in front of Pac-Man."""
        # The pivot is two tiles in front of Pac-Man. The vector from Blinky to
        # the pivot is doubled: target = blinky + 2 * (pivot - blinky).
        pivot = ahead(pacman, config.INKY_AHEAD)
        blinky = ghosts[0].tile
        return (2 * pivot[0] - blinky[0], 2 * pivot[1] - blinky[1])


class Clyde(Personality):
    """Chases Pac-Man from far away, then loses his nerve and goes to his corner."""

    def find_corner(self, maze: Maze) -> Tile:
        """Return the bottom-left corner."""
        return (0, maze.height - 1)  # bottom-left

    def target(self, ghost, pacman, ghosts) -> Tile:
        """Return Pac-Man's tile when far from him, otherwise the corner."""
        if math.dist(ghost.tile, pacman.tile) >= config.CLYDE_RADIUS:
            return pacman.tile
        return self.corner


# One personality class per ghost, in the order of config.GHOST_NAMES.
PERSONALITIES = (Blinky, Pinky, Inky, Clyde)
