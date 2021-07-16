# Southeast Aquatic Barrier Inventory Data Processing - Post-Processing

Once all data have been processed from the network analysis and prioritization steps, they can be summarized for each of the summary units used in the tool.

Vector tiles are created to display the summary statistics by summary unit, as well as to show points for the barrier inventory.

### Waterfalls

Waterfalls are displayed on the map to help users interpret network results. No additional details are shown for waterfalls except names.

Run `analysis/post/postprocess_waterfalls.py` to export waterfalls for vector tiles (below).

NOTE: this does not currently include any network analysis results for waterfalls.

### Summary statistics

Run `analysis/post/extract_summary_stats.py` to generate an overall summary file used by the user interface in the tool.

### Vector tiles

Final tiles for deployment are output to `/tiles`

Run the following Python scripts to generate summary vector tiles and network vector tiles:

- `analysis/post/create_summary_tiles.py`
- `analysis/post/create_network_tiles.py`

Run the following shell script to create barrier tiles:

- `analysis/post/generate_barrier_tiles.sh`

This generates the on and off-network tilesets for dams, small barriers (off-network includes road crossings), and waterfalls, and joins summary stats to the boundary layers.
