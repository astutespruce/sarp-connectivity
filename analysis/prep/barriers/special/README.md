# One-time barrier data preparation steps

The following tasks are performed a single time based on a particular version of the source dataset, or are re-run as needed on update of the underlying network.

Each of the following tasks are independent of each other and are not presented in any particular order.

## Download and extract OpenStreetMap dams

OpenStreetMap (OSM) data for North America was downloaded from https://osmtoday.com/north_america.html on 8/29/2024.

OSM data are very slow to process. Features of interest are first extracted to a GPKG file using the following command-line commands:

```bash
export OSM_CONFIG_FILE="analysis/prep/barriers/special/osmconf.ini"

ogr2ogr data/barriers/source/northamerica_osm.gpkg -nln points data/barriers/source/north_america.pbf -sql "SELECT * from points WHERE \"waterway\" in ('waterfall', 'dam', 'weir', 'fish_pass')"
ogr2ogr data/barriers/source/northamerica_osm.gpkg -nln lines -update data/barriers/source/north_america.pbf -sql "SELECT * from lines WHERE \"waterway\" in ('dam', 'weir', 'fish_pass')"
ogr2ogr data/barriers/source/northamerica_osm.gpkg -nln multipolygons -update data/barriers/source/north_america.pbf -sql "SELECT * from multipolygons WHERE \"waterway\" in ('dam', 'weir', 'fish_pass')"
```

Dams and waterfalls are extracted from OSM data using `analysis/prep/barriers/special/extract_osm_barriers.py`.

These data are provided directly to Kat for integration into the master dams dataset on AGOL.

## Prepare NABD dams

The National Anthropogenic Barrier Database is used to help snap dams derived
from NID, unless otherwise manually reviewed.

NABD dams are prepared using `analysis/prep/barriers/special/prep_nabd.py`.

## Estimate dams from waterbodies

`analysis/prep/barriers/special/estimate_dams.py` is used to estimate dams using waterbody drain points and boundaries.

This only considers drains on smaller sizeclass rivers and streams; the results
on larger sizeclasses were not good (typically ponds downstream of major dams
that were not actually impounded).

It does the following for each drain point / waterbody pair:

1. extract the waterbody boundary (exterior ring).
2. find the position of the drain point on the exterior ring.
3. extract vertex coordinates along the boundary on each side of the drain point up to 50 points per side (less if the polygon has fewer vertices).
4. the extracted vertices are used for form a single line.
5. the line is simplified using [Visvalingam-Whyatt simplification](https://en.wikipedia.org/wiki/Visvalingam%E2%80%93Whyatt_algorithm). This calculates the area of each triangle formed by each triad of 3 contiguous vertices within the line. The vertex that creates the triangle with the smallest area is dropped. This process is repeated until there are no more vertices to drop, or the smallest area is greater than either 100 m2 or 1/100th of the area in the waterbody, whichever is smaller.
6. the simplified line is then further evaluated to find suitably straight sections. The angle of each contiguous triad of vertices (measured from the middle vertex of each triad) is calculated, and if within 180° +/- 10° that vertex is dropped. This process of dropping low angle vertices is repeated 5 times.
7. the result at this point is a fairly straight polyline (`LineString`).
8. the length of each segment within the polyline is calculated. Any segments that are greater than 30 meters and less than 45% of the total length of the waterbody boundary are retained. NOTE: these lengths are based on the significant vertices extracted above, not the original vertices of the boundary.
9. once the above segments are identified, a polyline is extracted for each based on the original vertices. That is, if the above approach identifies vertices 1 and 8 as straight enough and long enough segments, this extracts all vertices 1,2,3,4,5,6,7,8.
10. the extracted polylines are intersected with a 1 meter buffer around the drain point; only those that intersect are retained.
11. the position of the drain point is calculated on those polylines. The drain point must occur within the interior of those lines by at least 1 meter (meaning: not at the endpoints) in order for those polylines to be retained. This avoids extracting straight side edges of waterbodies that end at the drain point.

Note: this uses [numba](http://numba.pydata.org/) to speed up several of the
internal operations. You will need to install numba in order to run this script.

Estimated dams are crosschecked against dams in the master inventory. Dams that do not duplicate existing dams are provided to SARP for manual review and integration into the master inventory.

## Dam removal costs

Estimated dam costs were modeled by Suman Jumani (TNC) and provided to Kat Hoenke on 1/16/2024,
saved to `data/barriers/source/sarp_dam_costpred_V2.xlsx`.

We extracted Mean and 95% upper / lower prediction intervals and saved to a Feather file for faster joins later.
These were post-processed using `analysis/prep/barriers/special/extract_cost_estimates.py`.

## Modeled road crossings

Modeled road crossings are prepared using `analysis/prep/barriers/special/prep_raw_road_crossings.py`

NOTE: this needs to be rerun each time the underlying network data are updated or any of the data used in the spatial joins are updated.

Modeled road crossings are derived from USGS road / stream crossings and USFS road / stream crossings.  They are used as snapping targets for surveyed road-related barriers and to help mark which ones have been surveyed.

USGS crossing ownership is joined from the associated crossing observation data table packaged with the crossings based on shared identifiers, if the modeled point and observed point are within 100 meters.

Census TIGER roads (2022 version) are spatially joined to the modeled crossings and used to supplement ownership information, based on the road type recorded in the TIGER roads dataset.

USGS and USFS modeled road crossings are combined into a single dataset, with preference given to USGS crossings.  They are assigned a crossing code based on methods from the North Atlantic Aquatic Connectivity Collaborative, and then deduplicated based on that crossing code.  This removes duplicate crossings at exactly the same location that result from overlapping road types at the same crossing point.

Crossings are then deduplicated based on clustering crossings that are individually no more than 5 meters apart.  This finds all clusters of crossings where any pair of crossing in the cluster is less than 5 meters apart, even though some members of the cluster may be more than 5 meters apart from other barriers.  This uses a connected components graph algorithm.  The purpose of this is to deduplicate chains of very close crossings into a single representative point for the overall crossing.

Crossings are then snapped to the nearest flowline in the network based on a 10 meter tolerance.  

Crossings are spatially joined to a variety of contextual datasets after snapping.

Any crossings that do not snap are dropped from all subsequent analyses.