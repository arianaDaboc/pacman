"""Common interface for the ghosts' search algorithms (DFS, BFS, A*, greedy). No pygame here."""

from functools import lru_cache

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
    free = [n for n in maze.neighbours(tile) if maze.is_walkable(n, config.GHOST) and (use_house or n not in inside)]
    if tile == start:
        allowed = [n for n in free if n not in banned]
        return allowed or free
    return free


@lru_cache(maxsize=8)
def corridors(maze: Maze) -> tuple[Tile, ...]:
    """Return every tile Pac-Man can walk on, in reading order. Computed once per maze, then remembered."""
    return tuple(
        (x, y) for y in range(maze.height) for x in range(maze.width) if maze.is_walkable((x, y), config.PACMAN)
    )


def closest_walkable(maze: Maze, tile: Tile) -> Tile:
    """Return tile itself if it is a corridor tile, otherwise the corridor tile closest to it.

    A personality can ask for a wall or for a tile outside the maze (for example four tiles
    in front of Pac-Man). The ghost then aims at the closest corridor tile, measured in a
    straight line; if several are equally close, the first one in reading order wins.
    """
    if maze.is_walkable(tile, config.PACMAN):
        return tile
    return min(corridors(maze), key=lambda c: (c[0] - tile[0]) ** 2 + (c[1] - tile[1]) ** 2)


def rebuild_path(parent: dict[Tile, Tile | None], goal: Tile) -> list[Tile]:
    """Follow the parents back from goal and return the path without the start tile."""
    path = []
    tile = goal
    while parent[tile] is not None:
        path.append(tile)
        tile = parent[tile]
    path.reverse()
    return path
