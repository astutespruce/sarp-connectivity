# Southeast Aquatic Barrier Inventory Data Processing

This project involves several data processing steps to work from raw aquatic network and barrier data to outputs of the network and connectivity analyses:

## Data preparation:

### 1. Aquatic network data

The National Hydrography Dataset - High-Resolution Plus version is pre-processed to extract flowlines and joins between flowlines that are used in the remainder of the analysis.

See [analysis/prep/network/README.md](prep/network).

### 2. Boundary data

Boundary datasets, such as states, counties, and watersheds, are joined to barriers during processing and are also displayed on maps. These boundaries are obtained from various sources, extracted within the SARP region, and projected to a standard projection.

See [`analysis/prep/boundaries/README.md`](prep/boundaries).

### 3. Aquatic barrier data

Aquatic barriers are obtained in advance or downloaded from live-edited feature services hosted on ArcGIS Online. They are consolidated, snapped to the aquatic network, de-duplicated, and otherwise processed to prepare for the network analysis.

See [analysis/prep/barriers/README.md](prep/barriers).

### 4. Species data

See [analysis/prep/species/README.md](prep/species).

## Network analysis

Aquatic barriers are used to cut flowlines, which are then aggregated into functional networks between barriers and aquatic network origin / termination points. Multiple scenarios are run: natural networks (only waterfalls), dams (dams + waterfalls), small barriers (small barriers + dams + waterfalls).

See [analysis/network/README.md](network).

## Prioritization analysis

Aquatic barriers are ranked according to their network metrics using 3 different scenarios that express network connectivity and watershed condition. These data are then reformatted for use in the API and for creating vector tiles of the inventory.

See [analysis/rank/README.md](rank).

## Post-processing

See [analysis/post/README.md](post).
