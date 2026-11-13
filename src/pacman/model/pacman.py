"""Pac-Man's position and movement, measured in tiles. No pygame here."""

import math

from pacman import config

# Direction name -> change of (column, row). Rows grow downwards.
DIRECTIONS = {
    "up": config.UP,
    "left": config.LEFT,
    "down": config.DOWN,
    "right": config.RIGHT,
}


def _next_centre(pos: float, direction: int) -> float:
    """Return the next tile centre in the direction of travel."""
    if direction > 0:
        return math.floor(pos) + 1
    if direction < 0:
        return math.ceil(pos) - 1
    return pos


class PacMan:
    """Move from tile centre to tile centre, turning only at a centre."""

    def __init__(self, maze, start: tuple[int, int]) -> None:
        self.maze = maze
        self.x = float(start[0])
        self.y = float(start[1])
        self.direction: tuple[int, int] | None = None
        self.wanted: tuple[int, int] | None = None

    def turn(self, name: str) -> None:
        """Remember the requested direction for the next tile centre."""
        try:
            self.wanted = DIRECTIONS[name]
        except KeyError as exc:
            raise ValueError(f"unknown direction {name!r}") from exc

    def update(self, dt: float) -> None:
        """Move for dt seconds, stopping at walls."""
        remaining = max(0.0, config.PACMAN_SPEED * dt)
        while remaining > 1e-9:
            if self._at_centre():
                self._choose_direction()
                if self.direction is None:
                    return

            dx, dy = self.direction
            tx = _next_centre(self.x, dx)
            ty = _next_centre(self.y, dy)
            distance = abs(tx - self.x) + abs(ty - self.y)
            step = min(remaining, distance)
            if step >= distance:
                self.x, self.y = float(round(tx)), float(round(ty))
            else:
                self.x += dx * step
                self.y += dy * step

            # The classic maze wraps horizontally through its side tunnels.
            self.x %= self.maze.width
            remaining -= step

    def _at_centre(self) -> bool:
        return abs(self.x - round(self.x)) < 1e-9 and abs(self.y - round(self.y)) < 1e-9

    def _free(self, direction: tuple[int, int]) -> bool:
        col = (round(self.x) + direction[0]) % self.maze.width
        row = round(self.y) + direction[1]
        return self.maze.is_walkable((col, row), config.PACMAN)

    def _choose_direction(self) -> None:
        if self.wanted is not None and self._free(self.wanted):
            self.direction = self.wanted
        elif self.direction is not None and not self._free(self.direction):
            self.direction = None
