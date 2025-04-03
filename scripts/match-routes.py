import sys
import ast
import requests

import pandas as pd

OSRM_URL = "http://localhost:6001/match/v1/foot/"
MATCH_RADIUS_METERS = 10

def get_matched_pair(coord1, coord2):
    coords_str = f"{coord1[1]},{coord1[0]};{coord2[1]},{coord2[0]}"
    url = f"{OSRM_URL}{coords_str}?radiuses={MATCH_RADIUS_METERS};{MATCH_RADIUS_METERS}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        matched_coords = []
        if "tracepoints" in data:
            for tracepoint in data["tracepoints"]:
                (lon, lat) = tracepoint["location"]
                matched_coords.append((lat, lon))

        return matched_coords
    except requests.RequestException as e:
        return [coord1, coord2] 

def main(
    routes_filename,
):
    df = pd.read_csv(routes_filename)
    
    matched_data = []
    for _, row in df.iterrows():        
        route = ast.literal_eval(row["route"])
        
        matched_route = []
        for i in range(len(route) - 1):
            matched_route.extend(
                get_matched_pair(route[i], route[i + 1]),
            )

        if route:
            matched_route.append(route[-1])
        
        matched_data.append({
            "name": row["name"], 
            "route": matched_route,
        })

    matched_df = pd.DataFrame(matched_data)
    matched_df.to_csv(routes_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])