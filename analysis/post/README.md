# Southeast Aquatic Barrier Inventory Data Processing - Post-Processing

Once all data have been processed from the network analysis and prioritization steps, they can be summarized for each of the summary units used in the tool.

Vector tiles are created to display the summary statistics by summary unit, as well as to show points for the barrier inventory.

### Summary statistics

Run `analysis/post/extract_summary_stats.py` to generate an overall summary file used by the user interface in the tool.

### Waterfall networks

Run `analysis/post/extract_waterfall_networks.py` to extract network statistics from the dams and small
barrier network results, which is used to make tiles below.

### Vector tiles

Final tiles for deployment are output to `/tiles`

Run the following Python scripts to generate barrier, summary, and network vector tiles:

- `analysis/post/create_barrier_tiles.py`
- `analysis/post/create_summary_tiles.py`
- `analysis/post/create_network_tiles.py`

### Region boundary maps

Each region includes a boundary map in the user interface. These are generated
using [`mbgl-renderer`](https://github.com/consbio/mbgl-renderer).

From within the `maps` directory, make sure that NodeJS 10 is installed and currently active (newer NodeJS versions NOT supported).

Then run `npm ci` if necessary to install `mbgl-renderer` and other dependencies.

Then run `npm run maps` to create maps for each of the regions; these are automatically saved to the `ui/src/images/maps` directory.
