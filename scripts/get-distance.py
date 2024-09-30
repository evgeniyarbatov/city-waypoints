import sys
import requests

import pandas as pd

from haversine import haversine, Unit

def get_closest_point(start, way_border):
    """
    Find the closest coordinate in way_border to the target coordinates.
    """
    way_border = eval(way_border)  # Convert string to list of tuples
    
    distances = [haversine(start, (float(lat), float(lon))) for lat, lon in way_border]
    min_dist_index = distances.index(min(distances))
    
    return way_border[min_dist_index]

def get_distance(row, start):
    def osrm_format(coords):
        lat, lon = coords
        return f"{lon},{lat}"
    
    closest_point = get_closest_point(start, row['way_border'])
    stop_lat, stop_lon = closest_point
    
    points = [start] + [(stop_lat, stop_lon)]
    points = ';'.join(map(osrm_format, points))

    response = requests.get(
        f"http://127.0.0.1:6000/route/v1/foot/{points}", 
        params = {
            'geometries': 'polyline6',
            'overview': 'full',
        })
    routes = response.json()
    
    if routes['code'] != 'Ok':
        return None
    
    return routes['routes'][0]['distance']

def main(
    start_lat, 
    start_lon, 
    parks_filename, 
    distances_filename,
):
    start = (float(start_lat), float(start_lon))
    
    df = pd.read_csv(parks_filename)
    
    df['distance'] = df.apply(
        get_distance, 
        axis = 1,
        start = start
    )
    df = df.sort_values(by='distance', ascending=True)
    df = df.drop_duplicates(subset=['name'], keep='first')
    
    df[[
        'name',
        'distance',
    ]].to_csv(distances_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])