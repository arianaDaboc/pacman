"""The game loop. Pygame is used only here and in the view package."""

from pathlib import Path

import pygame

from pacman import config
from pacman.model.maze import Maze
from pacman.model.pacman import PacMan
from pacman.model.score import Score
from pacman.view.maze_view import MazeView
from pacman.view.pacman_view import PacManView

ARROWS = {
    pygame.K_UP: "up",
    pygame.K_LEFT: "left",
    pygame.K_DOWN: "down",
    pygame.K_RIGHT: "right",
}

NEW_GAME_KEYS = (pygame.K_RETURN, pygame.K_SPACE)


class Game:
    """Owns the window and runs the loop at a fixed frame rate."""

    def __init__(self, map_path: Path = config.MAP_PATH) -> None:
        """Load the map, then open the window. Raises MapError if the map is invalid."""
        # The map is loaded before pygame starts, so an invalid map stops the
        # program with a clear message instead of flashing an empty window.
        self.map_path = map_path
        maze = Maze.load(map_path)
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE)
        self.big_font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE * 2)
        fruit = pygame.image.load(config.FRUIT_SPRITE).convert_alpha()
        self.fruit_image = pygame.transform.scale(fruit, (config.TILE_SIZE, config.TILE_SIZE))
        self.running = True
        self.new_game(maze)

    def new_game(self, maze: Maze | None = None) -> None:
        """Start a new game: all dots back, Pac-Man at the start, score 0, full lives."""
        self.maze = maze if maze is not None else Maze.load(self.map_path)
        self.maze_view = MazeView(self.maze)
        self.pacman = PacMan(self.maze, self.maze.pacman_start)
        self.pacman_view = PacManView(self.maze_view)
        self.score = Score()
        self.lives = config.LIVES
        self.fruit_timer = 0.0  # seconds the fruit stays in the maze; 0 means no fruit
        self.won = False

    def handle_events(self) -> None:
        """Process the window events. Closing the window stops the loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.won and event.key in NEW_GAME_KEYS:
                    self.new_game()
                elif not self.won and event.key in ARROWS:
                    self.pacman.turn(ARROWS[event.key])

    def update(self, dt: float) -> None:
        """Advance the game model by dt seconds."""
        if self.won:
            return
        self.pacman.update(dt)
        self.pacman_view.update(self.pacman, dt)
        self.eat()
        if self.fruit_timer > 0:
            self.fruit_timer = max(0.0, self.fruit_timer - dt)
        if not self.maze.dots and not self.maze.energizers:
            self.won = True

    def eat(self) -> None:
        """Eat what is on Pac-Man's tile: a dot, an energizer or the fruit."""
        tile = (round(self.pacman.x) % self.maze.width, round(self.pacman.y))
        if tile in self.maze.dots:
            self.maze.dots.remove(tile)
            self.score.eat_dot()
            if self.score.fruit_due():
                self.fruit_timer = config.FRUIT_SECONDS
        elif tile in self.maze.energizers:
            self.maze.energizers.remove(tile)
            self.score.eat_energizer()
        if self.fruit_timer > 0 and tile == self.maze.fruit:
            self.score.eat_fruit()
            self.fruit_timer = 0.0

    def draw(self) -> None:
        """Draw one frame: background, maze, fruit, Pac-Man, the panel and maybe the win screen."""
        self.screen.fill(config.BACKGROUND_COLOUR)
        self.maze_view.draw(self.screen)
        if self.fruit_timer > 0 and self.maze.fruit is not None:
            centre = self.maze_view.tile_centre(self.maze.fruit)
            self.screen.blit(self.fruit_image, self.fruit_image.get_rect(center=centre))
        self.pacman_view.draw(self.screen, self.pacman)
        self.draw_panel()
        if self.won:
            self.draw_win_screen()
        pygame.display.flip()

    def draw_panel(self) -> None:
        """Show the score on the left and the lives on the right, under the maze."""
        left = self.maze_view.origin[0]
        right = left + self.maze.width * config.TILE_SIZE
        top = self.maze_view.origin[1] + self.maze.height * config.TILE_SIZE
        y = top + (config.HUD_HEIGHT - self.font.get_height()) // 2
        score = self.font.render(f"SCORE {self.score.points}", True, config.TEXT_COLOUR)
        lives = self.font.render(f"LIVES {self.lives}", True, config.TEXT_COLOUR)
        self.screen.blit(score, (left, y))
        self.screen.blit(lives, (right - lives.get_width(), y))

    def draw_win_screen(self) -> None:
        """Darken the maze and show the final score and how to start again."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(config.WIN_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        lines = [
            (self.big_font, "YOU WIN!"),
            (self.font, f"FINAL SCORE {self.score.points}"),
            (self.font, "PRESS ENTER FOR A NEW GAME"),
        ]
        y = config.SCREEN_HEIGHT // 3
        for font, text in lines:
            image = font.render(text, True, config.TEXT_COLOUR)
            self.screen.blit(image, image.get_rect(midtop=(config.SCREEN_WIDTH // 2, y)))
            y += image.get_height() * 2

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
