#!/bin/bash

NETWORKDIR="data/networks"
TMPDIR="/tmp"
OUTDIR="tiles"


### Create tiles for dams network
# Note: these networks include the complete flowlines, not just dam upstream networks

BARRIER_TYPE="dams"

# disconnected regions
for region in '02' '03' '12' '13' '21'
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
    ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -sql "SELECT geom,networkID from network" $TMPDIR/network.json $NETWORKDIR/$region/$BARRIER_TYPE/network.gpkg

    echo "Creating tiles"
    tippecanoe -f -Z 9 -z 16 -l networks -P -pg -o $TMPDIR/dam_networks$region.mbtiles $TMPDIR/network.json
    rm $TMPDIR/network.json

    echo "Done processing region"
    echo "--------------------"
    echo
done

# merged regions
for region in '05' '06' '07' '08' '10' '11'
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
    ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -sql "SELECT geom,networkID from network" $TMPDIR/network.json $NETWORKDIR/merged/$region/$BARRIER_TYPE/network.gpkg

    echo "Creating tiles"
    tippecanoe -f -Z 9 -z 16 -l networks -P -pg -o $TMPDIR/dam_networks$region.mbtiles $TMPDIR/network.json
    rm $TMPDIR/network.json

    echo "Done processing region"
    echo "--------------------"
    echo
done


echo "Merging regions to create final tileset"
tile-join -f -pg -o $OUTDIR/dam_networks.mbtiles \
    $TMPDIR/dam_networks02.mbtiles \
    $TMPDIR/dam_networks03.mbtiles \
    $TMPDIR/dam_networks05.mbtiles \
    $TMPDIR/dam_networks06.mbtiles \
    $TMPDIR/dam_networks07.mbtiles \
    $TMPDIR/dam_networks08.mbtiles \
    $TMPDIR/dam_networks11.mbtiles \
    $TMPDIR/dam_networks12.mbtiles \
    $TMPDIR/dam_networks13.mbtiles \
    $TMPDIR/dam_networks21.mbtiles



## Create tiles for small barriers network
# NOTE: this includes only the networks upstream of small barriers

BARRIER_TYPE="small_barriers"

# disconnected regions
for region in '02' '03' '12' '21' # '13'  (13 does not have inventoried barriers yet)
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
    ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -sql "SELECT geom,networkID from network WHERE barrier='small_barrier'" $TMPDIR/network.json $NETWORKDIR/$region/$BARRIER_TYPE/network.gpkg

    echo "Creating tiles"
    tippecanoe -f -Z 9 -z 16 -l networks -P -pg -o $TMPDIR/small_barrier_networks$region.mbtiles $TMPDIR/network.json
    rm $TMPDIR/network.json

    echo "Done processing region"
    echo "--------------------"
    echo
done

# merged regions
for region in '05' '06' '07' '08' '10' '11'
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
    ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -sql "SELECT geom,networkID from network WHERE barrier='small_barrier'" $TMPDIR/network.json $NETWORKDIR/merged/$region/$BARRIER_TYPE/network.gpkg

    echo "Creating tiles"
    tippecanoe -f -Z 9 -z 16 -l networks -P -pg -o $TMPDIR/small_barrier_networks$region.mbtiles $TMPDIR/network.json
    rm $TMPDIR/network.json

    echo "Done processing region"
    echo "--------------------"
    echo
done

echo "Merging regions to create final tileset"
tile-join -f -pg -o $OUTDIR/small_barrier_networks.mbtiles \
    $TMPDIR/small_barrier_networks02.mbtiles \
    $TMPDIR/small_barrier_networks03.mbtiles \
    $TMPDIR/small_barrier_networks05.mbtiles \
    $TMPDIR/small_barrier_networks06.mbtiles \
    $TMPDIR/small_barrier_networks07.mbtiles \
    $TMPDIR/small_barrier_networks08.mbtiles \
    $TMPDIR/small_barrier_networks10.mbtiles \
    $TMPDIR/small_barrier_networks11.mbtiles \
    $TMPDIR/small_barrier_networks12.mbtiles \
    $TMPDIR/small_barrier_networks21.mbtiles
    # TODO: $TMPDIR/small_barrier_networks13.mbtiles \