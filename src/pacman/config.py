"""All constants of the game, defined once (see Table 8 of the project description)."""

from pathlib import Path

# --- Window ---
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Pac-Man AI"

# --- Layout ---
TILE_SIZE = 18  # pixels per tile: a 28 x 36 map is 504 x 648 px
HUD_HEIGHT = 72  # control panel under the maze: 648 + 72 = 720 px

# --- Files ---
# This file is src/pacman/config.py, so parents[2] is the repository root.
ROOT_DIR = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT_DIR / "maps" / "classic.txt"

# --- Map file format: one character per tile ---
WALL = "#"
DOT = "."
ENERGIZER = "o"
EMPTY = " "
DOOR = "-"
HOUSE = "H"
PACMAN_START = "P"
GHOST_STARTS = "0123"  # Blinky, Pinky, Inky, Clyde
FRUIT = "F"

# --- Map requirements ---
MIN_DOTS = 170
ENERGIZER_COUNT = 4

# --- Agents (who asks Maze.is_walkable) ---
PACMAN = "pacman"
GHOST = "ghost"

# --- Directions as (dx, dy) in tiles; x grows to the right, y grows downwards ---
UP = (0, -1)
LEFT = (-1, 0)
DOWN = (0, 1)
RIGHT = (1, 0)
NEIGHBOUR_ORDER = (UP, LEFT, DOWN, RIGHT)

# --- Drawing (sizes in pixels, colours as (R, G, B)) ---
DOT_RADIUS = 2
ENERGIZER_RADIUS = 6
DOOR_THICKNESS = 4
BACKGROUND_COLOUR = (0, 0, 0)
WALL_COLOUR = (33, 33, 222)
DOOR_COLOUR = (255, 184, 222)
DOT_COLOUR = (255, 184, 151)

# --- Movement ---
PACMAN_SPEED = 7.6  # tiles per second, as in the original game

# --- Score and lives (Table 7) ---
DOT_POINTS = 10
ENERGIZER_POINTS = 50
GHOST_POINTS = (200, 400, 800, 1600)  # 1st, 2nd, 3rd, 4th ghost eaten with one energizer
FRUIT_POINTS = 100
CAUGHT_POINTS = -500
FRUIT_AFTER_DOTS = (70, 170)  # the fruit appears after this many dots have been eaten
FRUIT_SECONDS = 9.0  # how long the fruit stays in the maze
LIVES = 3

# --- Assets and text ---
ASSETS_DIR = ROOT_DIR / "assets"
FONT_PATH = ASSETS_DIR / "fonts" / "PressStart2P-Regular.ttf"
FRUIT_SPRITE = ASSETS_DIR / "sprites" / "fruit.png"
FONT_SIZE = 16
TEXT_COLOUR = (255, 255, 255)
WIN_OVERLAY = (0, 0, 0, 200)  # black, mostly opaque, drawn over the maze when the game is won

# --- Sprites ---
SPRITES_DIR = ASSETS_DIR / "sprites"
PACMAN_FRAMES = 4  # pacman_<direction>_0.png ... _3.png
PACMAN_ANIMATION_FPS = 12  # mouth frames per second

# --- Start screen and sound ---
GAME_TITLE = "PAC-MAN AI"  # shown on the start screen: put the name of your theme here
SOUNDS_DIR = ASSETS_DIR / "sounds"
SOUND_NAMES = ("dot", "energizer", "fruit", "win", "lose")

# --- Ghosts ---
GHOST_SPEED = 7.1  # tiles per second
GHOST_NAMES = ("blinky", "pinky", "inky", "clyde")
GHOST_RELEASE_DOTS = (0, 0, 30, 60)  # Blinky starts outside; Pinky, Inky, Clyde leave after 0, 30, 60 dots
GHOST_SPRITES = {"blinky": "red", "pinky": "pink", "inky": "green", "clyde": "orange"}
