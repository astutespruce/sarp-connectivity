# Southeast Aquatic Barrier Inventory Data Processing - Post-Processing

Once all data have been processed from the network analysis and prioritization steps, they can be summarized for each of the summary units used in the tool.

Vector tiles are created to display the summary statistics by summary unit, as well as to show points for the barrier inventory.

### Summary statistics and maps

Run `analysis/post/extract_summary_stats.py` to generate an overall summary file used by the user interface in the tool.

Run `analysis/post/create_region_maps.py` to generate thumbnails of the ranked dams in each region. This must be done after creating tilesets below.

Note: generating maps uses `pymgl` to render the maps, which is only available for MacOS or Ubuntu 20.04.

### Vector tiles

Final tiles for deployment are output to `/tiles`

Run the following Python scripts to generate barrier, summary, and network vector tiles:

- `analysis/post/create_barrier_tiles.py`
- `analysis/post/create_summary_tiles.py`
- `analysis/post/create_network_tiles.py`
