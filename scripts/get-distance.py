import sys
import requests

import pandas as pd

def get_distance(row, start):
    def osrm_format(coords):
        lat, lon = coords
        return f"{lon},{lat}"
    
    points = [start] + [(row['lat'], row['lon'])]
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
    start = (start_lat, start_lon)
    
    df = pd.read_csv(parks_filename)
    
    df['distance'] = df.apply(
        get_distance, 
        axis = 1,
        start = start
    )
    df = df.sort_values(by='distance', ascending=False)
    
    df[[
        'name',
        'way_id',
        'distance',
    ]].to_csv(distances_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])