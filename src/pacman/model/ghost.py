"""A ghost: its position, its state and how it moves. No pygame here.

The ghost decides only at the centre of a tile. What it does there depends on its state:
in the house it waits or walks out, in scatter and chase it follows a path to its target,
frightened it picks a random exit, and eaten it follows a path back to the house.
"""

import math
import random
from collections import deque

from pacman import config
from pacman.model.ghost_state import GhostState
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

    def __init__(self, maze: Maze, name: str, start: Tile, dots_to_leave: int, personality, rng: random.Random) -> None:
        self.maze = maze
        self.name = name
        self.personality = personality  # chooses the tile this ghost hunts (US2.4)
        self.start = start
        self.dots_to_leave = dots_to_leave
        self.rng = rng
        self.exit = maze.ghost_starts[0]  # the tile just outside the door, where Blinky starts
        # Where the eyes of an eaten ghost go: Pinky's start, in the middle of the house.
        self.home = maze.ghost_starts[1] if maze.ghost_starts[1] in maze.house else min(maze.house)
        self.finder = None  # the PathFinder chosen in the game (BFS by default)
        self.target: Tile | None = None  # the tile the ghost is heading to; None while it has none
        self.path: list[Tile] = []  # the tiles still ahead on the current path (overlay of US2.6)
        self.path_target: Tile | None = None  # the target the current path was computed for
        self.path_length = 0  # length of the last path found
        self.expanded = 0  # tiles expanded by the last search
        self.reset(GhostState.SCATTER)

    def reset(self, mode: GhostState) -> None:
        """Go back to the start tile, as at the beginning of a life.

        `mode` is the current scatter/chase mode: Blinky, who starts outside the house, takes it at once.
        """
        self.x = float(self.start[0])
        self.y = float(self.start[1])
        self.direction: tuple[int, int] | None = None
        self.state = GhostState.IN_HOUSE if self.start in self.maze.house else mode
        self.path = []
        self.path_target = None

    @property
    def tile(self) -> Tile:
        """The tile that contains the ghost's centre."""
        return (round(self.x) % self.maze.width, round(self.y))

    @property
    def in_house(self) -> bool:
        """True while the ghost waits in the house or walks out of it."""
        return self.state is GhostState.IN_HOUSE

    @property
    def speed(self) -> float:
        """Tiles per second: a frightened ghost moves at half speed."""
        if self.state is GhostState.FRIGHTENED:
            return config.GHOST_SPEED * config.FRIGHTENED_SPEED
        return config.GHOST_SPEED

    def set_state(self, state: GhostState) -> None:
        """Change the state. The old path belongs to the old state, so it is dropped."""
        self.state = state
        self.path = []
        self.path_target = None

    def reverse(self) -> None:
        """Turn around at once. Only a change of state may do this; a ghost never reverses on its own."""
        if self.direction is not None:
            self.direction = (-self.direction[0], -self.direction[1])
        self.path = []
        self.path_target = None

    def update(self, dt: float, dots_eaten: int, mode: GhostState) -> None:
        """Move for dt seconds.

        A ghost in the house waits until Pac-Man has eaten enough dots. `mode` is the
        current scatter/chase mode, which the ghost takes when it steps out of the house.
        """
        if self.in_house and dots_eaten < self.dots_to_leave:
            return
        remaining = self.speed * dt
        while remaining > 1e-9:
            if self._at_centre():
                self._choose_direction(mode)
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
        return abs(self.x - round(self.x)) < 1e-9 and abs(self.y - round(self.y)) < 1e-9

    def _choose_direction(self, mode: GhostState) -> None:
        """At a tile centre: decide where to go next, depending on the state."""
        here = self.tile
        if self.state is GhostState.EATEN and here == self.home:
            self.set_state(GhostState.IN_HOUSE)  # the eyes are home: the ghost revives and walks out again
        if self.state is GhostState.IN_HOUSE:
            if here == self.exit:
                self.set_state(mode)  # outside: join the others in the current mode
            else:
                step = self._first_step_to(self.exit)
                self.direction = (step[0] - here[0], step[1] - here[1]) if step else None
                return
        # Scatter, chase and eaten follow a path to the target; frightened has no target.
        if self.finder is not None and self.target is not None and self.state is not GhostState.FRIGHTENED:
            if self._follow_path(here):
                return
        self._random_exit(here)

    def _random_exit(self, here: Tile) -> None:
        """Pick one of the free directions at random, never the one the ghost came from."""
        options = []
        for d in config.NEIGHBOUR_ORDER:
            n = ((here[0] + d[0]) % self.maze.width, here[1] + d[1])
            # Outside, a ghost stays out of the house; only the eyes go back in, along their path.
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
            self.path_length = len(self.path)
            self.path_target = self.target
        if not self.path:
            return False
        nxt = self.path[0]
        dx = nxt[0] - here[0]
        if abs(dx) > 1:  # the step goes through the warp tunnel: 27 -> 0 is one step to the right
            dx = 1 if dx < 0 else -1
        self.direction = (dx, nxt[1] - here[1])
        return True
