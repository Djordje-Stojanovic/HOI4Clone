"""Map rendering and coordinate handling"""
import pygame
from typing import Tuple, List, Dict
from hoi4clone.utils.config import *
from hoi4clone.core.country import Country, CountryManager
from hoi4clone.core.city import City, CityManager
import numpy as np

class MapRenderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.offset_x = WINDOW_WIDTH // 2
        self.offset_y = WINDOW_HEIGHT // 2
        self.zoom = INITIAL_ZOOM
        
        # Font setup
        self.font = pygame.font.Font(None, 24)
        
        # Create water background
        self.water_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.water_surface.fill(WATER_COLOR)
        
        # Create main map surface
        self.map_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.map_surface.fill(WATER_COLOR)
        
        # Store country geometries
        self.country_geometries: Dict[str, List[List[Tuple[float, float]]]] = {}

    def geo_to_screen(self, lon: float, lat: float) -> Tuple[int, int]:
        """Convert geographic coordinates to screen coordinates"""
        x = (lon + 180) / 360 * WINDOW_WIDTH * self.zoom
        y = (-lat + 90) / 180 * WINDOW_HEIGHT * self.zoom
        return (int(x + self.offset_x), int(y + self.offset_y))

    def screen_to_geo(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to geographic coordinates"""
        x = screen_x - self.offset_x
        y = screen_y - self.offset_y
        
        x = x / (WINDOW_WIDTH * self.zoom)
        y = y / (WINDOW_HEIGHT * self.zoom)
        
        lon = x * 360 - 180
        lat = -(y * 180 - 90)
        return lon, lat

    def draw_country(self, country: Country):
        """Draw a single country"""
        # Get visible bounds
        min_lon, max_lat = self.screen_to_geo(0, 0)
        max_lon, min_lat = self.screen_to_geo(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Get polygons at appropriate detail level
        polygons = country.get_polygons(self.zoom)
        
        # Draw polygons
        for polygon in polygons:
            points = []
            # Convert coordinates in batch
            coords = np.array(polygon)
            screen_coords = np.column_stack([
                (coords[:, 0] + 180) / 360 * WINDOW_WIDTH * self.zoom + self.offset_x,
                (-coords[:, 1] + 90) / 180 * WINDOW_HEIGHT * self.zoom + self.offset_y
            ]).astype(np.int32)
            
            if len(screen_coords) >= 3:
                pygame.draw.polygon(self.screen, country.get_color(), screen_coords)
                if self.zoom >= 1.0:
                    pygame.draw.polygon(self.screen, (0, 0, 0), screen_coords, 1)

    def draw_city(self, city: City):
        """Draw a single city"""
        x, y = self.geo_to_screen(city.lon, city.lat)
        
        # Draw city marker
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 4)
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 1)
        
        # Draw city name
        text = self.font.render(city.name, True, (0, 0, 0))
        text_rect = text.get_rect(midleft=(x + 6, y))
        
        # Add white background
        bg_rect = text_rect.inflate(8, 4)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, 1)
        self.screen.blit(text, text_rect)

    def draw(self, country_manager: CountryManager, city_manager: CityManager):
        """Draw the map"""
        # Draw water background
        self.screen.blit(self.water_surface, (0, 0))
        
        # Get visible bounds
        min_lon, max_lat = self.screen_to_geo(0, 0)
        max_lon, min_lat = self.screen_to_geo(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Draw countries
        for country in country_manager.countries.values():
            if (country.max_lon >= min_lon and country.min_lon <= max_lon and
                country.max_lat >= min_lat and country.min_lat <= max_lat):
                self.draw_country(country)
        
        # Draw cities
        visible_cities = city_manager.get_visible_cities(
            min_lon, max_lon, min_lat, max_lat, self.zoom
        )
        for city in visible_cities:
            self.draw_city(city)
        
        # Draw zoom level
        zoom_text = f"Zoom: {self.zoom:.1f}x"
        text = self.font.render(zoom_text, True, (0, 0, 0))
        text_rect = text.get_rect(topright=(WINDOW_WIDTH - 10, 10))
        bg_rect = text_rect.inflate(8, 4)
        bg_rect.topright = (WINDOW_WIDTH - 8, 8)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, 1)
        self.screen.blit(text, text_rect)
        
        # Draw selected country name
        if country_manager.selected_country:
            text = self.font.render(country_manager.selected_country.name, True, (0, 0, 0))
            text_rect = text.get_rect(topleft=(10, 10))
            bg_rect = text_rect.inflate(8, 4)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, 1)
            self.screen.blit(text, text_rect)

    def adjust_zoom(self, factor: float, mouse_x: int, mouse_y: int):
        """Adjust zoom level while maintaining mouse position"""
        old_lon, old_lat = self.screen_to_geo(mouse_x, mouse_y)
        
        old_zoom = self.zoom
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * factor))
        
        if self.zoom != old_zoom:
            new_x, new_y = self.geo_to_screen(old_lon, old_lat)
            self.offset_x += mouse_x - new_x
            self.offset_y += mouse_y - new_y

    def pan(self, dx: int, dy: int):
        """Pan the map by the given amount"""
        self.offset_x += dx
        self.offset_y += dy
