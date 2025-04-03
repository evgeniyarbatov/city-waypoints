PROJECT_NAME := $(shell basename $(PWD))
VENV_PATH = ~/.venv/city-parks

START_LAT = 20.99483375616291
START_LON = 105.86792091531574

URL = https://download.geofabrik.de/asia/vietnam-latest.osm.pbf
COUNTRY_OSM_FILE = $$(basename $(URL))

OSM_DIR = osm

CITY_NAME = hanoi
RADIUS_KM = 20

CIRCLE = data/$(CITY_NAME).poly
POINTS = data/$(CITY_NAME).csv
ROUTES = data/$(CITY_NAME)-routes.csv
WAYPOINTS = data/$(CITY_NAME)-waypoints.gpx
MAP = data/$(CITY_NAME)-routes.gpx
MAP_COMPRESSED = data/$(CITY_NAME)-routes-compressed.gpx

all: venv install

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@source $(VENV_PATH)/bin/activate && \
	pip install --disable-pip-version-check -q -r requirements.txt

country:
	if [ ! -f $(OSM_DIR)/$(COUNTRY_OSM_FILE) ]; then \
		wget $(URL) -P $(OSM_DIR); \
	fi

circle:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-circle.py \
	$(START_LAT) \
	$(START_LON) \
	$(RADIUS_KM) \
	$(CIRCLE);

city:
	@osmconvert $(OSM_DIR)/$(COUNTRY_OSM_FILE) -B=$(CIRCLE) -o=$(OSM_DIR)/$(CITY_NAME).osm.pbf
	@osmium cat --overwrite $(OSM_DIR)/$(CITY_NAME).osm.pbf -o $(OSM_DIR)/$(CITY_NAME).osm

	@osmfilter $(OSM_DIR)/$(CITY_NAME).osm --keep="highway=motorway highway=trunk highway=primary highway=secondary highway=tertiary" -o=$(OSM_DIR)/$(CITY_NAME)-roads.osm
	@osmium cat --overwrite $(OSM_DIR)/$(CITY_NAME)-roads.osm -o $(OSM_DIR)/$(CITY_NAME)-roads.osm.pbf

points:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-points.py \
	$(START_LAT) \
	$(START_LON) \
	$(OSM_DIR)/$(CITY_NAME).osm \
	$(POINTS);

docker:
	@open -a Docker
	@while ! docker info > /dev/null 2>&1; do \
			sleep 1; \
	done
	@docker stop $$(docker ps -a -q)
	@docker compose up --build -d

clean:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/clean-points.py \
	$(START_LAT) \
	$(START_LON) \
	$(RADIUS_KM) \
	$(POINTS);

waypoints:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/waypoints.py \
	$(POINTS) \
	$(WAYPOINTS);

routes:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-routes.py \
	$(START_LAT) \
	$(START_LON) \
	$(POINTS) \
	$(ROUTES);

match:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/match-routes.py \
	$(ROUTES);

map:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/make-map.py \
	$(ROUTES) \
	$(MAP);

compress:
	@gpsbabel -i gpx -f $(MAP) \
	-x simplify,crosstrack,error=0.01k \
	-o gpx -F $(MAP_COMPRESSED);

.PHONY: all venv install docker country circle city points clean waypoints routes match map compress