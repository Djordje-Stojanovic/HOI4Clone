"""City class and management"""
from typing import List, Dict
import geopandas as gpd

class City:
    def __init__(self, name: str, lon: float, lat: float, population: int, country: str):
        self.name = name
        self.lon = lon
        self.lat = lat
        self.population = population
        self.country = country

class CityManager:
    def __init__(self):
        self.cities: List[City] = []
        self.cities_by_country: Dict[str, List[City]] = {}
        self.country_populations: Dict[str, int] = {}

    def load_from_shapefile(self, shapefile_path: str, countries_shapefile_path: str):
        """Load cities from shapefile"""
        # Load country populations first
        print("\nLoading country populations...")
        countries_gdf = gpd.read_file(countries_shapefile_path)
        for _, row in countries_gdf.iterrows():
            name = row['ADMIN']  # Country name
            pop = row['POP_EST']
            if isinstance(pop, (int, float)) and pop > 0:
                self.country_populations[row['SOV_A3']] = int(pop)  # Store by country code
        
        # Load cities
        print("Loading cities...")
        cities_gdf = gpd.read_file(shapefile_path)
        
        # Process cities
        for _, row in cities_gdf.iterrows():
            name = row['NAME']
            population = int(row['POP_MAX'])
            point = row['geometry']
            country = row['SOV_A3']  # Country code
            
            # Create city object
            city = City(
                name=name,
                lon=point.x,
                lat=point.y,
                population=population,
                country=country
            )
            
            # Store city
            self.cities.append(city)
            
            # Group by country
            if country not in self.cities_by_country:
                self.cities_by_country[country] = []
            self.cities_by_country[country].append(city)
        
        # Sort cities by population within each country
        for cities in self.cities_by_country.values():
            cities.sort(key=lambda x: x.population, reverse=True)
        
        # Print summary
        print(f"\nLoaded {len(self.cities)} cities")
        print(f"Loaded {len(self.country_populations)} country populations")

    def get_visible_cities(self, min_lon: float, max_lon: float, 
                          min_lat: float, max_lat: float, zoom: float) -> List[City]:
        """Get cities that should be visible in the current viewport"""
        visible_cities = []
        
        # Calculate viewport width in degrees
        viewport_width = max_lon - min_lon
        
        # Get cities in viewport
        for city in self.cities:
            if (min_lon <= city.lon <= max_lon and
                min_lat <= city.lat <= max_lat):
                
                # For zoomed in views, show cities based on country population
                if viewport_width <= 10:  # When viewing a specific country
                    country_pop = self.country_populations.get(city.country, 0)
                    country_cities = self.cities_by_country.get(city.country, [])
                    if country_cities:
                        # Show N cities where N is population in millions, minimum 3
                        num_cities = max(3, int(country_pop / 1000000))
                        city_rank = country_cities.index(city)
                        if city_rank < num_cities:
                            visible_cities.append(city)
                
                # For wider views, use population thresholds
                else:
                    # Determine threshold based on viewport width
                    if viewport_width > 180:     # World view
                        threshold = 5000000
                    elif viewport_width > 60:    # Continental view
                        threshold = 2000000
                    elif viewport_width > 20:    # Regional view
                        threshold = 1000000
                    elif viewport_width > 5:     # Country view
                        threshold = 500000
                    else:                        # Local view
                        threshold = 100000
                    
                    if city.population >= threshold:
                        visible_cities.append(city)
        
        return visible_cities
