"""The maze: a grid of tiles loaded from a map file.

This module must not import pygame (architecture rule). It only knows about
tiles, so the search algorithms and the tests can use it without a window.
"""

from collections import deque
from pathlib import Path

from pacman import config

Tile = tuple[int, int]
"""A position in the grid, as (column, row); (0, 0) is the top-left corner."""

ALLOWED_CHARS = set(
    config.WALL
    + config.DOT
    + config.ENERGIZER
    + config.EMPTY
    + config.DOOR
    + config.HOUSE
    + config.PACMAN_START
    + config.GHOST_STARTS
    + config.FRUIT
)

# Elements that must appear exactly once, with a readable name for error messages.
UNIQUE_ELEMENTS = {
    config.PACMAN_START: "Pac-Man start",
    config.GHOST_STARTS[0]: "Blinky start",
    config.GHOST_STARTS[1]: "Pinky start",
    config.GHOST_STARTS[2]: "Inky start",
    config.GHOST_STARTS[3]: "Clyde start",
    config.FRUIT: "fruit spot",
}


def _reading_order(tile: Tile) -> tuple[int, int]:
    """Sort key: row first, then column, like reading a text file."""
    return (tile[1], tile[0])


class MapError(ValueError):
    """Raised when a map file breaks one of the map requirements."""


class Maze:
    """The grid of walls and free tiles that every agent moves on."""

    def __init__(self, rows: list[str], source: str = "<map>", full_validation: bool = True) -> None:
        """Build a maze from the lines of a map file and validate it.

        `source` is only used in error messages (usually the file name).
        Small test maps can pass full_validation=False: then only the format is
        checked (same line length, known characters), not the game requirements.
        Raises MapError if the map is invalid.
        """
        self.rows = rows
        self.source = source
        self._check_format()
        self.width = len(rows[0])
        self.height = len(rows)

        self.dots: set[Tile] = self._find(config.DOT)
        self.energizers: set[Tile] = self._find(config.ENERGIZER)
        self.doors: set[Tile] = self._find(config.DOOR)
        self.pacman_start: Tile | None = self._first(config.PACMAN_START)
        self.ghost_starts: list[Tile | None] = [self._first(c) for c in config.GHOST_STARTS]
        self.fruit: Tile | None = self._first(config.FRUIT)

        # The house is every 'H' tile plus the ghost starts placed inside it.
        # A ghost start counts as inside if it touches an 'H' tile; this way a
        # start right above the door (Blinky) stays a normal corridor tile.
        self.house: set[Tile] = self._find(config.HOUSE)
        for start in self.ghost_starts:
            if start and any(self._char(n) == config.HOUSE for n in self.neighbours(start)):
                self.house.add(start)

        if full_validation:
            self._check_requirements()

    @classmethod
    def load(cls, path: Path | str, full_validation: bool = True) -> "Maze":
        """Read a map file and return the validated maze. Raises MapError if invalid."""
        rows = Path(path).read_text(encoding="utf-8").splitlines()
        while rows and rows[-1] == "":  # ignore empty lines at the end of the file
            rows.pop()
        return cls(rows, str(path), full_validation)

    # ----- Public queries -------------------------------------------------

    def is_walkable(self, tile: Tile, agent: str) -> bool:
        """Return True if the agent (config.PACMAN or config.GHOST) may stand on this tile.

        Walls block everyone. The ghost house and its door are open to ghosts only.
        Tiles outside the grid are never walkable.
        """
        if agent not in (config.PACMAN, config.GHOST):
            raise ValueError(f"unknown agent {agent!r}")
        char = self._char(tile)
        if char is None or char == config.WALL:
            return False
        if agent == config.GHOST:
            return True
        return char != config.DOOR and tile not in self.house

    def neighbours(self, tile: Tile) -> list[Tile]:
        """Return the adjacent tiles in the order up, left, down, right.

        Moving off the left or right edge wraps to the other side of the same
        row, which is how the warp tunnel works. The result can include walls:
        callers filter it with is_walkable, because only they know the agent.
        """
        x, y = tile
        result = []
        for dx, dy in config.NEIGHBOUR_ORDER:
            nx = (x + dx) % self.width  # -1 becomes width-1, and width becomes 0
            ny = y + dy
            if 0 <= ny < self.height:  # no wrapping at the top and bottom
                result.append((nx, ny))
        return result

    # ----- Helpers ----------------------------------------------------------

    def _char(self, tile: Tile) -> str | None:
        """Return the map character at a tile, or None if the tile is outside the grid."""
        x, y = tile
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.rows[y][x]
        return None

    def _tiles(self) -> list[Tile]:
        """Return every tile of the grid in reading order."""
        return [(x, y) for y in range(self.height) for x in range(self.width)]

    def _find(self, char: str) -> set[Tile]:
        """Return all tiles that contain the given character."""
        return {tile for tile in self._tiles() if self._char(tile) == char}

    def _first(self, char: str) -> Tile | None:
        """Return the first tile (in reading order) with this character, or None."""
        found = sorted(self._find(char), key=_reading_order)
        return found[0] if found else None

    def _error(self, message: str, tile: Tile | None = None) -> MapError:
        """Build a MapError. Tiles are 0-based, but lines and columns are shown 1-based, like in an editor."""
        if tile is None:
            return MapError(f"{self.source}: {message}")
        x, y = tile
        return MapError(f"{self.source}, line {y + 1}, column {x + 1}: {message}")

    def _connected(self, start: Tile, allowed: set[Tile]) -> set[Tile]:
        """Breadth-first search: all tiles of `allowed` that can be reached from start."""
        seen = {start}
        queue = deque([start])
        while queue:
            for n in self.neighbours(queue.popleft()):
                if n in allowed and n not in seen:
                    seen.add(n)
                    queue.append(n)
        return seen

    # ----- Validation -------------------------------------------------------

    def _check_format(self) -> None:
        """Check the map is a non-empty rectangle made only of known characters."""
        if not self.rows:
            raise MapError(f"{self.source}: the map is empty")
        width = len(self.rows[0])
        for y, row in enumerate(self.rows):
            if len(row) != width:
                raise MapError(
                    f"{self.source}, line {y + 1}: has {len(row)} characters, "
                    f"expected {width} (all lines must have the same length)"
                )
            for x, char in enumerate(row):
                if char not in ALLOWED_CHARS:
                    raise MapError(f"{self.source}, line {y + 1}, column {x + 1}: unknown character {char!r}")

    def _check_requirements(self) -> None:
        """Check every game requirement; raise MapError on the first one that fails."""
        # 1. Elements that must appear exactly once, and the energizers.
        for char, name in UNIQUE_ELEMENTS.items():
            found = sorted(self._find(char), key=_reading_order)
            if not found:
                raise self._error(f"missing {name} ({char!r})")
            if len(found) > 1:
                raise self._error(f"second {name} ({char!r}); exactly one is allowed", found[1])
        if len(self.energizers) != config.ENERGIZER_COUNT:
            raise self._error(f"has {len(self.energizers)} energizers, expected {config.ENERGIZER_COUNT}")

        # 2. Exactly one ghost house, with a door attached to it.
        if not self.house:
            raise self._error(f"missing ghost house ({config.HOUSE!r})")
        first_house_tile = min(self.house, key=_reading_order)
        one_house = self._connected(first_house_tile, self.house)
        if one_house != self.house:
            other = min(self.house - one_house, key=_reading_order)
            raise self._error("a second ghost house starts here; exactly one is allowed", other)
        if not self.doors:
            raise self._error(f"missing ghost house door ({config.DOOR!r})")
        for door in sorted(self.doors, key=_reading_order):
            if not any(n in self.house for n in self.neighbours(door)):
                raise self._error("door is not attached to the ghost house", door)

        # 3. At least one warp tunnel: corridor tiles at both ends of the same row.
        last = self.width - 1
        if not any(
            self.is_walkable((0, y), config.PACMAN) and self.is_walkable((last, y), config.PACMAN)
            for y in range(self.height)
        ):
            raise self._error("no warp tunnel (a row with corridor tiles at both the left and right edge)")

        # 4. Enough dots.
        if len(self.dots) < config.MIN_DOTS:
            raise self._error(f"has {len(self.dots)} dots, at least {config.MIN_DOTS} are needed")

        # 5. The maze and the control panel fit on the screen.
        width_px = self.width * config.TILE_SIZE
        height_px = self.height * config.TILE_SIZE + config.HUD_HEIGHT
        if width_px > config.SCREEN_WIDTH or height_px > config.SCREEN_HEIGHT:
            raise self._error(
                f"is {self.width} x {self.height} tiles = {width_px} x {height_px} px with the panel, "
                f"but the screen is {config.SCREEN_WIDTH} x {config.SCREEN_HEIGHT} px"
            )

        corridors = {t for t in self._tiles() if self.is_walkable(t, config.PACMAN)}

        # 6. No dead ends: every corridor tile has at least two free neighbours.
        for tile in sorted(corridors, key=_reading_order):
            free = sum(n in corridors for n in self.neighbours(tile))
            if free < 2:
                raise self._error(f"dead end: this corridor tile has only {free} free neighbour(s)", tile)

        # 7. Every corridor tile can be reached from Pac-Man's start.
        unreachable = corridors - self._connected(self.pacman_start, corridors)
        if unreachable:
            raise self._error(
                "this corridor tile cannot be reached from Pac-Man's start",
                min(unreachable, key=_reading_order),
            )
