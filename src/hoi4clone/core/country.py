"""Country class and related functionality"""
import random
from typing import List, Tuple, Dict, Optional
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

class Country:
    def __init__(self, name: str, polygons: List[List[Tuple[float, float]]]):
        self.name = name
        # Convert polygons to numpy arrays for faster operations
        self.polygons = [np.array(polygon, dtype=np.float32) for polygon in polygons]
        # Generate random color
        self.color = (
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(100, 200)
        )
        self.selected = False
        
        # Calculate bounding box
        all_points = np.vstack(self.polygons)
        self.min_lon = np.min(all_points[:, 0])
        self.max_lon = np.max(all_points[:, 0])
        self.min_lat = np.min(all_points[:, 1])
        self.max_lat = np.max(all_points[:, 1])
        
        # Create Shapely polygons and calculate areas
        self.shapely_polygons = []
        self.polygon_areas = []
        for poly in self.polygons:
            shapely_poly = Polygon(poly)
            self.shapely_polygons.append(shapely_poly)
            self.polygon_areas.append(shapely_poly.area)

    def get_polygons(self, zoom: float) -> List[np.ndarray]:
        """Get polygons at appropriate detail level"""
        # Define area thresholds for different zoom levels
        zoom_thresholds = [
            (0.5, 10.0, 8),  # zoom <= 0.5: very large landmasses, every 8th point
            (1.0, 5.0, 4),   # zoom <= 1.0: large landmasses, every 4th point
            (2.0, 1.0, 2),   # zoom <= 2.0: medium landmasses, every 2nd point
            (4.0, 0.1, 1),   # zoom <= 4.0: small islands, all points
            (float('inf'), 0.0, 1)  # zoom > 4.0: everything, all points
        ]
        
        # Find appropriate threshold
        area_threshold = 0.0
        point_skip = 1
        for max_zoom, min_area, skip in zoom_thresholds:
            if zoom <= max_zoom:
                area_threshold = min_area
                point_skip = skip
                break
        
        # Get polygons that meet the area threshold
        visible_polys = []
        for poly, area in zip(self.polygons, self.polygon_areas):
            if area >= area_threshold:
                # Take every nth point based on zoom level
                points = poly[::point_skip]
                if len(points) >= 3:  # Ensure we have enough points for a polygon
                    visible_polys.append(points)
        
        return visible_polys

    def get_visible_polygons(self, min_lon: float, max_lon: float, 
                           min_lat: float, max_lat: float, zoom: float) -> List[np.ndarray]:
        """Get only the polygons that are visible in the viewport"""
        # Quick bounding box check
        if (max_lon < self.min_lon or min_lon > self.max_lon or 
            max_lat < self.min_lat or min_lat > self.max_lat):
            return []
        
        # Get polygons at appropriate detail level
        polygons = self.get_polygons(zoom)
        
        # Filter points to only those in viewport
        visible_polygons = []
        for polygon in polygons:
            # Use numpy for faster filtering
            mask = ((polygon[:, 0] >= min_lon - 1) & (polygon[:, 0] <= max_lon + 1) &
                   (polygon[:, 1] >= min_lat - 1) & (polygon[:, 1] <= max_lat + 1))
            visible_points = polygon[mask]
            if len(visible_points) >= 3:
                visible_polygons.append(visible_points)
        
        return visible_polygons

    def contains_point(self, lon: float, lat: float) -> bool:
        """Check if a point is inside the country"""
        # Quick bounding box check
        if (lon < self.min_lon or lon > self.max_lon or 
            lat < self.min_lat or lat > self.max_lat):
            return False
        
        point = Polygon([(lon, lat)])
        return any(poly.contains(point) for poly in self.shapely_polygons)

    def get_color(self) -> Tuple[int, int, int]:
        """Get country color, adjusted for selection state"""
        if self.selected:
            return tuple(min(c + 50, 255) for c in self.color)
        return self.color

class CountryManager:
    def __init__(self):
        self.countries: Dict[str, Country] = {}
        self.selected_country: Optional[Country] = None

    def load_from_geojson(self, geojson_data: dict):
        """Load countries from GeoJSON data"""
        # Clear existing data
        self.countries.clear()
        self.selected_country = None
        
        # Process features
        for idx, feature in enumerate(geojson_data['features']):
            # Get country name
            name = (feature['properties'].get('NAME_EN') or 
                   feature['properties'].get('ADMIN') or 
                   feature['properties'].get('NAME') or 
                   f"Country_{idx}")
            
            # Extract polygons
            geometry = feature['geometry']
            if geometry['type'] == 'Polygon':
                polygons = [geometry['coordinates'][0]]  # Take exterior ring only
            else:  # MultiPolygon
                polygons = [poly[0] for poly in geometry['coordinates']]  # Take exterior ring of each polygon
            
            # Create country
            country = Country(name, polygons)
            self.countries[name] = country

    def get_country_at_point(self, lon: float, lat: float) -> Optional[Country]:
        """Find country at point"""
        for country in self.countries.values():
            if country.contains_point(lon, lat):
                return country
        return None

    def select_country(self, country: Optional[Country]):
        """Select a country and deselect others"""
        if self.selected_country:
            self.selected_country.selected = False
        self.selected_country = country
        if country:
            country.selected = True
