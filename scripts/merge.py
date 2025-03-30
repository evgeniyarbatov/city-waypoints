import sys

import pandas as pd

DISTANCE_CUTOFF_METERS = 30000

def main(
    points_filename, 
    area_filename, 
    distance_filename,
    output_filename,
):
    points_df = pd.read_csv(points_filename)
    area_df = pd.read_csv(area_filename)
    distance_df = pd.read_csv(distance_filename)

    df = pd.merge(area_df, distance_df, on='name', how='inner') 
    df = pd.merge(df, points_df, on='name', how='inner') 

    df = df[df['distance'] <= DISTANCE_CUTOFF_METERS]
    df = df.sort_values(by=['area', 'distance'], ascending=[False, True])

    df = df.drop_duplicates(subset=['name'], keep='first')
    df = df[['name', 'area', 'distance', 'lat', 'lon']]

    df.to_csv(output_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])