import sys
import requests
import polyline

import pandas as pd

OSRM_URL = "http://127.0.0.1:6000/route/v1/foot/"

def get_route(
    start_lat,
    start_lon,
    dest_lat, 
    dest_lon,
):
    url = f"{OSRM_URL}{start_lon},{start_lat};{dest_lon},{dest_lat}?overview=full&geometries=polyline6"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'routes' in data and data['routes']:
            polyline_encoded = data['routes'][0]['geometry']
            return polyline.decode(polyline_encoded)
    return []


def main(
    start_lat,
    start_lon,
    points_filename,
    routes_filename,
):
    df = pd.read_csv(points_filename)

    df["route"] = df.apply(
        lambda row: get_route(
            start_lat,
            start_lon,
            row["lat"], 
            row["lon"],
        ), 
        axis=1,
    )
    
    df = df.drop(columns=['lat', 'lon'])
    
    df.to_csv(routes_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])