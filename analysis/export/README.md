# National Aquatic Barrier Inventory & Prioritization Tool Data Processing - Data Export

Scripts in this folder are used for exporting datasets for analysis by SARP and
partners.

## Estimating dams from waterbodies

`estimate_dams.py` is used to estimate dams using waterbody drain points and
boundaries.

This only considers drains on smaller sizeclass rivers and streams; the results
on larger sizeclasses were not good (typically ponds downstream of major dams
that were not actually impounded).

It does the following for each drain point / waterbody pair:

1. extract the waterbody boundary (exterior ring).
2. find the position of the drain point on the exterior ring.
3. extract vertex coordinates along the boundary on each side of the drain point
   up to 50 points per side (less if the polygon has fewer vertices).
4. the extracted vertices are used for form a single line.
5. the line is simplified using [Visvalingam-Whyatt simplification](https://en.wikipedia.org/wiki/Visvalingam%E2%80%93Whyatt_algorithm). This calculates the area of each triangle
   formed by each triad of 3 contiguous vertices within the line. The vertex
   that creates the triangle with the smallest area is dropped. This process is
   repeated until there are no more vertices to drop, or the smallest area is
   greater than either 100 m2 or 1/100th of the area in the waterbody, whichever
   is smaller.
6. the simplified line is then further evaluated to find suitably straight sections.
   The angle of each contiguous triad of vertices (measured from the middle vertex of each triad)
   is calculated, and if within 180° +/- 10° that vertex is dropped. This
   process of dropping low angle vertices is repeated 5 times.
7. the result at this point is a fairly straight polyline (`LineString`).
8. the length of each segment within the polyline is calculated. Any segments
   that are greater than 30 meters and less than 45% of the total length of the
   waterbody boundary are retained. NOTE: these lengths are based on the significant
   vertices extracted above, not the original vertices of the boundary.
9. once the above segments are identified, a polyline is extracted for each based
   on the original vertices. That is, if the above approach identifies vertices
   1 and 8 as straight enough and long enough segments, this extracts all vertices
   1,2,3,4,5,6,7,8.
10. the extracted polylines are intersected with a 1 meter buffer around the
    drain point; only those that intersect are retained.
11. the position of the drain point is calculated on those polylines. The drain
    point must occur within the interior of those lines by at least 1 meter
    (meaning: not at the endpoints) in order for those polylines to be retained.
    This avoids extracting straight side edges of waterbodies that end at the
    drain point.

Note: this uses [numba](http://numba.pydata.org/) to speed up several of the
internal operations. You will need to install numba in order to run this script.
