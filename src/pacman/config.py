"""All constants of the game, defined once (see Table 8 of the project description)."""

from pathlib import Path

# --- Window ---
SCREEN_WIDTH = 784  # the maze (504 px) on the left, the control panel (280 px) on the right
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Pac-Man AI"

# --- Layout ---
TILE_SIZE = 18  # pixels per tile: a 28 x 36 map is 504 x 648 px
HUD_HEIGHT = 72  # score and lives under the maze: 648 + 72 = 720 px
PANEL_WIDTH = 280  # control panel to the right of the maze

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

# --- Ghost states (section 3.5, Tables 6 and 8) ---
# Scatter and chase alternate on this schedule, as (mode, seconds). After the last entry: chase for ever.
MODE_SCHEDULE = (
    ("scatter", 7.0),
    ("chase", 20.0),
    ("scatter", 7.0),
    ("chase", 20.0),
    ("scatter", 5.0),
    ("chase", 20.0),
    ("scatter", 5.0),
)
FRIGHTENED_SECONDS = 6.0  # how long an energizer works
FLASH_SECONDS = 2.0  # the ghosts flash in the last seconds of the frightened time
FRIGHTENED_SPEED = 0.5  # a frightened ghost moves at this fraction of GHOST_SPEED
FLASH_FPS = 6  # colour changes per second while flashing
FLASH_BRIGHTEN = (170, 170, 170)  # added to the scared sprite's colours to get the flash sprite

# --- Ghost personalities (Table 8) ---
PINKY_AHEAD = 4  # Pinky hunts this many tiles in front of Pac-Man
INKY_AHEAD = 2  # Inky's pivot is this many tiles in front of Pac-Man
CLYDE_RADIUS = 8  # Clyde goes to his corner when he is closer than this to Pac-Man (in tiles)

# --- Overlay (shows where the ghosts are heading) ---
GHOST_COLOURS = {  # the colours of the sprites, used to draw each ghost's target
    "blinky": (255, 40, 40),
    "pinky": (255, 120, 255),
    "inky": (60, 220, 60),
    "clyde": (255, 170, 40),
}
OVERLAY_WIDTH = 2  # line thickness in pixels

# --- Control panel ---
PANEL_FONT_SIZE = 8
PANEL_MARGIN = 12  # space around the panel and between its buttons, in pixels
PANEL_LINE_GAP = 6  # extra space between two lines of text
BUTTON_HEIGHT = 28
BUTTON_SELECTED_COLOUR = (255, 221, 0)  # background of the selected search algorithm
