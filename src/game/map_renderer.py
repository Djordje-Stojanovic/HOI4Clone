import pygame
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

class MapRenderer:
    def __init__(self, width, height):
        # Colors
        self.WATER = (65, 105, 225)      # Royal blue for water
        self.LAND = (150, 200, 150)      # Light green for land
        self.BORDER = (60, 60, 60)       # Darker gray for borders
        self.HIGHLIGHT = (255, 255, 200)  # Light yellow for selection
        
        # Initialize surfaces
        self.width = width
        self.height = height
        self.map_surface = pygame.Surface((width, height))

    def draw_countries(self, countries_gdf, selected_country, transform_coords):
        """Draw all countries"""
        self.map_surface.fill(self.WATER)
        
        # Draw all countries
        for idx, country in countries_gdf.iterrows():
            geom = country.geometry
            if isinstance(geom, (Polygon, MultiPolygon)):
                if isinstance(geom, Polygon):
                    polygons = [geom]
                else:
                    polygons = list(geom.geoms)
                
                for polygon in polygons:
                    coords = list(polygon.exterior.coords)
                    screen_coords = transform_coords(coords)
                    
                    if len(screen_coords) > 2:
                        # Draw country fill
                        color = self.HIGHLIGHT if country['NAME'] == selected_country else self.LAND
                        try:
                            pygame.draw.polygon(self.map_surface, color, screen_coords)
                            pygame.draw.polygon(self.map_surface, self.BORDER, screen_coords, 2)
                        except (ValueError, pygame.error) as e:
                            print(f"Error drawing {country['NAME']}: {e}")
                            continue
        
        return self.map_surface
