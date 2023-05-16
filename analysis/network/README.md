# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Network Analysis

Once all the inputs are prepared (see `analysis/prep/README.md`), you now run the network analysis on all regions.

1. Cut flowlines by barriers
2. Create networks
3. Export networks (if needed)

## Cut flowlines by barriers

Run `cut_flowlines.py` to aggregate all barriers and cut all flowlines.

This creates the following output files:

- `networks/raw/all_barriers.feather`: all barrier types aggregated into single dataset
- `networks/raw/<HUC2>/flowlines.feather`: cut flowlines
- `networks/raw/<HUC2>/flowline_joins.feather`: joins for above flowlines
- `networks/raw/<HUC2>/barrier_joins.feather`: joins for lineIDs upstream / downstream of barriers

This cuts the network at each barrier and associates each barrier with an upstream and downstream flowline segment ID. It automatically calculates a new unique ID for a segment if it is creating a new segment between two barriers on the same original flowline segment. The networks are then re-assembled by traversing upstream from the downstream-most points of the NHD flowlines or from each barrier.

## Create networks

Run `run_network_analysis.py` to create networks for dams and small barriers, for all networks and only perennial networks (4 scenarios).

This creates the following output files:

- `networks/clean/<HUC2>/network_segments.feather`: lookup of lineID to networkID, for each of the 4 scenarios above; for flowlines located in this HUC2
- `networks/clean/<HUC2>/network_stats__dams.feather`: network stats for dams on all networks; for networks that originate in this HUC2
- `networks/clean/<HUC2>/network_stats__small_barriers.feather`

IMPORTANT: there may be multiple upstream networks from a given barrier or origin point. If this is encountered, the multiple networks
are merged together into a single network.

## Export networks

The output of this analysis is:

- `network.feather`: a feather file with one feature per functional network, including the upstream and downstream network IDs associated with each barrier.
- `network.gpkg`: a geopackage with one feature per functional network, including the upstream and downstream network IDs associated with each barrier.
- `barriers_network.feather`: a feather file with one record per barrier, with statistics from the upstream network, downstream length, and upstream / downstream network identifiers.
