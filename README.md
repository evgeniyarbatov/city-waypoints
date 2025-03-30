# city-waypoints

Create GPX file with waypoints in your city including parks and lakes.

## Prep

- Get URL for country OSM PBF file from https://download.geofabrik.de
- Locate GADM file for your country from https://gadm.org
- Get GADM Level 1 (city level) GeoJSON
- Add city key and value from GADM file to `config.json`.

## Run

```
make # Env setup
make docker # Start docker
make country # Get country OSM
make polygon # Create city polygon
make city # Extract city OSM
make parks # Extract parks from OSM map
make area # Get area of each park
make distance # Calculate distance to each park
make waypoints # Create GPX file with waypoints
```

