import pandas as pd
from shapely.geometry import Point, LineString, MultiLineString


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


def cut_line(line, point):
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


def snap_to_line(
    points, lines, tolerance=100, prefer_endpoints=False, line_columns=None
):
    def snap(record):
        point = record.geometry
        x, y = point.coords[0]

        # Search window
        window = (x - tolerance, y - tolerance, x + tolerance, y + tolerance)

        # find nearby features
        hits = lines.loc[sindex.intersection(window)].copy()
        # hits = get_line_by_window(window)

        # calculate distance to point and
        hits["dist"] = hits.distance(point)
        within_tolerance = hits[hits.dist <= tolerance]

        if len(within_tolerance):
            # find nearest line segment that is within tolerance
            closest = within_tolerance.nsmallest(1, columns=["dist"])

            # calculate the snapped coordinate as a point on the nearest line
            closest["snapped"] = closest.geometry.apply(
                lambda g: g.interpolate(g.project(point))
            )

            # TODO: if prefer_endpoints

            # Select first record
            closest = closest.iloc[0]

            columns = ["snap_x", "snap_y", "snap_dist", "nearby"]
            values = [
                closest.snapped.x,
                closest.snapped.y,
                closest.dist,
                len(within_tolerance),
            ]

            # Copy attributes from line to point
            if line_columns:
                columns.extend(line_columns)
                values.extend([closest[c] for c in line_columns])

            return pd.Series(values, index=columns)

    print("creating spatial index on lines")
    sindex = lines.sindex

    # TODO: make into a partial function

    print("snapping {} points".format(len(points)))

    return points.apply(snap, axis=1)

    # for idx, record in points.iterrows():

    # print("out\n", out, "---------------------------------")

    # return out
