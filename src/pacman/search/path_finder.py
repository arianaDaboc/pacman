"""Common interface for all search algorithms (BFS, DFS, UCS, A*, ...)."""

from pacman.model.maze import Maze, Tile


class PathFinder:
    """Base class: each search algorithm overrides find_path."""

    def find_path(self, maze: Maze, start: Tile, goal: Tile, banned: set[Tile]) -> list[Tile]:
        """Return the list of tiles from start to goal, avoiding the banned tiles.

        Returns an empty list if the goal cannot be reached.
        """
        raise NotImplementedError
