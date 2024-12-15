# HOI4 Clone

A Hearts of Iron IV inspired map visualization using Natural Earth Data.

## Project Structure

```
hoi4clone/
├── src/
│   └── hoi4clone/
│       ├── core/           # Core game components
│       │   ├── city.py     # City and CityManager classes
│       │   ├── country.py  # Country and CountryManager classes
│       │   ├── game.py     # Main game loop and input handling
│       │   └── map.py      # Map rendering and coordinate handling
│       ├── utils/          # Utility modules
│       │   └── config.py   # Game configuration and constants
│       ├── data/           # Map data files
│       │   ├── ne_10m_admin_0_countries/
│       │   ├── ne_10m_admin_1_states_provinces/
│       │   └── ne_10m_populated_places/
│       └── main.py         # Entry point
├── tests/                  # Test files
├── docs/                   # Documentation
├── setup.py               # Package configuration
└── README.md              # This file

## Features

- Interactive world map visualization
- Country selection and highlighting
- City display based on population
- Smooth zooming and panning
- Viewport optimization for performance
- Multiple detail levels based on zoom

## Dependencies

- Python 3.8+
- pygame
- geopandas
- numpy
- shapely
- rtree

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Djordje-Stojanovic/HOI4Clone.git
cd HOI4Clone
```

2. Install dependencies:
```bash
pip install -e .
```

## Running

```bash
python -m hoi4clone.main
```

## Controls

- Left Mouse Button: Pan map
- Right Mouse Button: Select country
- Mouse Wheel: Zoom in/out
- Arrow Keys/WASD: Pan map

## Data Sources

Using Natural Earth Data (1:10m scale):
- Admin 0 Countries
- Admin 1 States/Provinces
- Populated Places

## License

[MIT License](LICENSE)
