#!/bin/bash

DATADIR="data"
NHDDIR="data/nhd/clean"
TMPDIR="/tmp"
WORKDIR="data/tiles"
OUTDIR="tiles"
# NOTE: tiles generated in `data/tiles` are temporary, those in `tiles` ar deployed to the server.

for region in '02' '03' '05_06' '07_10' '08_11' '12' '13'
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
    ogr2ogr -t_srs EPSG:4326 -s_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -f GeoJSONSeq -sql "SELECT geometry from flowlines" $TMPDIR/flowlines.json $NHDDIR/$region/flowlines.gpkg

    echo "Creating tiles"
    # -X drops all attributes
    tippecanoe -f -Z 9 -z 16 -l flowlines -P -pg -X -o $WORKDIR/flowlines$region.mbtiles $TMPDIR/flowlines.json
    rm $TMPDIR/flowlines.json

    echo "Done processing region"
    echo "--------------------"
    echo
done

# 21 is a special case, no flowlines, just use networks, since we drop all attributes anyway
region='21'
echo "Processing ${region}"
echo "Converting to GeoJSON"
# Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
ogr2ogr -t_srs EPSG:4326 -s_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -f GeoJSONSeq -sql "SELECT networkID from network" $TMPDIR/flowlines.json $DATADIR/networks/$region/dams/network.shp

echo "Creating tiles"
# -X drops all attributes
tippecanoe -f -Z 9 -z 16 -l flowlines -P -pg -X -o $WORKDIR/flowlines$region.mbtiles $TMPDIR/flowlines.json
rm $TMPDIR/flowlines.json

echo "Done processing region"
echo "--------------------"
echo


echo "Merging regions to create final tileset"
tile-join -f -pg -o $OUTDIR/flowlines.mbtiles \
    $WORKDIR/flowlines02.mbtiles \
    $WORKDIR/flowlines03.mbtiles \
    $WORKDIR/flowlines05_06.mbtiles \
    $WORKDIR/flowlines07_10.mbtiles \
    $WORKDIR/flowlines08_11.mbtiles \
    $WORKDIR/flowlines12.mbtiles \
    $WORKDIR/flowlines13.mbtiles \
    $WORKDIR/flowlines21.mbtiles
