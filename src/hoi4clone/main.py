"""Main game entry point"""
import pygame
import sys
import os
from hoi4clone.core.game import Game
from hoi4clone.core.country import CountryManager
from hoi4clone.utils.config import WINDOW_WIDTH, WINDOW_HEIGHT
import geopandas as gpd

def main():
    # Initialize Pygame with hardware acceleration
    pygame.init()
    pygame.display.set_caption("HOI4 Clone")
    
    # Set display mode with hardware acceleration flags
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    
    try:
        # Initialize country manager
        country_manager = CountryManager()
        
        # Load map data
        data_dir = os.path.join(os.path.dirname(__file__), "data")
        countries_path = os.path.join(data_dir, "ne_10m_admin_0_countries", "ne_10m_admin_0_countries.shp")
        
        # Load and convert shapefile
        gdf = gpd.read_file(countries_path)
        country_manager.load_from_geojson(gdf.__geo_interface__)
        
        # Create and run game
        game = Game(screen, country_manager)
        game.run()
        
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main()
