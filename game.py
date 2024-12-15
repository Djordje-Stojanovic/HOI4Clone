"""Main game loop and input handling"""
import pygame
import json
from config import *
from map import MapRenderer
from country import CountryManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Hearts of Iron IV Clone")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.country_manager = CountryManager()
        self.map_renderer = MapRenderer(self.screen)
        
        # Input state
        self.dragging = False
        self.last_mouse_pos = None
        
        # Load map data
        with open('countries.geo.json', 'r') as f:
            geojson_data = json.load(f)
            self.country_manager.load_from_geojson(geojson_data)

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
                    # Convert screen coordinates to geographic
                    lon, lat = self.map_renderer.screen_to_geo(mouse_x, mouse_y)
                    
                    # Find clicked country
                    clicked_country = None
                    for country in self.country_manager.countries.values():
                        if country.contains_point(lon, lat):
                            clicked_country = country
                            break
                    
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

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_input()
            
            # Draw
            self.map_renderer.draw(self.country_manager)
            
            # Update display
            pygame.display.flip()
            
            # Cap framerate
            self.clock.tick(TARGET_FPS)

        pygame.quit()
