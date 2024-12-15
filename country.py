"""Country class and related functionality"""
import random
from typing import List, Tuple, Dict

class Country:
    def __init__(self, name: str, polygons: List[List[Tuple[float, float]]]):
        self.name = name
        self.polygons = polygons
        self.color = (
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        self.selected = False
        
        # Calculate bounding box for hit detection
        self.min_lon = float('inf')
        self.max_lon = float('-inf')
        self.min_lat = float('inf')
        self.max_lat = float('-inf')
        
        for polygon in polygons:
            for lon, lat in polygon:
                self.min_lon = min(self.min_lon, lon)
                self.max_lon = max(self.max_lon, lon)
                self.min_lat = min(self.min_lat, lat)
                self.max_lat = max(self.max_lat, lat)

    def contains_point(self, lon: float, lat: float) -> bool:
        """Check if a geographic point is inside the country"""
        # Quick bounding box check
        if (lon < self.min_lon or lon > self.max_lon or 
            lat < self.min_lat or lat > self.max_lat):
            return False
            
        # Check each polygon
        for polygon in self.polygons:
            if self._point_in_polygon(lon, lat, polygon):
                return True
        return False

    def _point_in_polygon(self, lon: float, lat: float, polygon: List[Tuple[float, float]]) -> bool:
        """Ray casting algorithm for point in polygon check"""
        inside = False
        j = len(polygon) - 1
        
        for i in range(len(polygon)):
            if ((polygon[i][1] > lat) != (polygon[j][1] > lat) and
                lon < (polygon[j][0] - polygon[i][0]) * (lat - polygon[i][1]) /
                (polygon[j][1] - polygon[i][1]) + polygon[i][0]):
                inside = not inside
            j = i
            
        return inside

    def get_color(self) -> Tuple[int, int, int]:
        """Get country color, adjusted for selection state"""
        if self.selected:
            return tuple(min(c + 50, 255) for c in self.color)
        return self.color

class CountryManager:
    def __init__(self):
        self.countries: Dict[str, Country] = {}
        self.selected_country = None

    def load_from_geojson(self, geojson_data: dict):
        """Load countries from GeoJSON data"""
        for feature in geojson_data['features']:
            name = feature['properties']['name']
            
            # Extract polygons from geometry
            geometry = feature['geometry']
            if geometry['type'] == 'Polygon':
                polygons = [geometry['coordinates']]
            else:  # MultiPolygon
                polygons = geometry['coordinates']
            
            # Store raw coordinates
            country_polygons = []
            for polygon in polygons:
                country_polygons.append(polygon[0])
            
            self.countries[name] = Country(name, country_polygons)

    def select_country(self, country: Country):
        """Select a country and deselect others"""
        if self.selected_country:
            self.selected_country.selected = False
        self.selected_country = country
        if country:
            country.selected = True
