"""The game loop. Pygame is used only here and in the view package."""

import random
from pathlib import Path

import pygame

from pacman import config
from pacman.model.ghost import Ghost
from pacman.model.ghost_state import GhostState, ModeTimer
from pacman.model.maze import Maze
from pacman.model.pacman import PacMan
from pacman.model.personality import PERSONALITIES
from pacman.model.score import Score
from pacman.search.astar import AStar
from pacman.search.bfs import BFS
from pacman.search.dfs import DFS
from pacman.search.path_finder import closest_walkable
from pacman.view.ghost_view import GhostView
from pacman.view.maze_view import MazeView
from pacman.view.overlay import Overlay
from pacman.view.pacman_view import PacManView
from pacman.view.sound import Sounds

ARROWS = {
    pygame.K_UP: "up",
    pygame.K_LEFT: "left",
    pygame.K_DOWN: "down",
    pygame.K_RIGHT: "right",
}

NEW_GAME_KEYS = (pygame.K_RETURN, pygame.K_SPACE)

# The number keys choose the ghosts' search algorithm, in the order of Game.finders.
FINDER_KEYS = (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4)


class Game:
    """Owns the window and runs the loop at a fixed frame rate."""

    def __init__(self, map_path: Path = config.MAP_PATH, full_validation: bool = True) -> None:
        """Load the map, then open the window. Raises MapError if the map is invalid.

        full_validation=False is for small test maps: only the file format is checked.
        """
        # The map is loaded before pygame starts, so an invalid map stops the
        # program with a clear message instead of flashing an empty window.
        self.map_path = map_path
        self.full_validation = full_validation
        maze = Maze.load(map_path, full_validation)
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE)
        self.big_font = pygame.font.Font(config.FONT_PATH, config.FONT_SIZE * 2)
        fruit = pygame.image.load(config.FRUIT_SPRITE).convert_alpha()
        self.fruit_image = pygame.transform.scale(fruit, (config.TILE_SIZE, config.TILE_SIZE))
        self.sounds = Sounds()
        self.finders = [DFS(), BFS(), AStar()]  # the search algorithms the ghosts can use
        self.finder = self.finders[1]  # BFS until the player chooses another one
        self.started = False  # the start screen is shown until Enter or Space is pressed
        self.running = True
        self.new_game(maze)

    def new_game(self, maze: Maze | None = None) -> None:
        """Start a new game: all dots back, Pac-Man at the start, score 0, full lives."""
        self.maze = maze if maze is not None else Maze.load(self.map_path, self.full_validation)
        self.maze_view = MazeView(self.maze)
        self.pacman = PacMan(self.maze, self.maze.pacman_start)
        self.pacman_view = PacManView(self.maze_view)
        self.score = Score()
        self.lives = config.LIVES
        self.fruit_timer = 0.0  # seconds the fruit stays in the maze; 0 means no fruit
        self.won = False
        self.mode_timer = ModeTimer()  # scatter/chase schedule and frightened time, for all the ghosts
        rng = random.Random()
        self.ghosts = [
            Ghost(self.maze, name, start, dots, personality(self.maze), rng)
            for name, start, dots, personality in zip(
                config.GHOST_NAMES, self.maze.ghost_starts, config.GHOST_RELEASE_DOTS, PERSONALITIES
            )
        ]
        for ghost in self.ghosts:
            ghost.finder = self.finder
        self.ghost_view = GhostView(self.maze_view)
        overlay_was_on = hasattr(self, "overlay") and self.overlay.visible
        self.overlay = Overlay(self.maze_view)
        self.overlay.visible = overlay_was_on  # a new game keeps the player's choice
        self.game_over = False

    def handle_events(self) -> None:
        """Process the window events. Closing the window stops the loop."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.sounds.toggle_mute()
                elif event.key == pygame.K_o:
                    self.overlay.toggle()
                elif event.key in FINDER_KEYS[: len(self.finders)]:
                    self.set_finder(self.finders[FINDER_KEYS.index(event.key)])
                elif not self.started:
                    if event.key in NEW_GAME_KEYS:
                        self.started = True
                elif (self.won or self.game_over) and event.key in NEW_GAME_KEYS:
                    self.new_game()
                elif not (self.won or self.game_over) and event.key in ARROWS:
                    self.pacman.turn(ARROWS[event.key])

    def set_finder(self, finder) -> None:
        """Give every ghost the chosen search algorithm; the paths are searched again at the next tile."""
        self.finder = finder
        for ghost in self.ghosts:
            ghost.finder = finder
            ghost.path = []

    def update(self, dt: float) -> None:
        """Advance the game model by dt seconds."""
        if not self.started or self.won or self.game_over:
            return
        self.pacman.update(dt)
        self.pacman_view.update(self.pacman, dt)
        self.eat()
        if self.fruit_timer > 0:
            self.fruit_timer = max(0.0, self.fruit_timer - dt)
        if not self.maze.dots and not self.maze.energizers:
            self.won = True
            self.sounds.play("win")
            return
        self.update_modes(dt)
        for ghost in self.ghosts:
            ghost.target = self.target_of(ghost)
            ghost.update(dt, self.score.dots_eaten, self.mode_timer.mode)
        self.ghost_view.update(dt)
        self.check_collisions()

    def update_modes(self, dt: float) -> None:
        """Advance the mode timer and apply what it says to the ghosts."""
        was_frightened = self.mode_timer.frightened
        if self.mode_timer.update(dt):
            # Scatter <-> chase: the ghosts outside take the new mode and reverse at once.
            for ghost in self.ghosts:
                if ghost.state in (GhostState.SCATTER, GhostState.CHASE):
                    ghost.set_state(self.mode_timer.mode)
                    ghost.reverse()
        if was_frightened and not self.mode_timer.frightened:
            # The energizer wore off: back to the current mode, this time without reversing.
            for ghost in self.ghosts:
                if ghost.state is GhostState.FRIGHTENED:
                    ghost.set_state(self.mode_timer.mode)

    def frighten_ghosts(self) -> None:
        """Pac-Man ate an energizer: the ghosts that are hunting turn blue and reverse."""
        self.mode_timer.start_fright()  # a second energizer starts the 6 seconds again
        for ghost in self.ghosts:
            if ghost.state in (GhostState.SCATTER, GhostState.CHASE):
                ghost.set_state(GhostState.FRIGHTENED)
                ghost.reverse()

    def target_of(self, ghost: Ghost):
        """Return the tile the ghost is heading to in its current state, or None if it has no target."""
        if ghost.state is GhostState.CHASE:
            # The personality says where to go; the search algorithm finds how.
            wanted = ghost.personality.target(ghost, self.pacman, self.ghosts)
        elif ghost.state is GhostState.SCATTER:
            wanted = ghost.personality.corner
        elif ghost.state is GhostState.EATEN:
            return ghost.home  # inside the house, so it is not moved to a corridor tile
        else:
            return None  # in the house, or frightened (random moves)
        return closest_walkable(self.maze, wanted)

    def check_collisions(self) -> None:
        """A ghost on Pac-Man's tile: Pac-Man eats it if it is frightened, otherwise it catches him."""
        for ghost in self.ghosts:
            if ghost.tile != self.pacman.tile or ghost.state is GhostState.EATEN:
                continue  # the eyes of an eaten ghost are harmless
            if ghost.state is GhostState.FRIGHTENED:
                self.score.eat_ghost()  # 200, 400, 800, 1600 with the same energizer
                ghost.set_state(GhostState.EATEN)
                self.sounds.play("fruit")
            else:
                self.lose_life()
                return

    def lose_life(self) -> None:
        """Pac-Man is caught: -500 points, one life less, everybody back to the start."""
        self.score.caught()
        self.lives -= 1
        if self.lives == 0:
            self.game_over = True
            self.sounds.play("lose")
            return
        self.pacman = PacMan(self.maze, self.maze.pacman_start)  # the dots already eaten stay eaten
        self.mode_timer.reset()
        for ghost in self.ghosts:
            ghost.reset(self.mode_timer.mode)

    def eat(self) -> None:
        """Eat what is on Pac-Man's tile: a dot, an energizer or the fruit."""
        tile = (round(self.pacman.x) % self.maze.width, round(self.pacman.y))
        if tile in self.maze.dots:
            self.maze.dots.remove(tile)
            self.score.eat_dot()
            self.sounds.play("dot")
            if self.score.fruit_due():
                self.fruit_timer = config.FRUIT_SECONDS
        elif tile in self.maze.energizers:
            self.maze.energizers.remove(tile)
            self.score.eat_energizer()
            self.sounds.play("energizer")
            self.frighten_ghosts()
        if self.fruit_timer > 0 and tile == self.maze.fruit:
            self.score.eat_fruit()
            self.sounds.play("fruit")
            self.fruit_timer = 0.0

    def draw(self) -> None:
        """Draw one frame: the start screen, or the maze, fruit, Pac-Man, the ghosts, the panel and maybe the end screen."""
        self.screen.fill(config.BACKGROUND_COLOUR)
        if not self.started:
            self.draw_start_screen()
            pygame.display.flip()
            return
        self.maze_view.draw(self.screen)
        if self.fruit_timer > 0 and self.maze.fruit is not None:
            centre = self.maze_view.tile_centre(self.maze.fruit)
            self.screen.blit(self.fruit_image, self.fruit_image.get_rect(center=centre))
        self.pacman_view.draw(self.screen, self.pacman)
        self.overlay.draw(self.screen, self.ghosts)
        self.ghost_view.draw(self.screen, self.ghosts, self.mode_timer.flashing)
        self.draw_panel()
        if self.won:
            self.draw_end_screen("YOU WIN!")
        elif self.game_over:
            self.draw_end_screen("GAME OVER")
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
        middle = self.finder.name + (" MUTED" if self.sounds.muted else "")
        image = self.font.render(middle, True, config.TEXT_COLOUR)
        self.screen.blit(image, image.get_rect(midtop=((left + right) // 2, y)))

    def draw_start_screen(self) -> None:
        """The title of the game, a big Pac-Man and the keys."""
        centre_x = config.SCREEN_WIDTH // 2
        title = self.big_font.render(config.GAME_TITLE, True, config.TEXT_COLOUR)
        self.screen.blit(title, title.get_rect(center=(centre_x, config.SCREEN_HEIGHT // 3)))
        size = 4 * config.TILE_SIZE
        sprite = pygame.transform.scale(self.pacman_view.frames["right"][1], (size, size))
        self.screen.blit(sprite, sprite.get_rect(center=(centre_x, config.SCREEN_HEIGHT // 2)))
        y = 2 * config.SCREEN_HEIGHT // 3
        for text in ("PRESS ENTER TO START", "ARROWS: MOVE   M: MUTE", "1: DFS   2: BFS   3: A*", "O: GHOST TARGETS"):
            image = self.font.render(text, True, config.TEXT_COLOUR)
            self.screen.blit(image, image.get_rect(midtop=(centre_x, y)))
            y += image.get_height() * 2

    def draw_end_screen(self, title: str) -> None:
        """Darken the maze and show the result, the final score and how to start again."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill(config.WIN_OVERLAY)
        self.screen.blit(overlay, (0, 0))
        lines = [
            (self.big_font, title),
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
