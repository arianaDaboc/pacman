"""The states of a ghost and the global timer that switches between scatter and chase. No pygame here."""

from enum import Enum

from pacman import config


class GhostState(Enum):
    """Every ghost is always in exactly one of these states (section 3.5 of the project description)."""

    IN_HOUSE = "house"  # waiting in the ghost house, or on its way out through the door
    SCATTER = "scatter"  # goes to its own corner
    CHASE = "chase"  # hunts the tile chosen by its personality
    FRIGHTENED = "frightened"  # slow, wanders at random, Pac-Man can eat it
    EATEN = "eaten"  # only the eyes: they return to the house


class ModeTimer:
    """Alternates scatter and chase on the schedule of Table 6, and counts the frightened time.

    There is one timer for all the ghosts. While the ghosts are frightened,
    the scatter/chase schedule is paused.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Start the schedule again from its first phase (a new game, or a new life)."""
        self.phase = 0  # index in config.MODE_SCHEDULE
        self.phase_left = config.MODE_SCHEDULE[0][1]  # seconds until the next phase
        self.fright_left = 0.0  # seconds of frightened time still to go; 0 means not frightened

    @property
    def mode(self) -> GhostState:
        """The current mode: GhostState.SCATTER or GhostState.CHASE."""
        if self.phase >= len(config.MODE_SCHEDULE):
            return GhostState.CHASE  # after the last phase of the table: chase for ever
        return GhostState(config.MODE_SCHEDULE[self.phase][0])

    @property
    def frightened(self) -> bool:
        """True while an energizer is still working."""
        return self.fright_left > 0

    @property
    def flashing(self) -> bool:
        """True in the last seconds of the frightened time, when the ghosts flash as a warning."""
        return 0 < self.fright_left <= config.FLASH_SECONDS

    def start_fright(self) -> None:
        """Pac-Man ate an energizer: the frightened time starts, or starts again."""
        self.fright_left = config.FRIGHTENED_SECONDS

    def update(self, dt: float) -> bool:
        """Advance the timer by dt seconds. Return True if the mode changed between scatter and chase."""
        if self.frightened:
            self.fright_left = max(0.0, self.fright_left - dt)
            return False  # the schedule is paused meanwhile
        if self.phase >= len(config.MODE_SCHEDULE):
            return False
        self.phase_left -= dt
        if self.phase_left > 0:
            return False
        self.phase += 1
        if self.phase < len(config.MODE_SCHEDULE):
            self.phase_left += config.MODE_SCHEDULE[self.phase][1]
        return True
