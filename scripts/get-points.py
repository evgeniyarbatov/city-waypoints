import sys
import osmium

import numpy as np
import pandas as pd

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
        
        way_lat = np.mean(way_coords[:, 0])
        way_lon = np.mean(way_coords[:, 1])

        name = self.get_name(w.tags)

        self.ways.append([
            name,
            (float(way_lat), float(way_lon)),
            way_nodes,
        ])            

def write_csv(ways, filename):
    df = pd.DataFrame(ways, columns=[
        'name',
        'coordinates', 
        'way_border', 
    ])

    df[['lat', 'lon']] = df['coordinates'].apply(pd.Series)
    df = df[df['name'] != 'Unknown']
    
    df[[
        'name',
        'lat',
        'lon',
        'way_border',
    ]].to_csv(filename, index=False)

def main(osm_file, filename):
    handler = WayHandler()
    handler.apply_file(osm_file, locations=True)
    write_csv(handler.ways, filename)

if __name__ == "__main__":
    main(*sys.argv[1:])