import sys
import ast
import gpxpy

import pandas as pd
import networkx as nx
import xml.etree.ElementTree as ET

class PointGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.list_mapping = {} 
        
    def add_list(self, point_list, list_id):
        for i, point in enumerate(point_list):
            point_str = f"{point[0]},{point[1]}"
            
            if point_str not in self.list_mapping:
                self.list_mapping[point_str] = set()
            self.list_mapping[point_str].add(list_id)
            
            self.graph.add_node(point_str, lat=point[0], lon=point[1])
            
            if i > 0:
                prev_point = f"{point_list[i-1][0]},{point_list[i-1][1]}"
                self.graph.add_edge(prev_point, point_str)

    def dfs_with_backtracking(self, start_point):
        visited = set()
        full_path = []

        def dfs_recursive(node, parent=None):
            visited.add(node)
            full_path.append(node)
            
            neighbors = [n for n in self.graph.neighbors(node) if n not in visited]
            
            for neighbor in neighbors:
                dfs_recursive(neighbor, node)
                if not [n for n in self.graph.neighbors(neighbor) if n not in visited]:
                    full_path.append(node)

        start_node = f"{start_point[0]},{start_point[1]}"
        dfs_recursive(start_node)

        return full_path

    def save_to_gpx(self, path, filename):
        gpx = ET.Element("gpx", version="1.1", creator="Evgeny Arbatov", xmlns="http://www.topografix.com/GPX/1/1")

        trk = ET.SubElement(gpx, "trk")
        trkseg = ET.SubElement(trk, "trkseg")

        for node in path:
            lat = str(self.graph.nodes[node]['lat'])
            lon = str(self.graph.nodes[node]['lon'])
            ET.SubElement(trkseg, "trkpt", lat=lat, lon=lon)

        tree = ET.ElementTree(gpx)
        ET.indent(tree, space="  ")
        tree.write(filename, encoding="utf-8", xml_declaration=True)

def simplify_gpx(map_filename):
    with open(map_filename, 'r') as f:
        gpx = gpxpy.parse(f)

    gpx.simplify()

    with open(map_filename, 'w') as f:
        f.write(gpx.to_xml())

def main(
    routes_filename,
    map_filename,
):
    df = pd.read_csv(routes_filename)

    df['route'] = df['route'].apply(ast.literal_eval)
    
    routes = df['route'].tolist()
    
    pg = PointGraph()
    for i, point_list in enumerate(routes):
        pg.add_list(point_list, i)
    
    start_point = routes[0][0]
    
    path = pg.dfs_with_backtracking(start_point)
     
    pg.save_to_gpx(path, map_filename)
    
    # simplify_gpx(map_filename)
  
if __name__ == "__main__":
    main(*sys.argv[1:])