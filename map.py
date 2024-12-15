"""Map rendering and coordinate handling"""
import pygame
from typing import Tuple, List
from config import *
from country import Country, CountryManager

class MapRenderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.offset_x = WINDOW_WIDTH // 2
        self.offset_y = WINDOW_HEIGHT // 2
        self.zoom = INITIAL_ZOOM

    def get_viewport_bounds(self) -> Tuple[float, float, float, float]:
        """Calculate geographic bounds of current viewport"""
        # Convert screen corners to geographic coordinates
        top_left_lon, top_left_lat = self.screen_to_geo(0, 0)
        bottom_right_lon, bottom_right_lat = self.screen_to_geo(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Return bounds as (min_lon, min_lat, max_lon, max_lat)
        return (
            min(top_left_lon, bottom_right_lon),
            min(bottom_right_lat, top_left_lat),
            max(top_left_lon, bottom_right_lon),
            max(bottom_right_lat, top_left_lat)
        )

    def is_country_visible(self, country: Country) -> bool:
        """Check if country intersects current viewport"""
        view_min_lon, view_min_lat, view_max_lon, view_max_lat = self.get_viewport_bounds()
        
        # Quick bounding box intersection test
        return not (
            country.max_lon < view_min_lon or
            country.min_lon > view_max_lon or
            country.max_lat < view_min_lat or
            country.min_lat > view_max_lat
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
        # Skip if country is not visible
        if not self.is_country_visible(country):
            return
            
        color = country.get_color()
        
        for polygon in country.polygons:
            points = []
            for lon, lat in polygon:
                x, y = self.geo_to_screen(lon, lat)
                points.append((x, y))
            
            if len(points) >= 3:
                pygame.draw.polygon(self.screen, color, points)
                pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)

    def draw(self, country_manager: CountryManager):
        """Draw the map"""
        self.screen.fill(WATER_COLOR)
        
        # Draw only visible countries
        for country in country_manager.countries.values():
            if self.is_country_visible(country):
                self.draw_country(country)
        
        # Draw selected country name
        if country_manager.selected_country:
            name = country_manager.selected_country.name
            font = pygame.font.Font(None, 36)
            text = font.render(name, True, TEXT_COLOR)
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

    def pan(self, dx: int, dy: int):
        """Pan the map by the given amount"""
        self.offset_x += dx
        self.offset_y += dy
