from setuptools import setup, find_packages

setup(
    name="hoi4clone",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pygame",
        "geopandas",
        "numpy",
        "shapely",
        "rtree",
    ],
    package_data={
        "hoi4clone.data": [
            "ne_10m_admin_0_countries/*",
            "ne_10m_admin_1_states_provinces/*",
            "ne_10m_populated_places/*",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    description="A Hearts of Iron IV clone with map visualization",
    keywords="game, map, strategy",
)
