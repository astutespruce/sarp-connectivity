# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Network Analysis

Once all the inputs are prepared (see `analysis/prep/README.md`), you now run the network analysis on all regions.

1. [Cut flowlines by barriers](#cut-flowlines-by-barriers)
2. [Create networks and calculate statistics](#create-networks-and-calculate-statistics)
3. [Calculate network statistics for removed barriers](#calculate-statistics-for removed-barriers)
4. Export networks (if needed)

The network analysis is run by default for the following network analysis types (`<type>` below):
- `dams`: networks are broken by waterfalls and dams
- `combined_barriers`: networks are broken by waterfalls, dams, and surveyed road-related barriers (excluding minor barriers)
- `largefish_barriers`: large-bodied fish networks are broken by waterfalls (unless marked as passable to salmonids), dams (unless marked as passable to salmonids), and surveyed road-related barriers marked as severe or significant barriers, or potential or proposed projects
- `smallfish_barriers`: small-bodied fish networks are broken by waterfalls, dams, and all surveyed road-related barriers (including minor barriers)

During preparation of each barrier type (see [analysis/prep/barriers/README.md](../prep/barriers/README.md)), barriers of each type that can participate in the network analysis (snapped and not dropped, excluded, duplicate, or on network loops or off-network flowlines) are assigned to a particular network type that is used to filter them for use in the above network types:
- `primary_network`: included in the default networks above
- `largefish_network`: included in the large-bodied networks above
- `smallfish_network`: included in the small-bodied networks above

These approximate different categories of barrier passability.

This makes it possible to compose network scenarios by taking different subsets of barrier types for a given network type.

See [analysis/constants.py::NETWORK_TYPES](../constants.py) for the network analysis scenario configuration.

Additional network analyses can be run by configuring a different set of barriers against a particular network type.  For example, to run on only artificial barriers but break networks for all barrier severities, this would use dams and surveyed road barriers (but not waterfalls) and use the `smallfish_network`.

## Cut flowlines by barriers

Run `cut_flowlines.py` to aggregate all barriers and cut all flowlines.

This uses the flowline joins to determine which HUC2s (NHD regions) are hydrologically connected to each other.  Networks are analyzed within the context of those hydrologically connected HUC2s.

This cuts the network at each barrier and associates each barrier with an
upstream and downstream flowline segment ID. It automatically calculates a new
unique ID for a segment if it is creating a new segment between two barriers on
the same original flowline segment. The networks are then re-assembled in the next step by traversing upstream from the downstream-most points of the NHD flowlines or from each barrier.

This cuts networks based on all snapped barriers that participate in any network analysis of all types including modeled road crossings.  While road crossings are not used to create networks, this allows us to calculate their position within the network, and count them as part of the upstream or downstream network of a given barrier.

This creates the following output files:

- `networks/connected_huc2s.feather`
- `networks/raw/all_barriers.feather`: all barrier types aggregated into single dataset
- `networks/raw/<HUC2>/flowlines.feather`: cut flowlines
- `networks/raw/<HUC2>/flowline_joins.feather`: joins for above flowlines
- `networks/raw/<HUC2>/barrier_joins.feather`: joins for lineIDs upstream / downstream of barriers


## Create networks and calculate statistics

Run `run_network_analysis.py` to create networks for each network analysis type.
The core logic for the network analysis is located in `analysis/network/lib/networks.py`.

NOTE: All network loops and off-network flowlines are excluded from the network analysis.  The network analysis assumes that all flowlines are configured in a dendritic (branching rather than looping) network configuration facing in the upstream direction, and that all network loops are properly identified and removed before the analysis.  It is a known issue that NHD does not properly identify all loops correctly and pains are taken during preparation of the flowlines and joins to correct these issues.


The core concept of this part of the network analysis is that there is a “join” between each upstream and downstream flowline that are hydrologically connected for purposes of the analysis.  A join is a pair of downstream line ID and upstream line ID.  This join is used to build an adjacency matrix that is the core of a directed graph data structure that can be used for traversing the network in the upstream dendritic (functional) or downstream linear direction.  Joins can be removed to “break” the network at that location (for example, because of a barrier), because that prevents the network traversal algorithm from stepping across that point; removing a join converts a connected network into 2 (or more) disconnected subnetworks.

Any flowline that is not upstream of another flowline becomes an “origin” point of a given network.  Origins can be either the downstream-most point on a network (e.g., where it connects to the ocean) or because the network was broken at that join for a barrier.  These types of network origins are treated separately in the analysis, but the traversal process is the same.

IMPORTANT: there may be multiple upstream networks from a given origin point.  For example, two incoming tributaries join at the barrier. If this is encountered, the multiple networks are merged together into a single network.

The script iterates over each network analysis type and removes joins between flowlines at the location of the barriers that are selected for that particular analysis.

### Create upstream functional networks

This builds a directed graph facing in the upstream network for all flowlines.  It calculates the natural origin points that are not upstream of any other flowline and the barrier origin points that are at the barriers.  For each type of origin point, it traverses the directed graph starting from their downstream end and using a breadth-first search to traverse to the upstream-most points of that network.  This identifies the set of upstream line IDs that are associated with that origin point, and all line segments in that network are assigned the line ID of the origin point.  This provides the lookup table of each flowline to the functional network it belongs to.

This uses an optimized set of graph building and traversal algorithms developed using numba.  See `analysis/lib/graph/speedups/directedgraph.py` for implementation details.

### Create upstream mainstem networks

Mainstem networks are based on flowlines that have at least 1 square mile of cumulative drainage area and are on the same stream order as their origin point.  To do this, it drops all joins where the upstream flowline has a lower stream order than the downstream flowline.  This therefore excludes any incoming tributaries of lower stream order.

This then builds a directed graph of the remaining flowline joins and traverses them from their downstream end to their upstream end in the same fashion as above.

### Create downstream linear networks

Downstream linear networks are based on traversing flowlines facing in their downstream linear flow direction.  This builds a directed graph facing in the downstream direction.  Each barrier is an “origin” point for starting the traversal, and it then traverses each join in moving in the downstream direction.

A given flowline may belong to multiple downstream linear networks that originated upstream of it.

This uses an optimized set of graph building and traversal algorithms developed using numba and further optimized for linear networks.  See `analysis/lib/graph/speedups/lineardirectedgraph.py` for implementation details.

### Calculate network statistics

Network statistics are implemented in `analysis/network/lib/stats.py`.

This uses the flowlines associated with each type of network (functional, mainstem, downstream linear) to calculate aggregated statistics based on characteristics associated with those flowlines.  For example, it sums the lengths of all flowlines associated with a given network to calculate its total length or calculates an average percent of natural landcover in the floodplains based on the size of the floodplain and amount of landcover in the floodplain for each catchment associated with each flowline.

This brings in several associated flowline attributes that are prepared in advance.  For example, it brings in all species habitat information that is associated with each NHD flowline, and uses that to calculate the total length of (possibly discontiguous) habitat within that network.

It also traverses the chain of downstream linear networks to determine if each network ultimately flows into the ocean or Great Lakes, in order to calculate the distance to that downstream endpoint, as well as the number of barriers of each type along the way.


### Outputs

This creates the following output files:

- `networks/clean/<HUC2>/network_segments.feather`: lookup of lineID to the networkID of each network analysis type (networkID is in the column with the name of the network analysis type) for flowlines located in this HUC2
- `networks/clean/<HUC2>/<type>_network_stats.feather`: network stats for
  each barrier type for networks that originate in this HUC2
- `networks/clean/<HUC2>/<type>_downstream_linear_segments.feather`: lookup of lineID to linear downstream networkID for each barrier type for networks that originate in this HUC2
- `networks/clean/<HUC2>/<type>_downstream_linear_network_stats.feather`: downstream linear network stats for each barrier type for networks that originate in this HUC2


## Calculate statistics for removed barriers

Run `calc_removed_barrier_stats.py` to create networks for each removed barrier.

This performs the analysis in two steps. First, it cuts subnetworks where removed barriers occur by all removed barriers in a single step and produces:

- `networks/clean/<HUC2>/removed_<type>_network_stats.feather`: network statistics for each network analysis type for removed barriers
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
for inspection within GIS or sharing with partners.

It produces the following outputs:

### `regionXX_artificial_barriers_networks.gdb`

These are the network lines dissolved to the network level, with functional network statistics attached.


**Attributes:**
- networkID: functional network identifier
- total_miles: total miles in the network
- perennial_miles: total perennial miles in the network based on perennial segments coded by NHD (i.e., not ephemeral / intermittent)
- intermittent_miles: total intermittent / ephemeral miles in network as coded by NHD
- altered_miles: total miles in segments coded by NHD as a canal, pipeline, falls within a reservoir, or overlaps with an NWI river type with a special modifier that indicates alteration
- unaltered_miles: total miles minus altered miles
- perennial_unaltered_miles: total perennial miles that are also not in altered status
- resilient miles: total miles that are within watersheds identified by The Nature Conservancy with above average or greater freshwater resilience (v0.44)
- cold miles: total miles that are within watersheds identified by The Nature Conservancy with above average or greater cold water temperature scores (March 2024)
- free_miles: total miles not in waterbodies
- free_perennial_miles: total perennial miles not in waterbodies
- free_intermittent_miles: total intermittent miles not in waterbodies
- free_altered_miles: total altered miles not in waterbodies
- free_unaltered_miles: total unaltered miles not in waterbodies
- free_perennial_unaltered_miles: total perennial unaltered miles not in waterbodies
- free_resilient_miles: total miles that are within watersheds identified by The Nature Conservancy with above average or greater freshwater resilience (v0.44) not in waterbodies
- free_cold_miles: total miles that are within watersheds identified by The Nature Conservancy with above average or greater cold water temperature scores (March 2024) not in waterbodies
- pct_unaltered: percent of network miles that are altered
- pct_perennial_unaltered: percent of network miles that are not altered
- pct_resilient: percent of the network miles that are in resilient watersheds
- pct_cold: percent of the network miles that are within cold water habitat watersheds
- natfldpln: percent of floodplain in natural landcover types
- sizeclasses: number of unique size classes in network
- barrier: barrier type at root of network
- flows_to_ocean: true if the network flows - possibly through downstream networks - eventually to the ocean
- flows_to_great_lakes: true if the network flows - possibly through downstream networks - eventually to one of the Great Lakes
- miles_to_outlet: distance downstream to the root of the downstream-most network.  Where flows_to_ocean is true, this will be the miles to the ocean; where flows_to_great_lakes is true, this will be miles to the outlet into the Great Lakes.



### `regionXX_artificial_barriers_segments.gdb`

These are the undissolved network lines extracted from NHD.

**Attributes:**
- lineID: internal line ID; changes every version; don't use
- intermittent: true if coded by NHD as an intermittent / ephemeral flowline type
- altered: true if coded by NHD as a canal, pipeline, falls within a reservoir, or overlaps with an NWI river type with a special modifier that indicates alteration
- waterbody: true if within a waterbody (natural or artificial)
- sizeclass: TNC size class based on drainage area
- StreamOrder: NHD modified Strahler stream order
- NHDPlusID: identifier provided by NHD that joins back to NHD High Res flowline and associated data
- FCode: NHD FCode
- FType: NHD Ftype
- TotDASqKm: NHD total drainage area in km2
- HUC4: NHD HUC4 that contains this flowline
- km: line length in km
- miles: line length in miles


It also includes  network attributes attached at flowline level (these apply to entire network not flowline):

- networkID: functional network identifier
- natfldkm2: area within floodplain that is in natural landcover types
- fldkm2: total area within floodplain
- natfldpln: percent of floodplain in natural landcover
- sizeclasses: number of unique sizeclasses in the network
- flows_to_ocean: true if the network flows - possibly through downstream networks - eventually to the ocean
- flows_to_great_lakes: true if the network flows - possibly through downstream networks - eventually to one of the Great Lakes

 





