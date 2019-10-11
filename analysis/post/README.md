# Southeast Aquatic Barrier Inventory Data Processing - Post-Processing

Once all data have been processed from the network analysis and prioritization steps, they can be summarized for each of the summary units used in the tool.

Vector tiles are created to display the summary statistics by summary unit, as well as to show points for the barrier inventory.

### Summary statistics

Run `analysis/post/extract_summary_stats.py` to generate an overall summary file used by the user interface in the tool, and a summary file for each of the summary units to be attached to their vector tiles.

### Vector tiles

From the root directory of the repository, run the shell script `analysis/post/generate_tiles.sh`.

This generates tiles for:

-   dams with and without barriers
-   small barriers with networks, and small barriers without barriers plus road crossings
-   summary units with summary statistics attached

Final tiles for deployment are in `/tiles`
