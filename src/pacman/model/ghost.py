"""A ghost: waits in the house, leaves it, then wanders the maze at random. No pygame here."""

import math
import random
from collections import deque

from pacman import config
from pacman.model.maze import Maze, Tile


def _next_centre(pos: float, direction: int) -> float:
    """Return the next tile centre in the direction of travel."""
    if direction > 0:
        return math.floor(pos) + 1
    if direction < 0:
        return math.ceil(pos) - 1
    return pos


class Ghost:
    """Moves from tile centre to tile centre and chooses a direction only at a centre."""

    def __init__(self, maze: Maze, name: str, start: Tile, dots_to_leave: int, rng: random.Random) -> None:
        """Remember the maze and the start, then put the ghost at its start."""
        self.maze = maze
        self.name = name
        self.start = start
        self.dots_to_leave = dots_to_leave
        self.rng = rng
        self.exit = maze.ghost_starts[0]  # the tile just outside the door, where Blinky starts
        self.finder = None  # the PathFinder chosen in the game (BFS by default)
        self.target: Tile | None = None  # the tile the ghost hunts; Pac-Man's tile until US2.4
        self.path: list[Tile] = []  # the tiles still ahead on the current path (overlay of US2.6)
        self.path_target: Tile | None = None  # the target the current path was computed for
        self.expanded = 0  # tiles expanded by the last search
        self.reset()

    def reset(self) -> None:
        """Go back to the start tile, as at the beginning of a life."""
        self.x = float(self.start[0])
        self.y = float(self.start[1])
        self.direction: tuple[int, int] | None = None
        self.in_house = self.start in self.maze.house
        self.path = []
        self.path_target = None

    @property
    def tile(self) -> Tile:
        """The tile that contains the ghost's centre."""
        return (round(self.x) % self.maze.width, round(self.y))

    def update(self, dt: float, dots_eaten: int) -> None:
        """Move for dt seconds. A ghost in the house waits until Pac-Man has eaten enough dots."""
        if self.in_house and dots_eaten < self.dots_to_leave:
            return
        remaining = config.GHOST_SPEED * dt
        while remaining > 1e-9:
            if self._at_centre():
                self._choose_direction()
                if self.direction is None:
                    return
            dx, dy = self.direction
            tx = _next_centre(self.x, dx)
            ty = _next_centre(self.y, dy)
            dist = abs(tx - self.x) + abs(ty - self.y)
            step = min(remaining, dist)
            if step >= dist:
                self.x, self.y = float(round(tx)), float(round(ty))
            else:
                self.x += dx * step
                self.y += dy * step
            self.x %= self.maze.width  # warp tunnel
            remaining -= step

    def _at_centre(self) -> bool:
        """True when the ghost is exactly in the middle of a tile."""
        return abs(self.x - round(self.x)) < 1e-9 and abs(self.y - round(self.y)) < 1e-9

    def _choose_direction(self) -> None:
        """Leave the house along a shortest path, then pick a random exit, never reversing."""
        here = self.tile
        if self.in_house:
            if here == self.exit:
                self.in_house = False
            else:
                step = self._first_step_to(self.exit)
                self.direction = (step[0] - here[0], step[1] - here[1]) if step else None
                return
        if self.finder is not None and self.target is not None:
            if self._follow_path(here):
                return
        options = []
        for d in config.NEIGHBOUR_ORDER:
            n = ((here[0] + d[0]) % self.maze.width, here[1] + d[1])
            # Outside, a ghost stays out of the house (until US2.5 sends the eaten ones back).
            if self.maze.is_walkable(n, config.GHOST) and n not in self.maze.house and n not in self.maze.doors:
                options.append(d)
        if self.direction is not None:
            back = (-self.direction[0], -self.direction[1])
            forward = [d for d in options if d != back]
            if forward:  # reversing is allowed only in a dead end
                options = forward
        self.direction = self.rng.choice(options) if options else None

    def _first_step_to(self, goal: Tile) -> Tile | None:
        """Return the first tile of a shortest path to goal, through the tiles open to ghosts."""
        start = self.tile
        parent: dict[Tile, Tile | None] = {start: None}
        queue = deque([start])
        while queue:
            tile = queue.popleft()
            if tile == goal:
                while parent[tile] != start:
                    tile = parent[tile]
                return tile
            for n in self.maze.neighbours(tile):
                if n not in parent and self.maze.is_walkable(n, config.GHOST):
                    parent[n] = tile
                    queue.append(n)
        return None

    def _follow_path(self, here: Tile) -> bool:
        """Turn towards the next tile of the path to the target. Return False if there is no path.

        The path is searched again only when the target changes (or the old path is used up),
        as the project description asks; otherwise the ghost keeps following it.
        """
        if self.path and self.path[0] == here:
            self.path.pop(0)  # this tile is reached
        if not self.path or self.path_target != self.target:
            banned: set[Tile] = set()
            if self.direction is not None:  # the tile behind: a ghost never reverses on its own
                banned.add(((here[0] - self.direction[0]) % self.maze.width, here[1] - self.direction[1]))
            self.path, self.expanded = self.finder.find_path(self.maze, here, self.target, banned)
            self.path_target = self.target
        if not self.path:
            return False
        nxt = self.path[0]
        dx = nxt[0] - here[0]
        if abs(dx) > 1:  # the step goes through the warp tunnel: 27 -> 0 is one step to the right
            dx = 1 if dx < 0 else -1
        self.direction = (dx, nxt[1] - here[1])
        return True
