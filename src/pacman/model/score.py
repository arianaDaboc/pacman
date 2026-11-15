"""The score (Table 7 of the project description). Pure logic, no pygame."""

from pacman import config


class Score:
    """Keeps the points and counts what Pac-Man ate."""

    def __init__(self) -> None:
        """Start a new game with 0 points and nothing eaten."""
        self.points = 0
        self.dots_eaten = 0
        self.ghosts_in_a_row = 0  # ghosts eaten with the current energizer

    def eat_dot(self) -> None:
        """Add the points for a dot and count it."""
        self.points += config.DOT_POINTS
        self.dots_eaten += 1

    def eat_energizer(self) -> None:
        """Add the points for an energizer and restart the ghost combo."""
        self.points += config.ENERGIZER_POINTS
        self.ghosts_in_a_row = 0  # a new energizer starts the count again

    def eat_ghost(self) -> None:
        """Add 200, 400, 800 or 1600 points, depending on how many ghosts were eaten with this energizer."""
        index = min(self.ghosts_in_a_row, len(config.GHOST_POINTS) - 1)
        self.points += config.GHOST_POINTS[index]
        self.ghosts_in_a_row += 1

    def eat_fruit(self) -> None:
        """Add the points for the fruit."""
        self.points += config.FRUIT_POINTS

    def caught(self) -> None:
        """Take away points when a ghost catches Pac-Man."""
        self.points += config.CAUGHT_POINTS

    def fruit_due(self) -> bool:
        """True right after the dot that makes the fruit appear (the 70th and the 170th)."""
        return self.dots_eaten in config.FRUIT_AFTER_DOTS
