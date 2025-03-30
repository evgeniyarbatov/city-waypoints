PROJECT_NAME := $(shell basename $(PWD))

START_LAT = 20.99483375616291
START_LON = 105.86792091531574

CITY_NAME = hanoi

URL = https://download.geofabrik.de/asia/vietnam-latest.osm.pbf

GADM = gadm/gadm41_VNM_1.json

COUNTRY_OSM_FILE = $$(basename $(URL))

OSM_DIR = osm

POLYGON = data/polygon/$(CITY_NAME).poly
POINTS = data/points/$(CITY_NAME).csv
AREA = data/area/$(CITY_NAME).csv
DISTANCE = data/distance/$(CITY_NAME).csv
WAYS = data/ways/$(CITY_NAME).csv
RESULT = data/$(CITY_NAME).csv

VENV_PATH = ~/.venv/city-parks

all: venv install

venv:
	@python3 -m venv $(VENV_PATH)

install: venv
	@source $(VENV_PATH)/bin/activate && \
	pip install --disable-pip-version-check -q -r requirements.txt

docker:
	@open -a Docker
	@while ! docker info > /dev/null 2>&1; do \
			sleep 1; \
	done
	@docker stop $$(docker ps -a -q)
	@docker compose up --build -d

country:
	if [ ! -f $(OSM_DIR)/$(COUNTRY_OSM_FILE) ]; then \
		wget $(URL) -P $(OSM_DIR); \
	fi

polygon:
	@mkdir -p $(dir $(POLYGON))
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-polygon.py $(GADM) $(POLYGON);

city:
	@osmconvert $(OSM_DIR)/$(COUNTRY_OSM_FILE) -B=$(POLYGON) -o=$(OSM_DIR)/$(CITY_NAME).osm.pbf
	@osmium cat --overwrite $(OSM_DIR)/$(CITY_NAME).osm.pbf -o $(OSM_DIR)/$(CITY_NAME).osm
	@bzip2 -f -k $(OSM_DIR)/$(CITY_NAME).osm

points:
	@mkdir -p $(dir $(POINTS))
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-points.py $(OSM_DIR)/$(CITY_NAME).osm $(POINTS);

area:
	@mkdir -p $(dir $(AREA))
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-area.py $(POINTS) $(AREA);

distance:
	@mkdir -p $(dir $(DISTANCE))
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/get-distance.py $(START_LAT) $(START_LON) $(POINTS) $(DISTANCE);

merge:
	@source $(VENV_PATH)/bin/activate && \
	python3 scripts/merge.py \
	$(POINTS) \
	$(AREA) \
	$(DISTANCE) \
	$(RESULT);

.PHONY: all venv install docker country polygon city points area distance merge