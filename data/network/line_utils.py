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

