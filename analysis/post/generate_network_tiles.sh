#!/bin/bash

NETWORKDIR="data/networks"
TMPDIR="/tmp"
WORKDIR="data/tiles"
OUTDIR="tiles"
# NOTE: tiles generated in `data/tiles` are temporary, those in `tiles` ar deployed to the server.

BARRIER_TYPE="dams"

# Note: these networks include the complete flowlines, not just dam upstream networks
for region in '02' '03' '05_06' '07_10' '08_11' '12' '13' '21'
do
    echo "Processing ${region}"

    echo "Converting to GeoJSON"
    # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
    ogr2ogr -t_srs EPSG:4326 -f GeoJSONSeq -sql "SELECT networkID from network" $TMPDIR/network.json $NETWORKDIR/$region/$BARRIER_TYPE/network.shp

    echo "Creating tiles"
    tippecanoe -f -Z 9 -z 16 -l networks -P -pg -o $WORKDIR/dam_networks$region.mbtiles $TMPDIR/network.json
    rm $TMPDIR/network.json

    echo "Done processing region"
    echo "--------------------"
    echo
done

echo "Merging regions to create final tileset"
tile-join -f -pg -o $OUTDIR/dam_networks.mbtiles \
    $WORKDIR/dam_networks02.mbtiles \
    $WORKDIR/dam_networks03.mbtiles \
    $WORKDIR/dam_networks05_06.mbtiles \
    $WORKDIR/dam_networks07_10.mbtiles \
    $WORKDIR/dam_networks08_11.mbtiles \
    $WORKDIR/dam_networks12.mbtiles \
    $WORKDIR/dam_networks13.mbtiles \
    $WORKDIR/dam_networks21.mbtiles





# BARRIER_TYPE="small_barriers"

# # NOTE: 13 and 21 do not have small barrier networks
# for region in '02' '03' '05_06' '07_10' '08_11' '12' # '13' '21'
# do
#     echo "Processing ${region}"

#     echo "Converting to GeoJSON"
#     # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
#     # GPKG data are not getting the right CRS, so we provide it ourselves.
#     # NOTE: GPKG data are already limited to networkID only
#     ogr2ogr -t_srs EPSG:4326 -s_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -f GeoJSONSeq $TMPDIR/network.json $WORKDIR/small_barriers_network${region}.gpkg

#     # echo "Creating tiles"
#     tippecanoe -f -Z 9 -z 16 -l networks -P -pg -o $WORKDIR/small_barrier_networks$region.mbtiles $TMPDIR/network.json
#     rm $TMPDIR/network.json

#     echo "Done processing region"
#     echo "--------------------"
#     echo
# done

# echo "Merging regions to create final tileset"
# tile-join -f -pg -o $OUTDIR/small_barrier_networks.mbtiles \
#     $WORKDIR/small_barrier_networks02.mbtiles \
#     $WORKDIR/small_barrier_networks03.mbtiles \
#     $WORKDIR/small_barrier_networks05_06.mbtiles \
#     $WORKDIR/small_barrier_networks07_10.mbtiles \
#     $WORKDIR/small_barrier_networks08_11.mbtiles \
#     $WORKDIR/small_barrier_networks12.mbtiles





# # In case tiles for JUST the dam upstream networks are needed
# for region in '02' '03' '05_06' '07_10' '08_11' '12' '13' '21'
# do
#     echo "Processing ${region}"

#     echo "Converting to GeoJSON"
#     # Use GeoJSONSeq for faster parsing in tippecanoe, using the -P option
#     # GPKG data are not getting the right CRS, so we provide it ourselves.
#     # NOTE: GPKG data are already limited to networkID only
#     ogr2ogr -t_srs EPSG:4326 -s_srs "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs" -f GeoJSONSeq $TMPDIR/network.json $WORKDIR/dam_networks${region}.gpkg

#     # echo "Creating tiles"
#     tippecanoe -f -Z 9 -z 16 -l networks -P -pg -y "networkID" -o $WORKDIR/dam_networks$region.mbtiles $TMPDIR/network.json
#     rm $TMPDIR/network.json

#     echo "Done processing region"
#     echo "--------------------"
#     echo
# done

# echo "Merging regions to create final tileset"
# tile-join -f -pg -o $OUTDIR/dam_networks.mbtiles \
#     $WORKDIR/dam_networks02.mbtiles \
#     $WORKDIR/dam_networks03.mbtiles \
#     $WORKDIR/dam_networks05_06.mbtiles \
#     $WORKDIR/dam_networks07_10.mbtiles \
#     $WORKDIR/dam_networks08_11.mbtiles \
#     $WORKDIR/dam_networks12.mbtiles \
#     $WORKDIR/dam_networks13.mbtiles \
#     $WORKDIR/dam_networks21.mbtiles

