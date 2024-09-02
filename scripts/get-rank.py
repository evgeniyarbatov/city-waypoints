import sys
import requests

import pandas as pd

def get_way_count(row):
    overpass_query = f"""
    [out:json];
    way(id:{row['way_id']})->.park; 
    way(poly[park])(area.park);
    out count;
    """

    response = requests.get(
        "http://localhost:8000/api/interpreter", 
        params={'data': overpass_query}
    )
    data = response.json()

    for element in data['elements']:
        if 'tags' in element:
            return int(element['tags']['ways'])

def main(
    distances_filename,
    rank_filename,
):
    df = pd.read_csv(
        distances_filename,
    )

    df['way_count'] = df.apply(get_way_count, axis=1)
    df = df.sort_values(by='way_count', ascending=False)

    df.to_csv(rank_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])