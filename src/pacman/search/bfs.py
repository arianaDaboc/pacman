"""Breadth-first search: expands tiles in order of distance, so its path is always a shortest one."""

from collections import deque

from pacman.model.maze import Maze, Tile
from pacman.search.path_finder import PathFinder, SearchResult, rebuild_path, successors


class BFS(PathFinder):
    """Uninformed search with a FIFO queue."""

    name = "BFS"

    def find_path(self, maze: Maze, start: Tile, goal: Tile, banned: set[Tile]) -> SearchResult:
        """See PathFinder.find_path."""
        parent: dict[Tile, Tile | None] = {start: None}
        frontier = deque([start])
        expanded = 0
        while frontier:
            tile = frontier.popleft()
            if tile == goal:
                return rebuild_path(parent, goal), expanded
            expanded += 1
            for n in successors(maze, tile, start, goal, banned):
                if n not in parent:  # seen already: a shorter or equal path to it exists
                    parent[n] = tile
                    frontier.append(n)
        return [], expanded
