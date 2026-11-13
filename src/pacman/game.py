"""The game loop. Pygame is used only here and in the view package."""

from pathlib import Path

import pygame

from pacman import config
from pacman.model.maze import Maze
from pacman.view.maze_view import MazeView


class Game:
    """Owns the window and runs the loop at a fixed frame rate."""

    def __init__(self, map_path: Path = config.MAP_PATH) -> None:
        """Load the map, then open the window. Raises MapError if the map is invalid."""
        # The map is loaded before pygame starts, so an invalid map stops the
        # program with a clear message instead of flashing an empty window.
        self.maze = Maze.load(map_path)
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.maze_view = MazeView(self.maze)
        self.running = True

    def handle_events(self) -> None:
        """Process the window events. Closing the window stops the loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self, dt: float) -> None:
        """Advance the game model by dt seconds. Empty until the agents move."""

    def draw(self) -> None:
        """Draw one frame: background, then the maze."""
        self.screen.fill(config.BACKGROUND_COLOUR)
        self.maze_view.draw(self.screen)
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
