# Southeast Aquatic Barrier Inventory Data Processing

This project involves several data processing steps to work from raw aquatic network and barrier data to outputs of the network and connectivity analyses:

## 1. Aquatic network data preparation

The National Hydrography Dataset - High Resolution Plus version is pre-processed to extract flowlines and joins between flowlines that are used in the remainder of the analysis.

See `analysis/prep/network/README.md`

## 2. Boundary data preparation

Boundary datasets, such as states, counties, and watersheds are joined to barriers during processing, and are also displayed on maps. These boundaries are obtained from various sources, extracted within the SARP region, and projected to a standard projection.

See `analysis/prep/boundaries/README.md`

## 3. Aquatic barrier data preparation

Aquatic barriers are obtained in advance or downloaded from live-edited feature services hosted on ArcGIS Online. They are consolidated, snapped to the aquatic network, de-duplicated, and otherwise processed to prepare for the network analysis.

See `analysis/prep/barriers/README.md`

## 4. Network analysis

Aquatic barriers are used to cut flowlines, which are then aggregated into functional networks between barriers and aquatic network origin / termination points. Multiple scenarios are run: natural networks (only waterfalls), dams (dams + waterfalls), small barriers (small barriers + dams + waterfalls).

See `analysis/network/README.md`

## 5. Prioritization analysis

TODO

## Postprocessing

See `analysis/post/README.md`

<!--
## Overview

Basic processing not dependent on the inventory includes:

1. Extraction and processing of summary units and other boundaries
2. Creation of summary unit vector tiles

Processing on updates to the inventory is derived into 3 main parts:

1. Download barrier data
2. Prepare barrier data to snap to network, etc
3. Perform network analysis of barriers (dams, small barriers, and waterfalls)
4. Prioritization analysis of barriers
5. Creation of vector tiles for the barriers datasets -->
