"""Depth-first search: follows one corridor as far as it can, so its path is valid but often long."""

from pacman.model.maze import Maze, Tile
from pacman.search.path_finder import PathFinder, SearchResult, rebuild_path, successors


class DFS(PathFinder):
    """Uninformed search with a LIFO stack."""

    name = "DFS"

    def find_path(self, maze: Maze, start: Tile, goal: Tile, banned: set[Tile]) -> SearchResult:
        """See PathFinder.find_path."""
        parent: dict[Tile, Tile | None] = {start: None}
        stack = [start]
        visited: set[Tile] = set()
        expanded = 0
        while stack:
            tile = stack.pop()
            if tile in visited:
                continue
            visited.add(tile)
            if tile == goal:
                return rebuild_path(parent, goal), expanded
            expanded += 1
            # Pushed in reverse, so they come off the stack in the order up, left, down, right.
            for n in reversed(successors(maze, tile, start, goal, banned)):
                if n not in visited:
                    parent[n] = tile
                    stack.append(n)
        return [], expanded
