#!/bin/bash

WORKDIR="data/tiles"
TMPDIR="/tmp"
OUTDIR="tiles"
# NOTE: tiles generated in `data/tiles` are temporary, those in `tiles` ar deployed to the server.

### Dams with and without networks.
echo "Generating tiles for dams..."
tippecanoe -f -Z5 -z16 -B6 -pk -pg -pe -ai -o $TMPDIR/dams_with_networks.mbtiles -l dams -T sarpid:string -T name:string -T river:string -T County:string -T HUC6:string -T HUC8:string -T HUC12:string -T TotalUpstreamMiles:float -T FreeUpstreamMiles:float -T TotalDownstreamMiles:float -T FreeDownstreamMiles:float $WORKDIR/dams_with_networks.csv
tippecanoe -f -Z9 -z16 -B10 -pk -pg -pe -ai -o $TMPDIR/dams_without_networks.mbtiles -l background -T sarpid:string  -T name:string -T river:string -T excluded:bool $WORKDIR/dams_without_networks.csv

# Merge into a single tileset
tile-join -f --no-tile-size-limit -pg -o $OUTDIR/sarp_dams.mbtiles $TMPDIR/dams_with_networks.mbtiles $TMPDIR/dams_without_networks.mbtiles

## Small barriers with networks, and small barriers without networks + road crossings
echo "Generating tiles for small barriers and road crossings..."
tippecanoe -f -Z5 -z16 -B6 -pk -pg -pe -ai -o $TMPDIR/barriers_with_networks.mbtiles -l barriers -T name:string -T stream:string -T road:string -T sarpid:string -T localid:string -T crossingcode:string -T source:string -T roadtype:string -T crossingtype:string -T condition:string -T potentialproject:string -T County:string -T HUC6:string -T HUC8:string -T HUC12:string -T TotalUpstreamMiles:float -T FreeUpstreamMiles:float -T TotalDownstreamMiles:float -T FreeDownstreamMiles:float $WORKDIR/barriers_with_networks.csv

# NOTE: this is a much larger dataset, so we need to more aggressively drop points from tiles.
tippecanoe -f -Z9 -z16 -B10 -pg -pe --drop-densest-as-needed -o $TMPDIR/barriers_background.mbtiles -l background -T name:string -T stream:string -T road:string -T sarpid:string -T localid:string -T crossingcode:string -T source:string -T stream:string -T road:string -T roadtype:string -T crossingtype:string -T condition:string -T potentialproject:string -T excluded:bool $WORKDIR/barriers_background.csv

# Merge into a single tileset
tile-join -f -pg --no-tile-size-limit -pg -o $OUTDIR/sarp_barriers.mbtiles $TMPDIR/barriers_with_networks.mbtiles $TMPDIR/barriers_background.mbtiles

# Waterfalls with and without networks
echo "Generating tiles for waterfalls"
# To include other fields, include: -T stream:string -T localid:string -T source:string
tippecanoe -f -Z5 -z16 -B6 -pk -pg -pe -ai -o $OUTDIR/waterfalls.mbtiles -l waterfalls -T name:string $WORKDIR/waterfalls.csv

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