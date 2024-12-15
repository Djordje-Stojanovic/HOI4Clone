"""Country class and related functionality"""
import random
from typing import List, Tuple, Dict, Optional
import numpy as np

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

    def get_polygons(self, zoom: float) -> List[np.ndarray]:
        """Get polygons at appropriate detail level"""
        # Skip points based on zoom level
        if zoom <= 0.5:
            return [poly[::16] for poly in self.polygons]  # Very low detail
        elif zoom <= 1.0:
            return [poly[::8] for poly in self.polygons]   # Low detail
        elif zoom <= 2.0:
            return [poly[::4] for poly in self.polygons]   # Medium detail
        elif zoom <= 4.0:
            return [poly[::2] for poly in self.polygons]   # High detail
        else:
            return self.polygons                           # Full detail

    def get_visible_polygons(self, min_lon: float, max_lon: float, 
                           min_lat: float, max_lat: float, zoom: float) -> List[np.ndarray]:
        """Get only the polygons that are visible in the viewport"""
        # Quick bounding box check
        if (max_lon < self.min_lon or min_lon > self.max_lon or 
            max_lat < self.min_lat or min_lat > self.max_lat):
            return []
        
        # Get polygons at appropriate detail level
        polygons = self.get_polygons(zoom)
        
        # Filter points to only those in viewport with margin
        margin = 1.0  # degree margin to prevent edge artifacts
        visible_polygons = []
        for polygon in polygons:
            # Use numpy for faster filtering
            mask = ((polygon[:, 0] >= min_lon - margin) & 
                   (polygon[:, 0] <= max_lon + margin) &
                   (polygon[:, 1] >= min_lat - margin) & 
                   (polygon[:, 1] <= max_lat + margin))
            
            if np.any(mask):  # Only process if any points are visible
                # Get consecutive segments of visible points
                changes = np.diff(mask.astype(int))
                segment_starts = np.where(changes == 1)[0] + 1
                segment_ends = np.where(changes == -1)[0] + 1
                
                if mask[0]:
                    segment_starts = np.insert(segment_starts, 0, 0)
                if mask[-1]:
                    segment_ends = np.append(segment_ends, len(mask))
                
                # Add points just outside the visible segments
                for start, end in zip(segment_starts, segment_ends):
                    segment = polygon[max(0, start-1):min(len(polygon), end+1)]
                    if len(segment) >= 3:
                        visible_polygons.append(segment)
        
        return visible_polygons

    def contains_point(self, lon: float, lat: float) -> bool:
        """Check if a point is inside the country"""
        # Quick bounding box check
        if (lon < self.min_lon or lon > self.max_lon or 
            lat < self.min_lat or lat > self.max_lat):
            return False
        
        point = np.array([lon, lat])
        
        # Ray casting algorithm using numpy
        for polygon in self.polygons:
            inside = False
            j = len(polygon) - 1
            
            for i in range(len(polygon)):
                if ((polygon[i, 1] > lat) != (polygon[j, 1] > lat) and
                    lon < (polygon[j, 0] - polygon[i, 0]) * (lat - polygon[i, 1]) /
                    (polygon[j, 1] - polygon[i, 1]) + polygon[i, 0]):
                    inside = not inside
                j = i
                
            if inside:
                return True
        
        return False

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
