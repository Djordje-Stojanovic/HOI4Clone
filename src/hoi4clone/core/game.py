"""Main game loop and input handling"""
import pygame
import os
from hoi4clone.utils.config import *
from hoi4clone.core.map import MapRenderer
from hoi4clone.core.country import CountryManager
from hoi4clone.core.city import CityManager

class Game:
    def __init__(self, screen: pygame.Surface, country_manager: CountryManager):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.country_manager = country_manager
        self.city_manager = CityManager()
        self.map_renderer = MapRenderer(self.screen)
        
        # Load city data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.city_manager.load_from_shapefile(
            os.path.join(data_dir, "ne_10m_populated_places", "ne_10m_populated_places.shp"),
            os.path.join(data_dir, "ne_10m_admin_0_countries", "ne_10m_admin_0_countries.shp")
        )
        
        # Input state
        self.dragging = False
        self.last_mouse_pos = None
        
        # Performance monitoring
        self.frame_count = 0
        self.last_time = pygame.time.get_ticks()
        self.fps = 0

    def handle_input(self) -> bool:
        """Handle user input. Returns False if the game should exit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                
                if event.button == DRAG_BUTTON:  # Left click for dragging
                    self.dragging = True
                    self.last_mouse_pos = (mouse_x, mouse_y)
                
                elif event.button == SELECT_BUTTON:  # Right click for selection
                    lon, lat = self.map_renderer.screen_to_geo(mouse_x, mouse_y)
                    clicked_country = self.country_manager.get_country_at_point(lon, lat)
                    self.country_manager.select_country(clicked_country)
                
                elif event.button == 4:  # Mouse wheel up
                    self.map_renderer.adjust_zoom(ZOOM_SPEED, mouse_x, mouse_y)
                
                elif event.button == 5:  # Mouse wheel down
                    self.map_renderer.adjust_zoom(1/ZOOM_SPEED, mouse_x, mouse_y)
                    
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == DRAG_BUTTON:
                    self.dragging = False
                    self.last_mouse_pos = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.last_mouse_pos:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x - self.last_mouse_pos[0]
                    dy = mouse_y - self.last_mouse_pos[1]
                    self.map_renderer.pan(dx, dy)
                    self.last_mouse_pos = (mouse_x, mouse_y)
            
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    self.map_renderer.pan(PAN_SPEED, 0)
                elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.map_renderer.pan(-PAN_SPEED, 0)
                elif event.key in [pygame.K_UP, pygame.K_w]:
                    self.map_renderer.pan(0, PAN_SPEED)
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.map_renderer.pan(0, -PAN_SPEED)
        
        return True

    def update_fps(self):
        """Update FPS counter"""
        self.frame_count += 1
        current_time = pygame.time.get_ticks()
        if current_time - self.last_time > 1000:  # Update every second
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_time = current_time

    def run(self):
        """Main game loop"""
        running = True
        while running:
            # Handle input
            running = self.handle_input()
            
            # Draw
            self.map_renderer.draw(self.country_manager, self.city_manager)
            
            # Update FPS counter
            self.update_fps()
            fps_text = self.map_renderer.font.render(f"FPS: {self.fps}", True, (0, 0, 0))
            fps_rect = fps_text.get_rect(bottomleft=(10, WINDOW_HEIGHT - 10))
            pygame.draw.rect(self.screen, (255, 255, 255), fps_rect.inflate(8, 4))
            self.screen.blit(fps_text, fps_rect)
            
            # Update display
            pygame.display.flip()
            
            # Cap framerate
            self.clock.tick(TARGET_FPS)

        pygame.quit()
