import sys
import osmium

import numpy as np
import pandas as pd

from haversine import haversine, Unit

class WayHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.ways = []

    def is_temple(self, tags):
        return (
            tags.get('landuse') == 'religious' or
            tags.get('building') == 'temple'
        )

    def is_park(self, tags):
        return (
            tags.get('leisure') in {'park', 'garden', 'nature_reserve'} or
            tags.get('landuse') in {'recreation_ground', 'grass'} or
            tags.get('boundary') == 'national_park'
        )

    def is_lake(self, tags):
        return (
            tags.get('water') in {'lake', 'pond', 'reservoir'} or
            (tags.get('natural') == 'water' and tags.get('water') in {'lake', 'pond', 'reservoir'})
        )

    def is_interesting_tag(self, tags):
        return self.is_temple(tags) or self.is_park(tags) or self.is_lake(tags)

    def get_name(self, tags):
        return tags.get('name:en', tags.get('name', 'Unknown'))

    def way(self, w):
        if not self.is_interesting_tag(w.tags):
            return

        way_nodes = []
        for n in w.nodes:
            try:
                way_nodes.append((
                    float(n.lat),
                    float(n.lon),                    
                ))
            except:
                continue
        
        way_coords = np.array(way_nodes)
        if way_coords.size == 0:
            return

        name = self.get_name(w.tags)

        self.ways.append([
            name,
            way_nodes,
        ])            

def get_point(start, way_border):
    distances = [haversine(start, (float(lat), float(lon))) for lat, lon in way_border]
    min_dist_index = distances.index(min(distances))
    return way_border[min_dist_index]

def write_csv(
    start_lat, 
    start_lon, 
    ways, 
    filename,
):
    df = pd.DataFrame(ways, columns=[
        'name',
        'way_border', 
    ])
    
    df = df[df['name'] != 'Unknown']
    df = df.drop_duplicates(subset='name', keep=False) 
        
    df['way_border'] = df['way_border'].apply(lambda x: [(float(lat), float(lon)) for lat, lon in x])
    
    df[['lat', 'lon']] = df['way_border'].apply(
        lambda way: pd.Series(get_point((float(start_lat), float(start_lon)), way))
    )
    
    df[[
        'name',
        'lat',
        'lon',
        'way_border',
    ]].to_csv(filename, index=False)

def main(
    start_lat, 
    start_lon, 
    osm_file, 
    filename,
):
    handler = WayHandler()
    handler.apply_file(osm_file, locations=True)
    write_csv(
        start_lat, 
        start_lon,
        handler.ways, 
        filename,
    )

if __name__ == "__main__":
    main(*sys.argv[1:])