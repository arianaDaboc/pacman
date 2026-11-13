"""Decides what Pac-Man does each turn (keyboard or AI)."""


class PacManController:
    """Base class: each controller (human, search-based, ...) overrides get_action."""

    def get_action(self, state: object) -> str:
        """Return the next move for Pac-Man ("UP", "DOWN", "LEFT", "RIGHT" or "STOP").

        `state` is the current game state; its exact type is defined in a later US.
        """
        raise NotImplementedError
