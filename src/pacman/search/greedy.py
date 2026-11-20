"""Greedy best-first search: always expands the tile that looks closest to the goal. No pygame here."""

import heapq
import itertools

from pacman.model.maze import Maze, Tile
from pacman.search.astar import manhattan
from pacman.search.path_finder import PathFinder, SearchResult, rebuild_path, successors


class GreedyBestFirst(PathFinder):
    """Informed search that orders the frontier by the heuristic h alone (A* uses g + h).

    It ignores how long the path already is, so it usually expands few tiles,
    but its path is not always a shortest one.
    """

    name = "GREEDY"

    def find_path(self, maze: Maze, start: Tile, goal: Tile, banned: set[Tile]) -> SearchResult:
        """See PathFinder.find_path."""
        parent: dict[Tile, Tile | None] = {start: None}
        order = itertools.count()  # equal h: the tile added first is expanded first
        frontier = [(manhattan(start, goal), next(order), start)]
        expanded = 0
        while frontier:
            _, _, tile = heapq.heappop(frontier)
            if tile == goal:
                return rebuild_path(parent, goal), expanded
            expanded += 1
            for n in successors(maze, tile, start, goal, banned):
                if n not in parent:  # each tile is added once: its first parent is kept
                    parent[n] = tile
                    heapq.heappush(frontier, (manhattan(n, goal), next(order), n))
        return [], expanded
