import sys

import pandas as pd
import xml.etree.ElementTree as ET

from unidecode import unidecode

def get_waypoint_name(row):
    distance = round(row["distance"] / 1000.0)
    return f'{unidecode(row["name"])}'

def csv_to_gpx(input_csv, output_gpx):
    gpx = ET.Element("gpx", {
        "version": "1.1",
        "creator": "Evgeny Arbatov",
        "xmlns": "http://www.topografix.com/GPX/1/1"
    })

    try:
        df = pd.read_csv(input_csv)
        
        for index, row in df.iterrows():
            wpt = ET.SubElement(gpx, "wpt", {
                "lat": str(row["lat"]),
                "lon": str(row["lon"])
            })
            
            name = ET.SubElement(wpt, "name")
            name.text = get_waypoint_name(row)

        tree = ET.ElementTree(gpx)
        
        ET.indent(tree, space="  ")
        tree.write(output_gpx, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def main(
    input_filename, 
    waypoint_filename,
):
    csv_to_gpx(input_filename, waypoint_filename)

if __name__ == "__main__":
    main(*sys.argv[1:])