CITY_NAME = hanoi

URL = https://download.geofabrik.de/asia/vietnam-latest.osm.pbf
COUNTRY_OSM_FILE = $$(basename $(URL))

COUNTRY_OSM_DIR = ~/osm
CITY_OSM_DIR = osm

GADM = gadm/gadm41_VNM_1.json
POLYGON = polygon/$(CITY_NAME).poly
PARKS = parks/$(CITY_NAME).csv

VENV_PATH = ~/.venv/city-parks

all: venv install

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@source $(VENV_PATH)/bin/activate && \
	pip install --disable-pip-version-check -q -r requirements.txt

country:
	@mkdir -p $(COUNTRY_OSM_DIR)
	@if [ ! -f $(COUNTRY_OSM_DIR)/$(COUNTRY_OSM_FILE) ]; then \
		wget $(URL) -P $(COUNTRY_OSM_DIR); \
	fi

polygon:
	@mkdir -p $(dir $(POLYGON))
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-polygon.py $(GADM) $(POLYGON);

city:
	@mkdir -p $(CITY_OSM_DIR)
	osmconvert $(COUNTRY_OSM_DIR)/$(COUNTRY_OSM_FILE) -B=$(POLYGON) -o=$(CITY_OSM_DIR)/$(CITY_NAME).osm.pbf
	osmium cat --overwrite $(CITY_OSM_DIR)/$(CITY_NAME).osm.pbf -o $(CITY_OSM_DIR)/$(CITY_NAME).osm

parks:
	@mkdir -p $(dir $(PARKS))
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-city-parks.py $(CITY_OSM_DIR)/$(CITY_NAME).osm $(PARKS);

.PHONY: all venv install country polygon city parks