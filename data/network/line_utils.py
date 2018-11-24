import pandas as pd
import geopandas as gp
import numpy as np
from shapely.geometry import Point, LineString, MultiLineString
import rtree

# if points are within this distance of start or end coordinate, nothing is cut
EPS = 1e-6


def create_points(df, x_column, y_column, crs):
    """Create a GeoDataFrame from pandas DataFrame
    
    Parameters
    ----------
    df : pandas DataFrame
    x_column : str
        column containing x values
    y_colummn : str
        column containing y values
    crs : geopandas CRS object
        CRS of points
    
    Returns
    -------
    geopandas.GeoDataFrame
    """

    geometry = [Point(xy) for xy in zip(df[x_column], df[y_column])]
    return gp.GeoDataFrame(df, geometry=geometry, crs=crs)


def to2D(geometry):
    """Flatten a 3D line to 2D.
    
    Parameters
    ----------
    geometry : LineString or MultiLineString
        Input 3D geometry
    
    Returns
    -------
    LineString or MultiLineString
        Output 2D geometry
    """

    if geometry.type == "MultiLineString":
        return MultiLineString([LineString(c[:2] for c in g.coords) for g in geometry])
    return LineString(c[:2] for c in geometry.coords)


def calculate_sinuosity(geometry):
    """Calculate sinuosity of the line.

    This is the length of the line divided by the distance between the endpoints of the line.
    By definition, it is always >=1.

    If input is MultiLineString, a length-weighted sum is returned.
    
    Parameters
    ----------
    geometry : LineString or MultiLineString
    
    Returns
    -------
    float
        sinuosity value
    """

    if geometry.type == "MultiLineString":
        total_length = 0
        results = []
        for line in geometry:
            length = line.length
            total_length += length
            straight_line_distance = Point(line.coords[0]).distance(
                Point(line.coords[-1])
            )

            if straight_line_distance > 0:
                sinuosity = length / straight_line_distance
                results.append((length, sinuosity))

        if total_length == 0:
            return 1

        # return weighted sum
        return max(
            sum([(length / total_length) * sinuosity for length, sinuosity in results]),
            1,
        )

    # By definition, sinuosity should not be less than 1
    line = geometry
    straight_line_distance = Point(line.coords[0]).distance(Point(line.coords[-1]))
    if straight_line_distance > 0:
        return max(line.length / straight_line_distance, 1)

    return 1  # if there is no straight line distance, there is no sinuosity


def snap_to_line(lines, tolerance=100, prefer_endpoint=False):
    """
    Attempt to snap a line to the nearest line, within tolerance distance.

    Lines must be in a planar (not geographic) projection and points 
    must be in the same projection.

    Parameters
    ----------
    points : GeoPandas.DataFrame
        points to snap
    lines : GeoPandas.DataFrame
        lines to snap against 
    tolerance : int, optional (default: 100)
        maximum distance between line and point that can still be snapped
    prefer_endpoint : bool, optional (default False)
        if True, will try to match to the nearest endpoint on the nearest line
        provided that the distance to that endpoint is less than tolerance

    Returns
    -------
    geopandas.GeoDataFrame
        output data frame containing: 
        * geometry: snapped geometry
        * snap_dist: distance between original point and snapped location
        * nearby: number of nearby lines within tolerance
        * is_endpoint: True if successfully snapped to endpoint
        * any columns joined from lines
    """

    line_columns = list(set(lines.columns).difference({"geometry"}))

    def snap(record):
        point = record.geometry
        x, y = point.coords[0][:2]

        # Search window
        window = (x - tolerance, y - tolerance, x + tolerance, y + tolerance)

        # find nearby features
        hits = lines.iloc[list(sindex.intersection(window))].copy()

        # calculate distance to point and
        hits["dist"] = hits.distance(point)
        within_tolerance = hits[hits.dist <= tolerance]

        if len(within_tolerance):
            # find nearest line segment that is within tolerance
            closest = within_tolerance.nsmallest(1, columns=["dist"]).iloc[0]
            line = closest.geometry

            dist = closest.dist
            snapped = None
            is_endpoint = False
            if prefer_endpoint:
                # snap to the nearest endpoint if it is within tolerance
                endpoints = [
                    (pt, point.distance(pt))
                    for pt in (Point(line.coords[0]), Point(line.coords[-1]))
                    if point.distance(pt) < tolerance
                ]
                endpoints = sorted(endpoints, key=lambda x: x[1])
                if endpoints:
                    snapped, dist = endpoints[0]
                    is_endpoint = True

            if snapped is None:
                snapped = line.interpolate(line.project(point))

            columns = ["geometry", "snap_dist", "nearby", "is_endpoint"]
            values = [snapped, dist, len(within_tolerance), is_endpoint]

            # Copy attributes from line to point
            columns.extend(line_columns)
            values.extend([closest[c] for c in line_columns])

            return gp.GeoSeries(values, index=columns)

    print("creating spatial index on lines")
    sindex = lines.sindex
    # Note: the spatial index is ALWAYS based on the integer index of the
    # geometries and NOT their index

    # we are calling this as a curried function, so we return the func
    # for the apply()
    return snap


def cut_line_at_point(line, point):
    """
    Cut line at a point on the line.
    modified from: https://shapely.readthedocs.io/en/stable/manual.html#splitting

    Parameters
    ----------
    line : shapely.LineString
    point : shapely.Point
    
    Returns
    -------
    list of LineStrings
    """

    distance = line.project(point)
    if distance <= 0.0 or distance >= line.length:
        return [LineString(line)]

    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [LineString(coords[: i + 1]), LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:]),
            ]


def cut_line_at_points(line, points):
    """
    Cut a line geometry by multiple points.
    
    Parameters
    ----------
    line : shapely.LineString
    points : iterable of shapely.Point objects.  
        Must be ordered from the start of the line to the end.
       
    
    Returns
    -------
    list of shapely.LineString containing new segments
    """

    segments = []
    remainder = line

    for point in points:
        segment, remainder = cut_line_at_point(remainder, point)
        segments.append(segment)

    segments.append(remainder)

    return segments


def cut_flowlines(flowlines, barriers, joins):
    print("Starting number of segments: {}".format(len(flowlines)))
    print("Cutting in {0} barriers".format(len(barriers)))

    # Our segment ids are ints, so just increment from the last one we had from NHD
    next_segment_id = int(flowlines.index.max() + 1)

    update_cols = ["length", "sinuosity", "geometry", "lineID"]
    copy_cols = list(set(flowlines.columns).difference(update_cols))
    columns = copy_cols + update_cols

    # create container for new geoms
    new_flowlines = gp.GeoDataFrame(
        columns=flowlines.columns, crs=flowlines.crs, geometry="geometry"
    )

    updated_joins = joins.copy()

    # create join table for barriers
    barrier_joins = []

    segments_with_barriers = flowlines.loc[flowlines.index.isin(barriers.lineID)]
    print("{} segments have at least one barrier".format(len(segments_with_barriers)))
    for idx, row in segments_with_barriers.iterrows():
        # print("-----------------------\n\nlineID", idx)

        # Find upstream and downstream segments
        upstream_ids = joins.loc[joins.downstream_id == idx]
        downstream_ids = joins.loc[joins.upstream_id == idx]

        # Barriers on this line
        points = barriers.loc[barriers.lineID == idx].copy()

        # ordinate the barriers by their projected distance on the line
        # Order this so we are always moving from upstream end to downstream end
        line = row.geometry
        length = line.length
        points["linepos"] = points.geometry.apply(lambda p: line.project(p))
        points.sort_values("linepos", inplace=True, ascending=True)

        # by definition, splits must occur after the first coordinate in the line and before the last coordinate
        split_points = points.loc[
            (points.linepos > EPS) & (points.linepos < (length - EPS))
        ]

        segments = []
        if len(split_points):
            lines = cut_line_at_points(line, split_points.geometry)
            num_segments = len(lines)
            ids = list(range(next_segment_id, next_segment_id + num_segments))
            next_segment_id += num_segments

            # make id, segment pairs
            segments = list(zip(ids, lines))

            # add these to flowlines
            for i, (id, segment) in enumerate(segments):
                values = [row[c] for c in copy_cols] + [
                    segment.length,
                    calculate_sinuosity(segment),
                    segment,
                    id,
                ]
                new_flowlines.loc[id] = gp.GeoSeries(values, index=columns)

                if i < num_segments - 1:
                    # add a join for this barrier
                    barrier_joins.append(
                        {
                            "NHDPlusID": row.NHDPlusID,
                            "joinID": split_points.iloc[i].joinID,
                            "upstream_id": id,
                            "downstream_id": ids[i + 1],
                        }
                    )

            # update upstream nodes to set first segment as their new downstream
            # update downstream nodes to set last segment as their new upstream
            updated_joins.loc[upstream_ids.index, "downstream_id"] = ids[0]
            updated_joins.loc[downstream_ids.index, "upstream_id"] = ids[-1]

            # add joins for everything after first node
            new_joins = [
                {
                    "upstream_id": ids[i],
                    "downstream_id": id,
                    "upstream": np.nan,
                    "downstream": np.nan,
                }
                for i, id in enumerate(ids[1:])
            ]
            updated_joins = updated_joins.append(new_joins, ignore_index=True)

        # If barriers are at the downstream-most point or upstream-most point
        us_points = points.loc[points.linepos <= EPS]
        ds_points = points.loc[points.linepos >= (length - EPS)]

        # Handle any points on the upstream or downstream end of line
        if len(us_points):
            # Create a record for each that has downstream set to the first segment if any, or
            # NHDPlusID of this segment
            # Do this for every upstream segment (if there are multiple upstream nodes)
            downstream_id = segments[0][0] if segments else idx
            for _, barrier in us_points.iterrows():
                for uIdx, upstream in upstream_ids.iterrows():
                    barrier_joins.append(
                        {
                            "NHDPlusID": row.NHDPlusID,
                            "joinID": barrier.joinID,
                            "upstream_id": upstream.upstream_id,
                            "downstream_id": downstream_id,
                        }
                    )

        if len(ds_points):
            # Create a record for each that has upstream set to the last segment if any, or
            # NHDPlusID of this segment
            # Do this for every downstream segment (if there are multiple downstream nodes)
            upstream_id = segments[-1][0] if segments else idx
            for _, barrier in ds_points.iterrows():
                for _, downstream in downstream_ids.iterrows():
                    barrier_joins.append(
                        {
                            "NHDPlusID": row.NHDPlusID,
                            "joinID": barrier.joinID,
                            "upstream_id": upstream_id,
                            "downstream_id": downstream.downstream_id,
                        }
                    )

    # Drop all segments replaced by new segments
    flowlines = flowlines.drop(
        flowlines.loc[flowlines.NHDPlusID.isin(new_flowlines.NHDPlusID)].index
    )
    flowlines = flowlines.append(new_flowlines, sort=False)
    print("Final number of segments", len(flowlines))

    barrier_joins = pd.DataFrame(
        barrier_joins, columns=["NHDPlusID", "joinID", "upstream_id", "downstream_id"]
    )

    return flowlines, updated_joins, barrier_joins
