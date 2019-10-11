# Southeast Aquatic Barrier Inventory Data Processing - Post-Processing

Once all data have been processed from the network analysis and prioritization steps, they can be summarized for each of the summary units used in the tool.

Vector tiles are created to display the summary statistics by summary unit, as well as to show points for the barrier inventory.

### Summary statistics

Run `analysis/post/extract_summary_stats.py` to generate an overall summary file used by the user interface in the tool, and a summary file for each of the summary units to be attached to their vector tiles.

### Vector tiles

#### Dams

Different zoom levels are used to display dams based on whether or not they have networks. Dams without networks generally are not visible until you zoom further in. This was done in part to limit the total size of the tiles, and focus the available space on dams that have the highest value (those with networks).

In `data/tiles` directory:

```
tippecanoe -f -Z5 -z12 -B6 -pk -pg -pe -ai -o dams_with_networks.mbtiles -l dams -T name:string -T river:string -T protectedland:bool -T County:string -T HUC6:string -T HUC8:string -T HUC12:string dams_with_networks.csv

tippecanoe -f -Z9 -z12 -B10 -pk -pg -pe -ai -o dams_without_networks.mbtiles -l background -T name:string -T river:string -T protectedland:bool dams_without_networks.csv
```

Merge the tilesets for dams with and without networks into a single tileset.

In `data/tiles` directory:

```
tile-join -f --no-tile-size-limit -o ../../tiles/sarp_dams.mbtiles dams_with_networks.mbtiles dams_without_networks.mbtiles
```

<!--
#### Small barriers

USGS Road / stream crossings: Preprocessed using `preprocess_road_crossings.py`.

Road-related barriers (that have been evaluated and snapped to network): preprocessed and off-network barriers merged with road / stream crossings using `preprocess_small_barriers.py`.

Note: because road / stream crossings are very large, these are only included in tiles and displayed in the map at higher zoom levels.

```
tippecanoe -f -Z5 -z12 -B6 -pk -pg -pe -ai -o ../tiles/barriers_with_networks.mbtiles -l barriers -T name:string -T stream:string -T road:string -T sarpid:string  -T protectedland:bool -T County:string -T HUC6:string -T HUC8:string -T HUC12:string barriers_with_networks.csv

tippecanoe -f -Z9 -z14 -B10 -pg -pe --drop-densest-as-needed -o ../tiles/barriers_background.mbtiles -l background -T name:string -T stream:string -T road:string -T sarpid:string -T protectedland:bool barriers_background.csv
```

Merge the small barriers with and without networks into a single tileset.

In `data/tiles` directory:

```
tile-join -f --no-tile-size-limit -o ../../tiles/sarp_barriers.mbtiles barriers_with_networks.mbtiles barriers_background.mbtiles
```

#### Create summary vector tiles

The summary unit boundary vector tiles are created above, and do not need to be recreated unless the summary units change. In contrast, the summary statistics of dams and small barriers are recalculated on each update to the barriers inventory, and these are joined into the final vector tiles below.

Assumes a working directory of `data/tiles`.

Summaries are created using `summarize_by_unit.py`

Join the summary statistics to the summary unit boundary vector tiles:

```
tile-join -f -o states_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/State.csv states.mbtiles
tile-join -f -o counties_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/County.csv counties.mbtiles
tile-join -f -o HUC6_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/huc6.csv HUC6.mbtiles
tile-join -f -o HUC8_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/huc8.csv HUC8.mbtiles
tile-join -f -o HUC12_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/huc12.csv HUC12.mbtiles
tile-join -f -o ECO3_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/ECO3.csv ECO3.mbtiles
tile-join -f -o ECO4_summary.mbtiles -c /Users/bcward/projects/sarp/data/derived/ECO4.csv ECO4.mbtiles
```

Merge all tilesets together to create a master vector tileset:

```
tile-join -f --no-tile-size-limit -o ../../tiles/sarp_summary.mbtiles mask.mbtiles boundary.mbtiles states_summary.mbtiles counties_summary.mbtiles huc6_summary.mbtiles huc8_summary.mbtiles huc12_summary.mbtiles ECO3_summary.mbtiles ECO4_summary.mbtiles
``` -->
