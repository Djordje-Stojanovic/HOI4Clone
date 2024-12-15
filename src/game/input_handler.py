import pygame
from shapely.geometry import Point

class InputHandler:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0
        self.pan_speed = 10
        self.zoom_speed = 1.1  # Increased for more noticeable zoom
        self.min_zoom = 0.5
        self.max_zoom = 5.0
        
        # Mouse drag handling
        self.dragging = False
        self.last_mouse_pos = None

    def handle_input(self, countries_gdf, screen_to_geo, events):
        """Handle keyboard and mouse input"""
        keys = pygame.key.get_pressed()
        selected_country = None
        
        # Pan with arrow keys (fixed directions)
        if keys[pygame.K_LEFT]:
            self.offset_x += self.pan_speed  # Move view left
        if keys[pygame.K_RIGHT]:
            self.offset_x -= self.pan_speed  # Move view right
        if keys[pygame.K_UP]:
            self.offset_y += self.pan_speed  # Move view up
        if keys[pygame.K_DOWN]:
            self.offset_y -= self.pan_speed  # Move view down
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            # Handle mouse wheel zoom
            if event.type == pygame.MOUSEWHEEL:
                # Get mouse position before zoom
                old_geo_x, old_geo_y = screen_to_geo(*mouse_pos)
                old_zoom = self.zoom
                
                # Apply zoom
                if event.y > 0:  # Scroll up
                    self.zoom = min(self.zoom * self.zoom_speed, self.max_zoom)
                else:  # Scroll down
                    self.zoom = max(self.zoom / self.zoom_speed, self.min_zoom)
                
                # Adjust offset to keep mouse position fixed
                zoom_factor = self.zoom / old_zoom
                self.offset_x = mouse_pos[0] - (mouse_pos[0] - self.offset_x) * zoom_factor
                self.offset_y = mouse_pos[1] - (mouse_pos[1] - self.offset_y) * zoom_factor
            
            # Handle mouse drag
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.dragging = True
                    self.last_mouse_pos = mouse_pos
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    if self.dragging and self.last_mouse_pos == mouse_pos:
                        # Click without drag - select country
                        geo_x, geo_y = screen_to_geo(*mouse_pos)
                        point = Point(geo_x, geo_y)
                        
                        for idx, country in countries_gdf.iterrows():
                            if country.geometry.contains(point):
                                selected_country = country['NAME']
                                print(f"Selected: {selected_country}")
                                break
                    
                    self.dragging = False
                    self.last_mouse_pos = None
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.last_mouse_pos:
                    # Calculate drag distance
                    dx = mouse_pos[0] - self.last_mouse_pos[0]
                    dy = mouse_pos[1] - self.last_mouse_pos[1]
                    
                    # Update offset based on drag (not inverted)
                    self.offset_x += dx
                    self.offset_y += dy
                    
                    self.last_mouse_pos = mouse_pos

        return selected_country, self.offset_x, self.offset_y, self.zoom
