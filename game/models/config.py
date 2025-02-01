import os
from pathlib import Path

# Basic game settings
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
TILE_SIZE = 100
GRAVITY = 10
WIN_CNT = 4
M = 6  # Number of rows
N = 7  # Number of columns
INFO_HEIGHT = 30
INFO_SIDE_OFFSET = 10
FRAMES_PER_SEC = 120
INFO_FONT = None

# Define colors (use RGB tuples)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (192, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 128, 0)
YELLOW = (255, 255, 0)

# Paths relative to Django settings base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust as needed to match your folder structure

ACTIONS_FOLDER = os.path.join(BASE_DIR, 'game', 'actions')
IMG_FOLDER = os.path.join(BASE_DIR, 'game', 'static', 'images')

# Ensure folders exist (optional, useful for development)
os.makedirs(ACTIONS_FOLDER, exist_ok=True)
os.makedirs(IMG_FOLDER, exist_ok=True)

