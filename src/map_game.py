import pygame
import numpy as np
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import transform
import pyproj
from functools import partial

class EuropaMap:
    def __init__(self, width=1024, height=768):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Europa Map")
        
        # Colors
        self.WATER = (65, 105, 225)      # Royal blue for water
        self.LAND_COLORS = {
            'plains': (150, 200, 150),    # Light green
            'mountains': (139, 137, 137),  # Gray
            'forest': (34, 139, 34),      # Forest green
            'urban': (169, 169, 169),     # Dark gray
            'desert': (238, 232, 170),    # Khaki
        }
        self.BORDER = (60, 60, 60)       # Darker gray for borders
        self.HIGHLIGHT = (255, 255, 200)  # Light yellow for selection
        self.TEXT_COLOR = (255, 255, 255) # White for text
        
        # Initialize surfaces
        self.map_surface = pygame.Surface((width, height))
        self.terrain_surface = pygame.Surface((width, height))
        self.ui_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Load and process map data
        self.load_map_data()
        
        # Camera/view parameters
        self.zoom = 1.0
        self.offset_x = -width/4  # Center on Europe
        self.offset_y = -height/4
        
        # State
        self.selected_country = None
        self.show_terrain = True
        self.show_provinces = True
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize terrain pattern
        self.create_terrain_patterns()

    def create_terrain_patterns(self):
        """Create terrain patterns for different types"""
        self.terrain_patterns = {}
        
        # Mountains pattern (diagonal lines)
        mountains = pygame.Surface((4, 4))
        mountains.fill(self.LAND_COLORS['mountains'])
        pygame.draw.line(mountains, (100, 100, 100), (0, 0), (3, 3))
        self.terrain_patterns['mountains'] = mountains
        
        # Forest pattern (dots)
        forest = pygame.Surface((4, 4))
        forest.fill(self.LAND_COLORS['forest'])
        pygame.draw.circle(forest, (0, 100, 0), (2, 2), 1)
        self.terrain_patterns['forest'] = forest

    def load_map_data(self):
        """Load and process Natural Earth data"""
        # Load country boundaries
        countries_path = Path("src/data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
        self.countries_gdf = gpd.read_file(countries_path)
        
        # Load provinces
        provinces_path = Path("src/data/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp")
        self.provinces_gdf = gpd.read_file(provinces_path)
        
        # Filter to European countries and Russia
        european_countries = [
            'France', 'Germany', 'United Kingdom', 'Italy', 'Spain', 'Poland',
            'Romania', 'Ukraine', 'Russia', 'Greece', 'Bulgaria', 'Hungary',
            'Portugal', 'Austria', 'Czech Republic', 'Serbia', 'Ireland',
            'Lithuania', 'Latvia', 'Croatia', 'Slovakia', 'Estonia', 'Denmark',
            'Netherlands', 'Switzerland', 'Finland', 'Norway', 'Sweden', 'Belgium',
            'Albania', 'Moldova', 'Belarus', 'Slovenia', 'North Macedonia',
            'Montenegro', 'Luxembourg', 'Iceland'
        ]
        self.countries_gdf = self.countries_gdf[self.countries_gdf['NAME'].isin(european_countries)]
        
        # Project to Web Mercator for better display
        self.countries_gdf = self.countries_gdf.to_crs(epsg=3857)
        self.provinces_gdf = self.provinces_gdf.to_crs(epsg=3857)
        
        # Normalize coordinates to fit screen
        bounds = self.countries_gdf.total_bounds
        self.x_scale = self.width / (bounds[2] - bounds[0])
        self.y_scale = self.height / (bounds[3] - bounds[1])
        self.scale = min(self.x_scale, self.y_scale) * 0.9  # 90% of full scale
        
        self.x_offset = bounds[0]
        self.y_offset = bounds[1]
        
        # Assign random terrain types for demonstration
        terrain_types = ['plains', 'mountains', 'forest', 'urban', 'desert']
        self.countries_gdf['terrain'] = np.random.choice(terrain_types, size=len(self.countries_gdf))

    def transform_coords(self, coords):
        """Transform geographic coordinates to screen coordinates"""
        screen_coords = []
        for x, y in coords:
            screen_x = (x - self.x_offset) * self.scale * self.zoom + self.offset_x
            screen_y = self.height - ((y - self.y_offset) * self.scale * self.zoom + self.offset_y)
            screen_coords.append((int(screen_x), int(screen_y)))
        return screen_coords

    def screen_to_geo(self, screen_x, screen_y):
        """Convert screen coordinates back to geographic coordinates"""
        x = (screen_x - self.offset_x) / (self.scale * self.zoom) + self.x_offset
        y = (self.height - screen_y - self.offset_y) / (self.scale * self.zoom) + self.y_offset
        return x, y

    def draw_terrain_pattern(self, surface, pattern, coords):
        """Draw terrain pattern within polygon"""
        # Get bounding box of polygon
        xs = [x for x, y in coords]
        ys = [y for x, y in coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Create pattern surface
        pattern_surface = pygame.Surface((max_x - min_x, max_y - min_y))
        pattern_surface.fill((0, 0, 0))
        
        # Draw base polygon
        adjusted_coords = [(x - min_x, y - min_y) for x, y in coords]
        pygame.draw.polygon(pattern_surface, (255, 255, 255), adjusted_coords)
        
        # Apply pattern
        for x in range(0, max_x - min_x, pattern.get_width()):
            for y in range(0, max_y - min_y, pattern.get_height()):
                pattern_surface.blit(pattern, (x, y))
        
        # Draw to main surface
        surface.blit(pattern_surface, (min_x, min_y))

    def draw_countries(self):
        """Draw all countries on the map surface"""
        self.map_surface.fill(self.WATER)
        self.terrain_surface.fill((0, 0, 0, 0))
        
        # Draw provinces first if enabled
        if self.show_provinces:
            for idx, province in self.provinces_gdf.iterrows():
                if isinstance(province.geometry, (Polygon, MultiPolygon)):
                    if isinstance(province.geometry, Polygon):
                        polygons = [province.geometry]
                    else:
                        polygons = list(province.geometry.geoms)
                    
                    for polygon in polygons:
                        coords = list(polygon.exterior.coords)
                        screen_coords = self.transform_coords(coords)
                        if len(screen_coords) > 2:
                            pygame.draw.polygon(self.map_surface, (100, 100, 100), screen_coords, 1)
        
        # Draw countries
        for idx, country in self.countries_gdf.iterrows():
            geom = country.geometry
            if isinstance(geom, (Polygon, MultiPolygon)):
                if isinstance(geom, Polygon):
                    polygons = [geom]
                else:
                    polygons = list(geom.geoms)
                
                for polygon in polygons:
                    coords = list(polygon.exterior.coords)
                    screen_coords = self.transform_coords(coords)
                    
                    if len(screen_coords) > 2:
                        # Draw country fill
                        color = self.HIGHLIGHT if country['NAME'] == self.selected_country else self.LAND_COLORS['plains']
                        pygame.draw.polygon(self.map_surface, color, screen_coords)
                        
                        # Draw terrain if enabled
                        if self.show_terrain and country['terrain'] in self.terrain_patterns:
                            self.draw_terrain_pattern(self.terrain_surface, 
                                                    self.terrain_patterns[country['terrain']], 
                                                    screen_coords)
                        
                        # Draw border
                        pygame.draw.polygon(self.map_surface, self.BORDER, screen_coords, 2)

    def draw_ui(self):
        """Draw UI elements"""
        self.ui_surface.fill((0, 0, 0, 0))
        
        # Draw selected country info
        if self.selected_country:
            country_data = self.countries_gdf[self.countries_gdf['NAME'] == self.selected_country].iloc[0]
            
            # Create info box
            box_height = 100
            box_width = 300
            box_surface = pygame.Surface((box_width, box_height))
            box_surface.fill((0, 0, 0))
            box_surface.set_alpha(180)
            
            # Draw country name
            text = self.font.render(self.selected_country, True, self.TEXT_COLOR)
            box_surface.blit(text, (10, 10))
            
            # Draw terrain type
            terrain_text = self.small_font.render(f"Terrain: {country_data['terrain']}", True, self.TEXT_COLOR)
            box_surface.blit(terrain_text, (10, 50))
            
            self.ui_surface.blit(box_surface, (10, 10))

    def handle_input(self):
        """Handle keyboard and mouse input"""
        keys = pygame.key.get_pressed()
        
        # Pan with arrow keys
        pan_speed = 10
        if keys[pygame.K_LEFT]:
            self.offset_x += pan_speed
        if keys[pygame.K_RIGHT]:
            self.offset_x -= pan_speed
        if keys[pygame.K_UP]:
            self.offset_y += pan_speed
        if keys[pygame.K_DOWN]:
            self.offset_y -= pan_speed
            
        # Zoom with + and -
        if keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS]:
            self.zoom *= 1.02
        if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
            self.zoom /= 1.02
            
        # Toggle terrain with T
        if keys[pygame.K_t]:
            self.show_terrain = not self.show_terrain
            
        # Toggle provinces with P
        if keys[pygame.K_p]:
            self.show_provinces = not self.show_provinces

        # Mouse input
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        if mouse_pressed[0]:  # Left click
            # Convert screen coordinates to geographic coordinates
            geo_x, geo_y = self.screen_to_geo(*mouse_pos)
            point = Point(geo_x, geo_y)
            
            # Find clicked country
            for idx, country in self.countries_gdf.iterrows():
                if country.geometry.contains(point):
                    self.selected_country = country['NAME']
                    print(f"Selected: {self.selected_country}")
                    return

    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Handle input
            self.handle_input()
            
            # Draw
            self.draw_countries()
            
            # Compose final frame
            self.screen.blit(self.map_surface, (0, 0))
            if self.show_terrain:
                self.screen.blit(self.terrain_surface, (0, 0))
            
            # Draw UI
            self.draw_ui()
            self.screen.blit(self.ui_surface, (0, 0))
            
            pygame.display.flip()
            
            # Cap at 60 FPS
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = EuropaMap()
    game.run()
