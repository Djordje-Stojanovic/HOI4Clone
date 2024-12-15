"""City class and management"""
from typing import List, Tuple, Dict
import geopandas as gpd
import numpy as np
import os

class City:
    def __init__(self, name: str, lon: float, lat: float, population: int, country: str):
        self.name = name
        self.lon = lon
        self.lat = lat
        self.population = population
        self.country = country
        
    def get_size(self, zoom: float) -> int:
        """Calculate city marker size based on population and zoom level"""
        # Base size on population (log scale)
        base_size = np.log10(max(self.population, 1000)) - 1
        # Scale with zoom, but maintain minimum size
        return int(max(3, min(15, base_size * zoom * 1.5)))

class CityManager:
    def __init__(self):
        self.cities: List[City] = []
        self.cities_by_country: Dict[str, List[City]] = {}
        self.country_populations: Dict[str, int] = {}
        
        # Zoom level determines what percentage of cities to show
        self.percent_cities_by_zoom = {
            0.3: 0.3,    # Show top 30% at far zoom
            0.5: 0.5,    # Show top 50%
            1.0: 0.7,    # Show top 70%
            2.0: 0.9,    # Show top 90%
            4.0: 1.0     # Show all cities
        }

    def load_from_shapefile(self, shapefile_path: str, countries_shapefile_path: str):
        """Load cities and country populations"""
        # Load country populations first
        countries_gdf = gpd.read_file(countries_shapefile_path)
        for _, row in countries_gdf.iterrows():
            name = row['NAME']
            pop = row['POP_EST']
            if isinstance(pop, (int, float)) and pop > 0:  # Only store valid populations
                self.country_populations[name] = int(pop)
        
        # Load cities
        cities_gdf = gpd.read_file(shapefile_path)
        
        for _, row in cities_gdf.iterrows():
            name = row['NAME']
            population = row['POP_MAX']
            point = row['geometry']
            country = row['SOV_A3']  # Country code
            
            # Create city object
            city = City(
                name=name,
                lon=point.x,
                lat=point.y,
                population=int(population),
                country=country
            )
            
            # Store city
            self.cities.append(city)
            
            # Group by country
            if country not in self.cities_by_country:
                self.cities_by_country[country] = []
            self.cities_by_country[country].append(city)
        
        # Sort cities within each country by population
        for country_cities in self.cities_by_country.values():
            country_cities.sort(key=lambda x: x.population, reverse=True)
            
        print(f"\nCities by country:")
        for country, cities in self.cities_by_country.items():
            pop = self.country_populations.get(country, 0)
            num_cities = len(cities)
            print(f"{country}: {num_cities} cities, population {pop:,}")

    def get_visible_cities(self, min_lon: float, max_lon: float, 
                          min_lat: float, max_lat: float, zoom: float) -> List[City]:
        """Get cities that should be visible in the current viewport"""
        visible_cities = []
        
        # Find percentage of cities to show based on zoom
        percent_to_show = 0.3  # Default 30%
        for zoom_threshold, percentage in sorted(self.percent_cities_by_zoom.items()):
            if zoom >= zoom_threshold:
                percent_to_show = percentage
        
        # For each country, show number of cities based on population
        for country, cities in self.cities_by_country.items():
            # Calculate how many cities to show for this country
            country_pop = self.country_populations.get(country, 0)
            num_cities = max(3, int(country_pop / 1000000))  # At least 3 cities per country
            num_to_show = max(2, int(num_cities * percent_to_show))  # Show at least 2 cities
            
            # Get top N cities for this country that are in viewport
            count = 0
            for city in cities:
                if count >= num_to_show:
                    break
                    
                if (min_lon <= city.lon <= max_lon and
                    min_lat <= city.lat <= max_lat):
                    visible_cities.append(city)
                    count += 1
        
        return visible_cities
