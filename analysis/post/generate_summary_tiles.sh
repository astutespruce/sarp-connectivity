#!/bin/bash

WORKDIR="data/tiles"
TMPDIR="/tmp"
OUTDIR="tiles"
# NOTE: tiles generated in `data/tiles` are temporary, those in `tiles` ar deployed to the server.


### Join summary data to summary units
echo "Joining summary stats to summary units..."

# Join the summary statistics to the summary unit boundary vector tiles:
tile-join -f -pg -o $WORKDIR/states_summary.mbtiles -c $WORKDIR/State.csv $WORKDIR/states.mbtiles
tile-join -f -pg -o $WORKDIR/counties_summary.mbtiles -c $WORKDIR/County.csv $WORKDIR/counties.mbtiles
tile-join -f -pg -o $WORKDIR/HUC6_summary.mbtiles -c $WORKDIR/HUC6.csv $WORKDIR/HUC6.mbtiles
tile-join -f -pg -o $WORKDIR/HUC8_summary.mbtiles -c $WORKDIR/HUC8.csv $WORKDIR/HUC8.mbtiles
tile-join -f -pg -o $WORKDIR/HUC12_summary.mbtiles -c $WORKDIR/HUC12.csv $WORKDIR/HUC12.mbtiles
tile-join -f -pg -o $WORKDIR/ECO3_summary.mbtiles -c $WORKDIR/ECO3.csv $WORKDIR/ECO3.mbtiles
tile-join -f -pg -o $WORKDIR/ECO4_summary.mbtiles -c $WORKDIR/ECO4.csv $WORKDIR/ECO4.mbtiles


### Merge all tilesets together to create a master vector tileset:
echo "Merging all summary tiles into single tileset..."
tile-join -f -pg --no-tile-size-limit -o $OUTDIR/sarp_summary.mbtiles \
    $WORKDIR/mask.mbtiles \
    $WORKDIR/boundary.mbtiles \
    $WORKDIR/states_summary.mbtiles \
    $WORKDIR/counties_summary.mbtiles \
    $WORKDIR/huc6_summary.mbtiles \
    $WORKDIR/huc8_summary.mbtiles \
    $WORKDIR/huc12_summary.mbtiles \
    $WORKDIR/ECO3_summary.mbtiles \
    $WORKDIR/ECO4_summary.mbtiles

echo "#### ALL DONE ####"