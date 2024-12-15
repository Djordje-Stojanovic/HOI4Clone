import geopandas as gpd
from pathlib import Path
import numpy as np
from shapely.geometry import box

class DataLoader:
    @staticmethod
    def load_map_data(width, height):
        """Load and process Natural Earth data"""
        # Load country boundaries
        countries_path = Path("src/data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
        countries_gdf = gpd.read_file(countries_path)
        
        # Filter to WW2 European theater countries with modern names
        ww2_countries = {
            # Central Powers Region
            'Germany': 'Germany',
            'Poland': 'Poland',
            'Czech Republic': 'Czech Republic',
            'Slovakia': 'Slovakia',
            'Austria': 'Austria',
            'Hungary': 'Hungary',
            
            # Western Europe
            'France': 'France',
            'Belgium': 'Belgium',
            'Netherlands': 'Netherlands',
            'Luxembourg': 'Luxembourg',
            'Switzerland': 'Switzerland',
            
            # British Isles
            'United Kingdom': 'United Kingdom',
            'Ireland': 'Ireland',
            
            # Southern Europe
            'Italy': 'Italy',
            'Spain': 'Spain',
            'Portugal': 'Portugal',
            'Greece': 'Greece',
            'Albania': 'Albania',
            'Serbia': 'Serbia',
            'Croatia': 'Croatia',
            'Slovenia': 'Slovenia',
            'Bosnia and Herz.': 'Bosnia and Herzegovina',
            'Montenegro': 'Montenegro',
            'Macedonia': 'North Macedonia',
            
            # Eastern Europe
            'Romania': 'Romania',
            'Bulgaria': 'Bulgaria',
            'Moldova': 'Moldova',
            'Ukraine': 'Ukraine',
            'Belarus': 'Belarus',
            'Lithuania': 'Lithuania',
            'Latvia': 'Latvia',
            'Estonia': 'Estonia',
            'Russia': 'Russia',
            
            # Nordic Countries
            'Norway': 'Norway',
            'Sweden': 'Sweden',
            'Finland': 'Finland',
            'Denmark': 'Denmark',
            'Iceland': 'Iceland',
            
            # Mediterranean and North Africa
            'Turkey': 'Turkey',
            'Cyprus': 'Cyprus',
            'Syria': 'Syria',
            'Lebanon': 'Lebanon',
            'Israel': 'Israel',
            'Palestine': 'Palestine',
            'Egypt': 'Egypt',
            'Libya': 'Libya',
            'Tunisia': 'Tunisia',
            'Algeria': 'Algeria',
            'Morocco': 'Morocco',
            
            # Middle East
            'Iraq': 'Iraq',
            'Iran': 'Iran',
            'Saudi Arabia': 'Saudi Arabia',
            'Jordan': 'Jordan'
        }
        
        # Filter countries and update names
        countries_gdf = countries_gdf[countries_gdf['NAME'].isin(ww2_countries.keys())]
        countries_gdf['NAME'] = countries_gdf['NAME'].map(ww2_countries)
        
        # Project to Web Mercator for better display
        countries_gdf = countries_gdf.to_crs(epsg=3857)
        
        # Define WW2 European theater bounding box (rough coordinates in Web Mercator)
        # Extended east to Moscow and north to include more of Scandinavia
        theater_bounds = box(-2500000, 0, 8000000, 12000000)
        
        # Clip geometries to theater bounds
        countries_gdf['geometry'] = countries_gdf.geometry.intersection(theater_bounds)
        
        # Remove empty geometries after clipping
        countries_gdf = countries_gdf[~countries_gdf.geometry.is_empty]
        
        # Calculate bounds for proper centering
        bounds = countries_gdf.total_bounds
        x_scale = width / (bounds[2] - bounds[0])
        y_scale = height / (bounds[3] - bounds[1])
        scale = min(x_scale, y_scale) * 0.9  # 90% of full scale
        
        return countries_gdf, bounds, scale
