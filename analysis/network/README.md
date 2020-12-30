# Southeast Aquatic Barrier Inventory Data Processing - Network Analysis

Once all the inputs are prepared (see `analysis/prep/README.md`), you now run the network analysis on all regions.

1. Run `run_network_analysis.py` (runs 3 network scenarios: natural, dams, small barriers)
2. Run `merge_networks.py` to merge networks that cross region boundaries.

This analysis cuts the network at each barrier and associates each barrier with an upstream and downstream flowline segment ID. It automatically calculates a new unique ID for a segment if it is creating a new segment between two barriers on the same original flowline segment. The networks are then re-assembled by traversing upstream from the downstream-most points of the NHD flowlines or from each barrier.

The output of this analysis is:

-   `network.feather`: a feather file with one feature per functional network, including the upstream and downstream network IDs associated with each barrier.
-   `network.gpkg`: a geopackage with one feature per functional network, including the upstream and downstream network IDs associated with each barrier.
-   `barriers_network.feather`: a feather file with one record per barrier, with statistics from the upstream network, downstream length, and upstream / downstream network identifiers.

IMPORTANT: there may be multiple upstream networks from a given barrier or origin point. If this is encountered, the multiple networks
are merged together into a single network.
