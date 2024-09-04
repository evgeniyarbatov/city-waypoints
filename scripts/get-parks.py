import sys
import osmium

import numpy as np
import pandas as pd

class WayHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.ways = []

    def is_interesting_tag(self, tags):
        is_leisure = 'leisure' in tags
        if not is_leisure:
            return False
        
        is_park = 'park' in tags['leisure']
        return is_park

    def get_tags(self, tags):
        return ','.join([f"{key}={value}" for key, value in tags])

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

        tags = self.get_tags(w.tags)

        self.ways.append([
            w.id,
            (float(way_lat), float(way_lon)),
            way_nodes,
            tags,
        ])            

def write_csv(ways, parks_filename):
    def split_tags(tags):
        if pd.isna(tags):
            return pd.Series()
        try:
            tag_dict = dict(tag.split('=') for tag in tags.split(','))
        except ValueError:
            return pd.Series()
        return pd.Series(tag_dict)

    df = pd.DataFrame(ways, columns=[
        'way_id', 
        'coordinates', 
        'way_border', 
        'tags',
    ])
    
    df = df.join(df['tags'].apply(split_tags))
    df = df.dropna(subset=['name'])
 
    df[['lat', 'lon']] = df['coordinates'].apply(pd.Series)
    
    df[[
        'name',
        'way_id',
        'lat',
        'lon',
        'way_border',
    ]].to_csv(parks_filename, index=False)

def main(osm_file, parks_filename):
    handler = WayHandler()
    handler.apply_file(osm_file, locations=True)
    write_csv(handler.ways, parks_filename)

if __name__ == "__main__":
    main(*sys.argv[1:])