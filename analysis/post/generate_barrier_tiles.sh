#!/bin/bash

WORKDIR="data/tiles"
TMPDIR="/tmp"
OUTDIR="tiles"
# NOTE: tiles generated in `data/tiles` are temporary, those in `tiles` ar deployed to the server.

### Dams with and without networks.
echo "Generating tiles for dams..."
tippecanoe -f -Z5 -z16 -B6 -pk -pg -pe -ai -o $TMPDIR/dams_with_networks.mbtiles -l dams -T sarpid:string -T name:string -T river:string -T County:string -T HUC6:string -T HUC8:string -T HUC12:string -T Ranked:bool -T TotalUpstreamMiles:float -T FreeUpstreamMiles:float -T TotalDownstreamMiles:float -T FreeDownstreamMiles:float  -T TotalUpstreamMiles_perennial:float -T FreeUpstreamMiles_perennial:float -T TotalDownstreamMiles_perennial:float -T FreeDownstreamMiles_perennial:float $WORKDIR/dams_with_networks.csv
tippecanoe -f -Z9 -z16 -B10 -pk -pg -pe -ai -o $TMPDIR/dams_without_networks.mbtiles -l background -T sarpid:string  -T name:string -T river:string -T excluded:bool -T Ranked:bool  $WORKDIR/dams_without_networks.csv

# Merge into a single tileset
tile-join -f --no-tile-size-limit -pg -o $OUTDIR/dams.mbtiles $TMPDIR/dams_with_networks.mbtiles $TMPDIR/dams_without_networks.mbtiles

## Small barriers with networks, and small barriers without networks + road crossings
echo "Generating tiles for small barriers and road crossings..."
tippecanoe -f -Z5 -z16 -B6 -pk -pg -pe -ai -o $TMPDIR/small_barriers_with_networks.mbtiles -l barriers -T name:string -T stream:string -T road:string -T sarpid:string -T localid:string -T crossingcode:string -T source:string -T roadtype:string -T crossingtype:string -T condition:string -T potentialproject:string -T County:string -T HUC6:string -T HUC8:string -T HUC12:string -T Ranked:bool -T TotalUpstreamMiles:float -T FreeUpstreamMiles:float -T TotalDownstreamMiles:float -T FreeDownstreamMiles:float -T TotalUpstreamMiles_perennial:float -T FreeUpstreamMiles_perennial:float -T TotalDownstreamMiles_perennial:float -T FreeDownstreamMiles_perennial:float $WORKDIR/small_barriers_with_networks.csv

# NOTE: this is a much larger dataset, so we need to more aggressively drop points from tiles.
tippecanoe -f -Z9 -z16 -B10 -pg -pe --drop-densest-as-needed -o $TMPDIR/small_barriers_background.mbtiles -l background -T name:string -T stream:string -T road:string -T sarpid:string -T localid:string -T crossingcode:string -T source:string -T stream:string -T road:string -T roadtype:string -T crossingtype:string -T condition:string -T potentialproject:string -T excluded:bool -T Ranked:bool $WORKDIR/small_barriers_background.csv

# Merge into a single tileset
tile-join -f -pg --no-tile-size-limit -pg -o $OUTDIR/small_barriers.mbtiles $TMPDIR/small_barriers_with_networks.mbtiles $TMPDIR/small_barriers_background.mbtiles

# Waterfalls with and without networks
echo "Generating tiles for waterfalls"
# To include other fields, include: -T stream:string -T localid:string -T source:string
tippecanoe -f -Z5 -z16 -B6 -pk -pg -pe -ai -o $OUTDIR/waterfalls.mbtiles -l waterfalls -T name:string $WORKDIR/waterfalls.csv

echo "#### ALL DONE ####"