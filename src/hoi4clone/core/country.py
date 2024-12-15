"""Country class and related functionality"""
import random
from typing import List, Tuple, Dict
import numpy as np
from shapely.geometry import Polygon, Point
from rtree import index

class Country:
    def __init__(self, name: str, polygons: List[List[Tuple[float, float]]]):
        self.name = name
        # Convert to numpy arrays for faster operations
        self.polygons = [np.array(polygon) for polygon in polygons]
        self.color = (
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        self.selected = False
        
        # Create Shapely polygons for efficient point-in-polygon testing
        self.shapely_polygons = [Polygon(polygon) for polygon in polygons]
        
        # Calculate bounding box
        all_coords = np.vstack(self.polygons)
        self.min_lon = np.min(all_coords[:, 0])
        self.max_lon = np.max(all_coords[:, 0])
        self.min_lat = np.min(all_coords[:, 1])
        self.max_lat = np.max(all_coords[:, 1])

        # Create simplified versions for different zoom levels
        self.simplified_polygons = {}
        self._create_simplified_versions()

    def _create_simplified_versions(self):
        """Create simplified versions of polygons for different zoom levels"""
        tolerances = [0.1, 0.5, 1.0, 2.0, 5.0]  # Degrees of simplification
        for tolerance in tolerances:
            simplified = []
            for poly in self.shapely_polygons:
                simplified.append(np.array(poly.simplify(tolerance).exterior.coords))
            self.simplified_polygons[tolerance] = simplified

    def get_polygons(self, zoom: float) -> List[np.ndarray]:
        """Get appropriate polygon detail level based on zoom"""
        if zoom >= 4.0:
            return self.polygons  # Full detail
        elif zoom >= 2.0:
            return self.simplified_polygons[0.1]
        elif zoom >= 1.0:
            return self.simplified_polygons[0.5]
        elif zoom >= 0.5:
            return self.simplified_polygons[1.0]
        elif zoom >= 0.3:
            return self.simplified_polygons[2.0]
        else:
            return self.simplified_polygons[5.0]

    def contains_point(self, lon: float, lat: float) -> bool:
        """Check if a geographic point is inside the country using Shapely"""
        # Quick bounding box check
        if (lon < self.min_lon or lon > self.max_lon or 
            lat < self.min_lat or lat > self.max_lat):
            return False
            
        point = Point(lon, lat)
        return any(polygon.contains(point) for polygon in self.shapely_polygons)

    def get_color(self) -> Tuple[int, int, int]:
        """Get country color, adjusted for selection state"""
        if self.selected:
            return tuple(min(c + 50, 255) for c in self.color)
        return self.color

class CountryManager:
    def __init__(self):
        self.countries: Dict[str, Country] = {}
        self.selected_country = None
        self.spatial_index = index.Index()
        self.country_lookup = []

    def load_from_geojson(self, geojson_data: dict):
        """Load countries from GeoJSON data"""
        for idx, feature in enumerate(geojson_data['features']):
            # Try different possible name fields
            name = (feature['properties'].get('NAME_EN') or 
                   feature['properties'].get('ADMIN') or 
                   feature['properties'].get('NAME') or 
                   f"Country_{idx}")
            
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
            
            country = Country(name, country_polygons)
            self.countries[name] = country
            
            # Add to spatial index
            self.country_lookup.append(country)
            self.spatial_index.insert(idx, (
                country.min_lon, 
                country.min_lat, 
                country.max_lon, 
                country.max_lat
            ))

    def get_country_at_point(self, lon: float, lat: float) -> Country:
        """Find country at point using spatial index"""
        # Query spatial index for potential matches
        for idx in self.spatial_index.intersection((lon, lat, lon, lat)):
            country = self.country_lookup[idx]
            if country.contains_point(lon, lat):
                return country
        return None

    def select_country(self, country: Country):
        """Select a country and deselect others"""
        if self.selected_country:
            self.selected_country.selected = False
        self.selected_country = country
        if country:
            country.selected = True
