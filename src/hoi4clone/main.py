"""Main game entry point"""
import pygame
import sys
from hoi4clone.core.game import Game
from hoi4clone.core.country import CountryManager
import geopandas as gpd
import os

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((1200, 800))
    pygame.display.set_caption("Map Game")
    
    # Initialize game objects
    country_manager = CountryManager()
    
    # Get the data directory path
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    # Load country data from Natural Earth shapefile
    try:
        countries_path = os.path.join(data_dir, "ne_10m_admin_0_countries", "ne_10m_admin_0_countries.shp")
        print("Loading shapefile...")
        gdf = gpd.read_file(countries_path)
        print(f"Loaded {len(gdf)} countries")
        print("Converting to GeoJSON...")
        geojson_data = gdf.__geo_interface__
        print("Loading into CountryManager...")
        country_manager.load_from_geojson(geojson_data)
        print(f"Loaded {len(country_manager.countries)} countries into manager")
    except Exception as e:
        print(f"Error loading map data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Create and run game
    game = Game(screen, country_manager)
    game.run()
    
    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
