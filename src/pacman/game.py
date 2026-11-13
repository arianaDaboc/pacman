"""The game loop. Pygame is used only here and in the view package."""

import pygame

from pacman import config


class Game:
    """Owns the window and runs the loop at a fixed frame rate."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

    def handle_events(self) -> None:
        """Process the window events. Closing the window stops the loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float) -> None:
        """Advance the game model by dt seconds. Empty until US1.1."""

    def draw(self) -> None:
        """Draw one frame. Empty until US1.1."""
        self.screen.fill((0, 0, 0))
        pygame.display.flip()

    def run(self) -> None:
        """Run the loop until the window is closed, then release pygame."""
        try:
            while self.running:
                self.handle_events()
                dt = self.clock.tick(config.FPS) / 1000
                self.update(dt)
                self.draw()
        finally:
            pygame.quit()
