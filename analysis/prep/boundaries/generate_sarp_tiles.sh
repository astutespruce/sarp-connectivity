#!/bin/bash

# NOTE: for each vector tileset below, we first have to convert
# the shapefile to WGS84 GeoJSON, stored in /tmp
# Since these can get big and ogr2ogr will not overwrite them, they are cleaned up after.

# This is run from the root directory
TMPDIR="/tmp"
DATADIR="data/boundaries"
TILEDIR="data/tiles"

### SARP boundary and mask
echo "Generating boundary and mask tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/boundary.json $DATADIR/sarp_boundary.gpkg -progress
tippecanoe -f -z 8 -l boundary -pg -P -o $TILEDIR/boundary.mbtiles $TMPDIR/boundary.json
rm $TMPDIR/boundary.json

ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/mask.json $DATADIR/sarp_mask.gpkg -progress
tippecanoe -f -z 8 -l mask -pg -P -o $TILEDIR/mask.mbtiles $TMPDIR/mask.json
rm $TMPDIR/mask.json

### Watersheds

# HUC6
echo "Generating HUC6 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/HUC6.json $DATADIR/sarp_huc6.gpkg -progress
tippecanoe -f -z 8 -l HUC6 -pg -P --detect-shared-borders -o $TILEDIR/HUC6.mbtiles  -T id:string $TMPDIR/HUC6.json
rm $TMPDIR/HUC6.json

# HUC8
echo "Generating HUC8 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/HUC8.json $DATADIR/sarp_huc8_priorities.gpkg -progress
tippecanoe -f -z 10 -l HUC8 -pg -P --detect-shared-borders -o $TILEDIR/HUC8.mbtiles  -T id:string $TMPDIR/HUC8.json
rm $TMPDIR/HUC8.json

# HUC12
echo "Generating HUC12 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/HUC12.json $DATADIR/sarp_huc12.gpkg -progress
tippecanoe -f -Z 6 -z 14 -pg -P --detect-shared-borders -l HUC12 -o $TILEDIR/HUC12.mbtiles  -T id:string $TMPDIR/HUC12.json
rm $TMPDIR/HUC12.json


### States and counties
echo "Generating state tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/states.json $DATADIR/sarp_states.gpkg -progress
tippecanoe -f -z 8 -l State -pg -P --detect-shared-borders -o $TILEDIR/states.mbtiles $TMPDIR/states.json
rm $TMPDIR/states.json

echo "Generating county tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/counties.json $DATADIR/sarp_counties.gpkg -progress
tippecanoe -f -Z 3 -z 12 -pg -P --detect-shared-borders -l County -o $TILEDIR/counties.mbtiles $TMPDIR/counties.json
rm $TMPDIR/counties.json

### Ecoregions
echo "Generating Ecoregion Level 3 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/ECO3.json $DATADIR/sarp_eco3.gpkg -progress
tippecanoe -f -z 10 -l ECO3 -pg -P --detect-shared-borders -o $TILEDIR/ECO3.mbtiles  -T id:string $TMPDIR/ECO3.json
rm $TMPDIR/ECO3.json

echo "Generating Ecoregion Level 4 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq $TMPDIR/ECO4.json $DATADIR/sarp_eco4.gpkg -progress
tippecanoe -f -Z 3 -z 12 -l ECO4 -pg -P --detect-shared-borders -o $TILEDIR/ECO4.mbtiles  -T id:string $TMPDIR/ECO4.json
rm $TMPDIR/ECO4.json

echo "#### ALL DONE ####"