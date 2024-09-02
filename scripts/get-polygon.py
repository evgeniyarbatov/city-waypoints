import sys
import json
import os

import geopandas as gpd

def get_filter(filepath):
    filename = os.path.basename(filepath)
    with open('config.json', 'r') as file:
        data = json.load(file)
    filter = data.get(filename)
    return (filter.get('key'), filter.get('value'))

def get_pff(polygon, name):
    pff = f"{name.lower()}\n"
    
    geometry_coordinates = [list(x.exterior.coords) for x in polygon.geoms]
    for idx, geometry in enumerate(geometry_coordinates, start=1):
        pff += f"{idx}\n"
        for coord in geometry:
            pff += f"\t{coord[0]}\t{coord[1]}\n"
        pff += "END\n"
    pff += "END"
    return pff

def main(args):
    gadm_filename = args[0]
    output_filename = args[1]
 
    gdf = gpd.read_file(gadm_filename)
    
    key, value = get_filter(gadm_filename)
    gdf = gdf[gdf[key] == value]

    polygon = gdf['geometry'].iloc[0]
    pff = get_pff(polygon, value)

    with open(f"{output_filename}", "w") as file:
        file.write(pff)
    
if __name__ == "__main__":
    main(sys.argv[1:])