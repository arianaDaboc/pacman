"""Draws the ghosts with their sprites: normal, frightened (blue, flashing at the end) or eaten (eyes)."""

import pygame

from pacman import config
from pacman.model.ghost_state import GhostState


class GhostView:
    """One sprite per ghost and per look, scaled to the tile size once."""

    def __init__(self, maze_view) -> None:
        """Load the ghost sprites and prepare the white one used for flashing."""
        self.maze_view = maze_view
        self.images = {name: self._load(f"ghost_{colour}.png") for name, colour in config.GHOST_SPRITES.items()}
        self.scared = self._load("ghost_scared.png")
        self.eyes = self._load("ghost_eyes.png")
        # The flash sprite is the scared one made much lighter. BLEND_RGB_ADD adds
        # to the colours only, so the transparent pixels stay transparent.
        self.flash = self.scared.copy()
        self.flash.fill(config.FLASH_BRIGHTEN, special_flags=pygame.BLEND_RGB_ADD)
        self.time = 0.0

    def _load(self, file_name: str) -> pygame.Surface:
        """Load one sprite and scale it to the size of a tile."""
        image = pygame.image.load(config.SPRITES_DIR / file_name).convert_alpha()
        return pygame.transform.scale(image, (config.TILE_SIZE, config.TILE_SIZE))

    def update(self, dt: float) -> None:
        """Advance the clock of the flashing animation."""
        self.time += dt

    def draw(self, surface: pygame.Surface, ghosts, flashing: bool = False) -> None:
        """Draw every ghost at its position (between tiles while it moves).

        `flashing` is True in the last seconds of the frightened time.
        """
        white_now = flashing and int(self.time * config.FLASH_FPS) % 2 == 0
        for ghost in ghosts:
            if ghost.state is GhostState.EATEN:
                image = self.eyes
            elif ghost.state is GhostState.FRIGHTENED:
                image = self.flash if white_now else self.scared
            else:
                image = self.images[ghost.name]
            x = self.maze_view.origin[0] + ghost.x * config.TILE_SIZE
            y = self.maze_view.origin[1] + ghost.y * config.TILE_SIZE
            surface.blit(image, (round(x), round(y)))
