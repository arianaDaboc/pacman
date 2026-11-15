"""Sound effects. Pygame is used only in the view package (and the game loop)."""

import pygame

from pacman import config


class Sounds:
    """Loads every effect once and plays it, unless the sound is muted."""

    def __init__(self) -> None:
        """Load assets/sounds/<name>.wav for every name in config.SOUND_NAMES."""
        self.muted = False
        self.effects: dict[str, pygame.mixer.Sound] = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            for name in config.SOUND_NAMES:
                self.effects[name] = pygame.mixer.Sound(config.SOUNDS_DIR / f"{name}.wav")
        except pygame.error:
            self.effects = {}  # no audio device: the game still runs, silently

    def play(self, name: str) -> None:
        """Play one effect by name."""
        if not self.muted and name in self.effects:
            self.effects[name].play()

    def toggle_mute(self) -> None:
        """Switch the sound off or back on."""
        self.muted = not self.muted
