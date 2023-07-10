# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Network Analysis

Once all the inputs are prepared (see `analysis/prep/README.md`), you now run the network analysis on all regions.

1. Cut flowlines by barriers
2. Create networks
3. Calculate network statistics for removed barriers
4. Export networks (if needed)

## Cut flowlines by barriers

Run `cut_flowlines.py` to aggregate all barriers and cut all flowlines.

This creates the following output files:

- `networks/raw/all_barriers.feather`: all barrier types aggregated into single dataset
- `networks/raw/<HUC2>/flowlines.feather`: cut flowlines
- `networks/raw/<HUC2>/flowline_joins.feather`: joins for above flowlines
- `networks/raw/<HUC2>/barrier_joins.feather`: joins for lineIDs upstream / downstream of barriers

This cuts the network at each barrier and associates each barrier with an
upstream and downstream flowline segment ID. It automatically calculates a new
unique ID for a segment if it is creating a new segment between two barriers on
the same original flowline segment. The networks are then re-assembled by
traversing upstream from the downstream-most points of the NHD flowlines or from
each barrier.

## Create networks

Run `run_network_analysis.py` to create networks for dams and small barriers.

This finds HUC2s that are connected via flowlines and operates on them as a
group. It breaks the network based on a set of barrier types:

- dams: networks broken by waterfalls and dams
- small_barriers: networks broken by waterfalls, dams, and small_barriers

This creates the following output files:

- `networks/clean/<HUC2>/network_segments.feather`: lookup of lineID to networkID
  for flowlines located in this HUC2
- `networks/clean/<HUC2>/<type>_network_stats.feather`: network stats for
  each barrier type for networks that originate in this HUC2

IMPORTANT: there may be multiple upstream networks from a given barrier or
origin point. If this is encountered, the multiple networks are merged together
into a single network.

## Calculate statistics for removed barriers

Run `calc_removed_barrier_stats.py` to create networks for each removed barrier.
This performs the analysis in two steps. First, it cuts subnetworks where removed
barriers occur by all removed barriers in a single step and produces:

- `networks/clean/<HUC2>/removed_<type>_network_stats.feather`: network statistics
  for each barrier type (dams, small barriers) for removed barriers
- `networks/clean/<HUC2>/removed_barriers_network_segments.feather`: lookup of
  lineID to networkID for each barrier type

Next, it iteratively removes barriers by the year they were removed, and
recalculates new networks and associated statistics, producing:

- `networks/clean/<HUC2>/removed_<type>_networks.feather`: barrier networks for
  each barrier type. Note: GainMiles is based on other barriers still present
  at the year a given barrier was removed (including in the same year) but
  accounts for longer networks resulting from previously removed barriers.
  DO NOT sum GainMiles to get at the total miles gained from removing barriers,
  as this double-counts miles. Instead, sum EffectiveGainMiles, which is the
  GainMiles value when cutting networks by all removed barriers (no double-
  counting of miles).

## Export networks

Modify and run `analysis/export/export_networks.py` to export dissolved networks
for visualization.
