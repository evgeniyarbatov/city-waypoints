import sys
import ast
import requests
import polyline

import pandas as pd

def get_parks(parks_filename):
    def split_tags(tags):
        if pd.isna(tags):
            return pd.Series()
        try:
            tag_dict = dict(tag.split('=') for tag in tags.split(','))
        except ValueError:
            return pd.Series()
        return pd.Series(tag_dict)

    df = pd.read_csv(parks_filename, names=['way_id', 'coordinates', 'tags'])
    
    df = df.join(df['tags'].apply(split_tags))
    df = df.dropna(subset=['name'])
 
    df['coordinates'] = df['coordinates'].apply(ast.literal_eval)
    df[['lat', 'lon']] = df['coordinates'].apply(pd.Series)
    
    return df

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
    
    df = get_parks(parks_filename)
    
    df['distance'] = df.apply(
        get_distance, 
        axis = 1,
        start = start
    )
    
    df[[
        'way_id',
        'name',
        'lat',
        'lon',
        'distance',
    ]].to_csv(distances_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])