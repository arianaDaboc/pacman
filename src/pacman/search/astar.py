"""A* search with the Manhattan distance as heuristic."""

import heapq
import itertools

from pacman.model.maze import Maze, Tile
from pacman.search.path_finder import PathFinder, SearchResult, rebuild_path, successors


def manhattan(a: Tile, b: Tile, width: int | None = None) -> int:
    """Return the wall-free grid distance, accounting for the side tunnel when width is given."""
    dx = abs(a[0] - b[0])
    if width is not None:
        dx = min(dx, width - dx)
    return dx + abs(a[1] - b[1])


class AStar(PathFinder):
    """Informed search: expands the tile with the lowest f = g + h first."""

    name = "A*"

    def find_path(self, maze: Maze, start: Tile, goal: Tile, banned: set[Tile]) -> SearchResult:
        """See PathFinder.find_path."""
        parent: dict[Tile, Tile | None] = {start: None}
        cost = {start: 0}  # g: steps from start
        order = itertools.count()  # equal f: the tile added first is expanded first
        frontier = [(manhattan(start, goal, maze.width), next(order), start)]
        closed: set[Tile] = set()
        expanded = 0
        while frontier:
            _, _, tile = heapq.heappop(frontier)
            if tile in closed:
                continue  # an older, worse entry for a tile already expanded
            if tile == goal:
                return rebuild_path(parent, goal), expanded
            closed.add(tile)
            expanded += 1
            for n in successors(maze, tile, start, goal, banned):
                if n in closed:
                    continue
                g = cost[tile] + 1
                if n not in cost or g < cost[n]:
                    cost[n] = g
                    parent[n] = tile
                    heapq.heappush(frontier, (g + manhattan(n, goal, maze.width), next(order), n))
        return [], expanded
