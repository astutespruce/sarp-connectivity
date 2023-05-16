# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Barrier Prioritization

Once all networks have been generated and merged across regions, barriers can be prioritized using their network connectivity metrics.

This involves the following steps:

1. the master dataset for each barrier type is joined to the merged network results across all regions
2. barriers are scored and tiers are calculated for 3 scenarios: Network Connectivity (NC), Watershed Condition (WC), and Combined (NCWC), at the regional and state levels.
3. output files are prepared for use by the API and for vector tiles.

Run `analysis/post/aggregate_networks.py`.
