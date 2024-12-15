"""Game configuration and constants"""

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
TARGET_FPS = 144  # Target frame rate

# Colors
WATER_COLOR = (65, 95, 115)
UI_COLOR = (30, 30, 30)
TEXT_COLOR = (255, 255, 255)

# Map settings
INITIAL_ZOOM = 1.0
MAX_ZOOM = 50.0
MIN_ZOOM = 0.3
ZOOM_SPEED = 1.1

# Movement settings
PAN_SPEED = 20
DRAG_BUTTON = 1  # Left mouse button
SELECT_BUTTON = 3  # Right mouse button

# Performance settings
MAX_POLYGON_CACHE_SIZE = 1000  # Maximum number of cached polygon surfaces
CACHE_CLEANUP_THRESHOLD = 800  # Clean cache when it exceeds this size
VIEWPORT_MARGIN = 1.0  # Degrees to expand viewport for smoother panning
SIMPLIFICATION_LEVELS = {  # Simplification tolerances for different zoom ranges
    0.3: 5.0,   # Far zoom: high simplification
    0.5: 2.0,
    1.0: 1.0,
    2.0: 0.5,
    4.0: 0.1    # Close zoom: low simplification
}

# City display settings
CITY_CACHE_SIZE = 1024  # Size of LRU cache for city calculations
MIN_CITY_POPULATION = 50000  # Minimum population for a city to be shown
CITY_ZOOM_THRESHOLDS = {  # Population thresholds for different zoom levels
    0.3: 2000000,  # Show only major cities when zoomed out
    0.5: 1000000,
    1.0: 500000,
    2.0: 200000,
    4.0: 50000     # Show all cities when zoomed in
}

# Debug settings
SHOW_FPS = True  # Whether to show FPS counter
SHOW_DEBUG_INFO = False  # Whether to show additional debug information
