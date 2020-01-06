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
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/boundary.json $DATADIR/SARP_boundary_prj.shp
tippecanoe -f -z 8 -l boundary -pg -o $TILEDIR/boundary.mbtiles $TMPDIR/boundary.json
rm $TMPDIR/boundary.json

ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/mask.json $DATADIR/sarp_mask.shp
tippecanoe -z 8 -l mask -pg -o $TILEDIR/mask.mbtiles $TMPDIR/mask.json
rm $TMPDIR/mask.json

### Watersheds

# HUC6
echo "Generating HUC6 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/HUC6.json $DATADIR/HUC6_prj.shp
tippecanoe -f -z 8 -l HUC6 -pg -o $TILEDIR/HUC6.mbtiles  -T id:string $TMPDIR/HUC6.json
rm $TMPDIR/HUC6.json

# HUC8
echo "Generating HUC8 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/HUC8.json $DATADIR/HUC8_prj.shp
tippecanoe -f -z 10 -l HUC8 -pg -o $TILEDIR/HUC8.mbtiles  -T id:string $TMPDIR/HUC8.json
rm $TMPDIR/HUC8.json

# HUC12
echo "Generating HUC12 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/HUC12.json $DATADIR/HUC12_prj.shp
tippecanoe -f -Z 6 -z 14 -pg -l HUC12 -o $TILEDIR/HUC12.mbtiles  -T id:string $TMPDIR/HUC12.json
rm $TMPDIR/HUC12.json


### States and counties
echo "Generating state tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/states.json $DATADIR/states_prj.shp
tippecanoe -f -z 8 -l State -pg -o $TILEDIR/states.mbtiles $TMPDIR/states.json
rm $TMPDIR/states.json

echo "Generating county tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/counties.json $DATADIR/counties_prj.shp
tippecanoe -f -Z 3 -z 12 -pg -l County -o $TILEDIR/counties.mbtiles $TMPDIR/counties.json
rm $TMPDIR/counties.json

### Ecoregions
echo "Generating Ecoregion Level 3 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/ECO3.json $DATADIR/eco3_prj.shp
tippecanoe -f -z 10 -l ECO3 -pg -o $TILEDIR/ECO3.mbtiles  -T id:string $TMPDIR/ECO3.json
rm $TMPDIR/ECO3.json

echo "Generating Ecoregion Level 4 tiles..."
ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/ECO4.json $DATADIR/eco4_prj.shp
tippecanoe -f -Z 3 -z 12 -l ECO4 -pg -o $TILEDIR/ECO4.mbtiles  -T id:string $TMPDIR/ECO4.json
rm $TMPDIR/ECO4.json

echo "#### ALL DONE ####"