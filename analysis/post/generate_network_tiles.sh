#!/bin/bash

NETWORKDIR="data/networks"
TMPDIR="/tmp"
WORKDIR="data/tiles"
OUTDIR="tiles"
# NOTE: tiles generated in `data/tiles` are temporary, those in `tiles` ar deployed to the server.

BARRIER_TYPE="dams"

# '02'
for region in '03' '05_06' '07_10' '08_11' '12' '13' '21'
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
    ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -sql "SELECT networkID from network" $TMPDIR/network.json $NETWORKDIR/$region/$BARRIER_TYPE/network.shp

    echo "Creating tiles"
    tippecanoe -f -Z 9 -z 16 -l networks --use-attribute-for-id="networkID" -P -o $WORKDIR/networks$region.mbtiles $TMPDIR/network.json
    rm $TMPDIR/network.json

    echo "Done processing region"
    echo "--------------------"
    echo
done

echo "Merging regions to create final tileset"
tile-join -f $OUTDIR/networks.mbtiles \
    $WORKDIR/networks02.mbtiles \
    $WORKDIR/networks03.mbtiles \
    $WORKDIR/networks05_06.mbtiles \
    $WORKDIR/networks07_10.mbtiles \
    $WORKDIR/networks08_11.mbtiles \
    $WORKDIR/networks12.mbtiles \
    $WORKDIR/networks13.mbtiles \
    $WORKDIR/networks21.mbtiles