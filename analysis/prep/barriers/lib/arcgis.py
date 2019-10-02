from math import ceil

import requests
from requests import HTTPError
import pandas as pd
import geopandas as gp
from shapely.geometry import Point

# Mapping of ESRI WKID to proj4 strings
CRS_LUT = {
    # Same as EPSG:3857
    102100: "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs",
    # same as EPSG:102003
    'PROJCS["Albers",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Albers"],PARAMETER["false_easting",0.0],PARAMETER["false_northing",0.0],PARAMETER["central_meridian",-96.0],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["latitude_of_origin",37.5],UNIT["Meter",1.0]]': "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs",
}


def getJSON(url, params=None, token=None, **kwargs):
    """Make JSON request, wrapped in exception handling
    
    Parameters
    ----------
    url : str
    token: str (optional)
    
    Raises
    ------
    HTTPError
        Raises error when returned as error by service
    """

    if params is None:
        params = {}

    response = requests.get(
        url, params={**params, "f": "json", "token": token}, **kwargs
    ).json()
    if "error" in response:
        raise HTTPError(
            "Error making request: {}\n{}".format(
                response["error"]["message"], response["error"]["details"]
            )
        )

    return response


def list_services(url, token=None):
    """Given a root ArcGIS server / ArcGIS Online services endpoint, return the list of services.
    
    Parameters
    ----------
    url : str
        services endpoint
    token : str, optional
        token, if required to access secured services
    
    Returns
    -------
    list
        contains {'name': <>, 'type': <>, 'url': <>} for each service
    """

    return getJSON(url, params={"f": "json", "token": token})["services"]


def download_fs(url, fields=None, token=None):
    """Download an ESRI FeatureService JSON to GeoDataFrame.

    Parameters
    ----------
    fs_data : dict
        Dict created from FeatureService JSON

    """

    # Get the total count we can query
    svc_info = getJSON(url, token=token)
    batch_size = max(svc_info["maxRecordCount"], svc_info["standardMaxRecordCount"])

    query = {"where": "1=1", "resultType": "standard", "outFields": "*"}

    # ArcGIS will return an error if you request fields that are not present, so we have to
    # make sure to request only those that are present
    if fields:
        fields_present = [f["name"] for f in svc_info["fields"]]
        request_fields = set(fields).intersection(fields_present)

        missing_fields = set(fields).difference(fields_present)
        if len(missing_fields):
            print("Requested fields are not present: {}".format(missing_fields))

        query["outFields"] = ",".join(request_fields)

    # Get total count we expect
    count = getJSON(
        "{}/query".format(url),
        params={"where": "1=1", "returnCountOnly": "true"},
        token=token,
    )["count"]

    batches = ceil(count / batch_size)
    print("Downloading {:,} records in {:,} requests".format(count, batches))

    # Download and merge data frames
    merged = None
    for offset in range(0, batches * batch_size, batch_size):
        query["resultOffset"] = offset
        response = getJSON("{}/query".format(url), params=query, token=token)

        df = fs_json_to_gdf(response)

        if merged is None:
            merged = df
        else:
            merged = merged.append(df, ignore_index=True, sort=False)

    return merged


def fs_json_to_gdf(fs_json):
    """Convert ArcGIS Feature Service JSON response to geopandas GeoDataFrame.

    Note: only points are supported at this time.
    
    Parameters
    ----------
    fs_json : dict
        JSON response from ESRI feature service layer query
    
    Returns
    -------
    geopandas.GeoDataFrame
    """

    # Convert feature array to a DataFrame
    temp = pd.DataFrame(fs_json["features"])

    # Drop bad geometries
    temp = temp.loc[temp.geometry.notnull()].copy()

    # Extract attributes into a new DataFrame
    # Each attribute is a columm
    atts = temp.attributes.apply(pd.Series)

    # Process geometry to appropriate type
    # SHORTCUT: we only deal in points here
    xy = temp.geometry.apply(pd.Series)
    points = xy.apply(list, axis=1).apply(Point)

    srs_json = fs_json["spatialReference"]
    spatial_ref = srs_json.get("wkid", srs_json.get("wkt"))
    if not spatial_ref in CRS_LUT:
        raise ValueError("Unsupported CRS: {}".format(spatial_ref))

    crs = CRS_LUT[spatial_ref]

    return gp.GeoDataFrame(atts, geometry=points, crs=crs)
