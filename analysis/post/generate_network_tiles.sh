#!/bin/bash

NETWORKDIR="data/networks"
TMPDIR="/tmp"
WORKDIR="data/tiles"
OUTDIR="tiles"
# NOTE: tiles generated in `data/tiles` are temporary, those in `tiles` ar deployed to the server.

BARRIER_TYPE="dams"

for region in '02' '03' '05_06' '07_10' '08_11' '12' '13' '21'
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    ogr2ogr -t_srs EPSG:4326 -f GeoJSON $TMPDIR/network.json $NETWORKDIR/$region/$BARRIER_TYPE/network.shp

    echo "Creating tiles"
    tippecanoe -f -Z 10 -z 16 -l networks -o $TILEDIR/networks$region.mbtiles $TMPDIR/network.json
    rm $TMPDIR/network.json

    echo "Done processing region"
    echo "--------------------"
    echo
done

tile-join -f $OUTDIR/networks.mbtiles \
    $TILEDIR/networks02.mbtiles \
    $TILEDIR/networks03.mbtiles \
    $TILEDIR/networks05_06.mbtiles \
    $TILEDIR/networks07_10.mbtiles \
    $TILEDIR/networks08_11.mbtiles \
    $TILEDIR/networks12.mbtiles \
    $TILEDIR/networks13.mbtiles \
    $TILEDIR/networks21.mbtiles