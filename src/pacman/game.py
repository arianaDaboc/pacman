"""The game loop. Pygame is used only here and in the view package."""

from pathlib import Path

import pygame

from pacman import config
from pacman.model.maze import Maze
from pacman.model.pacman import PacMan
from pacman.view.maze_view import MazeView

ARROWS = {
    pygame.K_UP: "up",
    pygame.K_LEFT: "left",
    pygame.K_DOWN: "down",
    pygame.K_RIGHT: "right",
}


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
        self.pacman = PacMan(self.maze, self.maze.pacman_start)
        self.running = True

    def handle_events(self) -> None:
        """Process the window events. Closing the window stops the loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key in ARROWS:
                self.pacman.turn(ARROWS[event.key])

    def update(self, dt: float) -> None:
        """Advance the game model by dt seconds."""
        self.pacman.update(dt)

    def draw(self) -> None:
        """Draw one frame: background, then the maze."""
        self.screen.fill(config.BACKGROUND_COLOUR)
        self.maze_view.draw(self.screen)
        half = config.TILE_SIZE / 2
        center = (
            round(self.maze_view.origin[0] + (self.pacman.x + 0.5) * config.TILE_SIZE),
            round(self.maze_view.origin[1] + (self.pacman.y + 0.5) * config.TILE_SIZE),
        )
        pygame.draw.circle(self.screen, (255, 255, 0), center, int(half) - 2)
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
