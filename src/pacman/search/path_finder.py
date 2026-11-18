"""Common interface for the ghosts' search algorithms (DFS, BFS, A*, greedy). No pygame here."""

from pacman import config
from pacman.model.maze import Maze, Tile

SearchResult = tuple[list[Tile], int]
"""(path, expanded): the tiles from the first step to the goal, and how many tiles were expanded."""


class PathFinder:
    """Base class: each search algorithm overrides find_path."""

    name = "?"

    def find_path(self, maze: Maze, start: Tile, goal: Tile, banned: set[Tile]) -> SearchResult:
        """Return (path, expanded).

        The path holds the tiles after start, up to and including goal; it is
        empty if start == goal or if the goal cannot be reached. The first step
        may not use a banned tile (the tile behind the ghost), unless it is the
        only way out. Neighbours are expanded in the order up, left, down, right.
        """
        raise NotImplementedError


def successors(maze: Maze, tile: Tile, start: Tile, goal: Tile, banned: set[Tile]) -> list[Tile]:
    """Return the tiles a ghost can step to from tile, in the order up, left, down, right.

    The ghost house and its door are used only by a search that starts or ends inside them
    (a ghost leaving the house, or going back to it); every other path stays in the corridors.
    On the first step (tile == start) the banned tiles are skipped, unless they are the only way out.
    """
    inside = maze.house | maze.doors
    use_house = start in inside or goal in inside
    free = [
        n for n in maze.neighbours(tile) if maze.is_walkable(n, config.GHOST) and (use_house or n not in inside)
    ]
    if tile == start:
        allowed = [n for n in free if n not in banned]
        return allowed or free
    return free


def rebuild_path(parent: dict[Tile, Tile | None], goal: Tile) -> list[Tile]:
    """Follow the parents back from goal and return the path without the start tile."""
    path = []
    tile = goal
    while parent[tile] is not None:
        path.append(tile)
        tile = parent[tile]
    path.reverse()
    return path
