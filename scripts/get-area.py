import sys
import ast
import pyproj

import pandas as pd

from shapely.geometry import Polygon
from shapely.ops import transform

def get_area(row):
    polygon = Polygon(row['way_border'])
    
    proj_wgs84 = pyproj.Proj('EPSG:4326')  # WGS84
    proj_utm = pyproj.Proj('EPSG:32648')  # UTM zone 48N

    projected_polygon = transform(
        pyproj.Transformer.from_proj(proj_wgs84, proj_utm).transform, 
        polygon,
    )
    
    return projected_polygon.area   

def main(
    parks_filename,
    area_filename,
):
    df = pd.read_csv(parks_filename)
    df['way_border'] = df['way_border'].apply(ast.literal_eval)
    
    df['area'] = df.apply(get_area, axis=1)
    df = df.sort_values(by='area', ascending=False)

    df[[
        'name',
        'way_id',
        'area',
    ]].to_csv(area_filename, index=False)

if __name__ == "__main__":
    main(*sys.argv[1:])