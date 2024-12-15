import pygame
import time
from game.map_renderer import MapRenderer
from game.data_loader import DataLoader
from game.input_handler import InputHandler
from game.game_state import GameState

class EuropaGame:
    def __init__(self, width=1024, height=768):
        pygame.init()
        pygame.display.set_caption("WW2 European Theater Map")
        
        # Set display flags for better performance
        self.screen = pygame.display.set_mode(
            (width, height),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        
        # Enable vertical sync to prevent screen tearing
        pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED, vsync=1)
        
        self.width = width
        self.height = height
        
        # Performance monitoring
        self.frame_times = []
        self.show_fps = True
        
        # Initialize components
        self.state = GameState(width, height)
        self.renderer = MapRenderer(width, height)
        self.input_handler = InputHandler()
        
        # Load map data
        print("Loading map data...")
        self.countries_gdf, bounds, scale = DataLoader.load_map_data(width, height)
        print(f"Map loaded with {len(self.countries_gdf)} countries")
        print(f"Countries: {', '.join(sorted(self.countries_gdf['NAME'].tolist()))}")
        
        self.state.set_map_bounds(bounds, scale)
        
        # Calculate center position based on bounds
        center_x = (bounds[2] + bounds[0]) / 2
        center_y = (bounds[3] + bounds[1]) / 2
        
        # Set initial view to center of map
        # Adjusted for the expanded map area
        self.input_handler.offset_x = width/2 - (center_x - bounds[0]) * scale * 0.7
        self.input_handler.offset_y = height/2 - (center_y - bounds[1]) * scale * 0.7
        self.input_handler.zoom = 0.7  # Start more zoomed out to show the expanded area

        # Initialize fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def update_fps(self):
        """Update FPS calculation"""
        current_time = time.time()
        self.frame_times.append(current_time)
        
        # Keep only the last second of frames
        while self.frame_times and self.frame_times[0] < current_time - 1:
            self.frame_times.pop(0)
        
        return len(self.frame_times)

    def run(self):
        """Main game loop"""
        running = True
        clock = pygame.time.Clock()
        
        print("Starting game loop...")
        print(f"Initial offset: ({self.input_handler.offset_x}, {self.input_handler.offset_y})")
        print(f"Initial zoom: {self.input_handler.zoom}")
        
        while running:
            # Event handling
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_f:  # Toggle FPS display
                        self.show_fps = not self.show_fps
                    elif event.key == pygame.K_d:  # Debug info
                        print(f"Current offset: ({self.input_handler.offset_x}, {self.input_handler.offset_y})")
                        print(f"Current zoom: {self.input_handler.zoom}")
            
            # Handle input and update state
            selected_country, offset_x, offset_y, zoom = self.input_handler.handle_input(
                self.countries_gdf, 
                self.state.screen_to_geo,
                events
            )
            self.state.update(selected_country, offset_x, offset_y, zoom)
            
            # Clear screen
            self.screen.fill(self.renderer.WATER)
            
            # Draw map
            map_surface = self.renderer.draw_countries(
                self.countries_gdf,
                self.state.selected_country,
                self.state.transform_coords
            )
            
            # Draw to screen
            self.screen.blit(map_surface, (0, 0))
            
            # Draw UI elements
            if self.state.selected_country:
                text = self.font.render(self.state.selected_country, True, (255, 255, 255))
                # Draw with black outline for better visibility
                outline_color = (0, 0, 0)
                for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    outline = self.font.render(self.state.selected_country, True, outline_color)
                    self.screen.blit(outline, (11+dx, 11+dy))
                self.screen.blit(text, (11, 11))
            
            # Draw controls help
            help_text = [
                "Controls:",
                "Arrow keys or Left click + drag: Pan map",
                "Mouse wheel: Zoom in/out at cursor",
                "Left click: Select country",
                "F: Toggle FPS",
                "D: Print debug info",
                "ESC: Quit"
            ]
            for i, line in enumerate(help_text):
                text = self.small_font.render(line, True, (255, 255, 255))
                # Draw with black outline
                outline = self.small_font.render(line, True, (0, 0, 0))
                pos_y = self.height - 140 + i * 20
                self.screen.blit(outline, (11, pos_y+1))
                self.screen.blit(text, (10, pos_y))
            
            # Draw FPS
            if self.show_fps:
                fps = self.update_fps()
                fps_text = self.small_font.render(f"FPS: {fps}", True, (255, 255, 255))
                self.screen.blit(fps_text, (self.width - 80, 10))
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = EuropaGame()
    game.run()
