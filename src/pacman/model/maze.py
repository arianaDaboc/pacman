"""The maze: a grid of tiles loaded from a map file (implemented in US1.1)."""

Tile = tuple[int, int]
"""A position in the grid, as (column, row)."""


class Maze:
    """The grid of walls and free tiles that every agent moves on."""

    def is_walkable(self, tile: Tile, agent: str) -> bool:
        """Return True if the given agent may stand on this tile.

        The agent matters because some tiles (e.g. the ghost house door)
        are open to ghosts but closed to Pac-Man.
        """
        raise NotImplementedError

    def neighbours(self, tile: Tile) -> list[Tile]:
        """Return the tiles adjacent to this one (up, down, left, right)."""
        raise NotImplementedError
