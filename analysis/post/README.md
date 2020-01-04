# Southeast Aquatic Barrier Inventory Data Processing - Post-Processing

Once all data have been processed from the network analysis and prioritization steps, they can be summarized for each of the summary units used in the tool.

Vector tiles are created to display the summary statistics by summary unit, as well as to show points for the barrier inventory.

### Waterfalls

Waterfalls are displayed on the map to help users interpret network results. No additional details are shown for waterfalls except names.

Run `analysis/post/postprocess_waterfalls.py` to export waterfalls for vector tiles (below).

NOTE: this does not currently include any network analysis results for waterfalls.

### Summary statistics

Run `analysis/post/extract_summary_stats.py` to generate an overall summary file used by the user interface in the tool, and a summary file for each of the summary units to be attached to their vector tiles.

### Networks for mapping

Run `analysis/post/extract_small_barrier_networks.py` to extract networks upstream of small barriers.
NOTE: these only the subset of networks associated with small barriers, not the full aquatic network.

Also note:
`analysis/post/extract_dam_networks.py' can be used to extract upstream networks for dams if needed.
This is not currently used.

### Vector tiles

From the root directory of the repository, run the following shell scripts:

-   `analysis/post/generate_barrier_tiles.sh`: this generates the on and off-network tilesets for dams, small barriers (off-network includes road crossings), and waterfalls, and joins summary stats to the boundary layers.
-   `analysis/post/generate_barrier_tiles.sh`: this generates the dams and small barrier networks. The networks for the dams are the complete set of networks and can be used to display flowlines on a map; the small barriers are only those networks upstream of small barriers.

Final tiles for deployment are in `/tiles`
