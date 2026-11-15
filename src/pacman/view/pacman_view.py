"""Draws Pac-Man with the animated sprites from assets/sprites."""

import pygame

from pacman import config

SPRITE_NAMES = {
    config.UP: "up",
    config.LEFT: "left",
    config.DOWN: "down",
    config.RIGHT: "right",
}


class PacManView:
    """Animates Pac-Man's mouth and turns the sprite to face his direction."""

    def __init__(self, maze_view) -> None:
        size = (config.TILE_SIZE, config.TILE_SIZE)
        self.maze_view = maze_view
        self.frames = {
            name: [
                pygame.transform.scale(
                    pygame.image.load(config.SPRITES_DIR / f"pacman_{name}_{i}.png").convert_alpha(), size
                )
                for i in range(config.PACMAN_FRAMES)
            ]
            for name in SPRITE_NAMES.values()
        }
        self.facing = "right"
        self.time = 0.0

    def update(self, pacman, dt: float) -> None:
        """Advance the mouth animation while Pac-Man is moving."""
        if pacman.direction is not None:
            self.facing = SPRITE_NAMES[pacman.direction]
            self.time += dt

    def draw(self, surface: pygame.Surface, pacman) -> None:
        """Draw Pac-Man at his current position, including between tile centres."""
        frame = int(self.time * config.PACMAN_ANIMATION_FPS) % config.PACMAN_FRAMES
        x = self.maze_view.origin[0] + pacman.x * config.TILE_SIZE
        y = self.maze_view.origin[1] + pacman.y * config.TILE_SIZE
        surface.blit(self.frames[self.facing][frame], (round(x), round(y)))
