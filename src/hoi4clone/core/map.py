"""Map rendering and coordinate handling"""
import pygame
from typing import Tuple, List
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
        self._setup_viewport()
        # Fonts for different purposes
        self.city_font = pygame.font.Font(None, 28)
        self.ui_font = pygame.font.Font(None, 32)  # Increased font size

    def _setup_viewport(self):
        """Initialize viewport tracking"""
        self.viewport_min_lon = -180
        self.viewport_max_lon = 180
        self.viewport_min_lat = -90
        self.viewport_max_lat = 90
        self.update_viewport()

    def update_viewport(self):
        """Update viewport boundaries based on current view"""
        # Convert screen corners to geographic coordinates
        self.viewport_min_lon, self.viewport_max_lat = self.screen_to_geo(0, 0)
        self.viewport_max_lon, self.viewport_min_lat = self.screen_to_geo(WINDOW_WIDTH, WINDOW_HEIGHT)

    def is_in_viewport(self, country: Country) -> bool:
        """Check if country intersects current viewport"""
        return not (
            country.max_lon < self.viewport_min_lon or
            country.min_lon > self.viewport_max_lon or
            country.max_lat < self.viewport_min_lat or
            country.min_lat > self.viewport_max_lat
        )

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
        if not self.is_in_viewport(country):
            return

        color = country.get_color()
        
        # Get appropriate detail level based on zoom
        polygons = country.get_polygons(self.zoom)
        
        for polygon in polygons:
            points = []
            # Convert geographic coordinates to screen coordinates
            for coord in polygon:
                x, y = self.geo_to_screen(coord[0], coord[1])
                points.append((x, y))
            
            if len(points) >= 3:
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)

    def draw_city(self, city: City):
        """Draw a single city"""
        x, y = self.geo_to_screen(city.lon, city.lat)
        
        # Draw city marker
        size = city.get_size(self.zoom)
        # Larger black border
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), size + 2)
        # White fill
        pygame.draw.circle(self.screen, (255, 255, 255), (x, y), size)
        # Small black center dot
        pygame.draw.circle(self.screen, (0, 0, 0), (x, y), max(1, size // 3))
        
        # Draw city name if zoomed in enough
        if self.zoom >= 1.0 or city.population > 2000000:
            text = self.city_font.render(city.name, True, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.midleft = (x + size + 4, y)
            
            # Add background for better readability
            padding = 4
            background_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(self.screen, (255, 255, 255), background_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), background_rect, 1)
            
            self.screen.blit(text, text_rect)

    def draw_ui(self):
        """Draw UI elements"""
        # Draw zoom level with black text
        zoom_text = f"Zoom: {self.zoom:.1f}x"
        text = self.ui_font.render(zoom_text, True, (0, 0, 0))  # Black text
        text_rect = text.get_rect()
        text_rect.topright = (WINDOW_WIDTH - 10, 10)
        
        # Add white background with black border
        padding = 6  # Increased padding
        background_rect = text_rect.inflate(padding * 2, padding * 2)
        background_rect.topright = (WINDOW_WIDTH - 8, 8)
        pygame.draw.rect(self.screen, (255, 255, 255), background_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), background_rect, 1)
        
        self.screen.blit(text, text_rect)

    def draw(self, country_manager: CountryManager, city_manager: CityManager):
        """Draw the map"""
        self.screen.fill(WATER_COLOR)
        self.update_viewport()
        
        # Draw all visible countries
        for country in country_manager.countries.values():
            if self.is_in_viewport(country):
                self.draw_country(country)
        
        # Draw visible cities
        visible_cities = city_manager.get_visible_cities(
            self.viewport_min_lon, self.viewport_max_lon,
            self.viewport_min_lat, self.viewport_max_lat,
            self.zoom
        )
        for city in visible_cities:
            self.draw_city(city)
        
        # Draw UI elements
        self.draw_ui()
        
        # Draw selected country name
        if country_manager.selected_country:
            name = country_manager.selected_country.name
            text = self.ui_font.render(name, True, TEXT_COLOR)
            self.screen.blit(text, (10, 10))

    def adjust_zoom(self, factor: float, mouse_x: int, mouse_y: int):
        """Adjust zoom level while maintaining mouse position"""
        old_lon, old_lat = self.screen_to_geo(mouse_x, mouse_y)
        
        old_zoom = self.zoom
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * factor))
        
        if self.zoom != old_zoom:
            new_x, new_y = self.geo_to_screen(old_lon, old_lat)
            self.offset_x += mouse_x - new_x
            self.offset_y += mouse_y - new_y
            self.update_viewport()

    def pan(self, dx: int, dy: int):
        """Pan the map by the given amount"""
        self.offset_x += dx
        self.offset_y += dy
        self.update_viewport()
