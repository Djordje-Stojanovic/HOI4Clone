class GameState:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.selected_country = None
        self.x_offset = 0
        self.y_offset = 0
        self.zoom = 1.0
        
        # Map state
        self.bounds = None
        self.scale = None
        
    def transform_coords(self, coords):
        """Transform geographic coordinates to screen coordinates"""
        if self.bounds is None or self.scale is None:
            return []
            
        screen_coords = []
        for x, y in coords:
            # Transform from geographic to screen coordinates
            screen_x = (x - self.bounds[0]) * self.scale * self.zoom + self.x_offset
            screen_y = self.height - ((y - self.bounds[1]) * self.scale * self.zoom + self.y_offset)
            
            # Only add if within reasonable bounds to prevent overflow
            if -10000 < screen_x < 10000 and -10000 < screen_y < 10000:
                screen_coords.append((int(screen_x), int(screen_y)))
            
        return screen_coords
    
    def screen_to_geo(self, screen_x, screen_y):
        """Convert screen coordinates back to geographic coordinates"""
        if self.bounds is None or self.scale is None:
            return 0, 0
            
        x = (screen_x - self.x_offset) / (self.scale * self.zoom) + self.bounds[0]
        y = (self.height - screen_y - self.y_offset) / (self.scale * self.zoom) + self.bounds[1]
        return x, y
    
    def update(self, selected_country=None, offset_x=None, offset_y=None, zoom=None):
        """Update game state"""
        if selected_country is not None:
            self.selected_country = selected_country
        if offset_x is not None:
            self.x_offset = offset_x
        if offset_y is not None:
            self.y_offset = offset_y
        if zoom is not None:
            self.zoom = zoom
            
    def set_map_bounds(self, bounds, scale):
        """Set map boundaries and scale"""
        self.bounds = bounds
        self.scale = scale
        
        # Print debug info
        print(f"Bounds: {bounds}")
        print(f"Scale: {scale}")
