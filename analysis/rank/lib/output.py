from pathlib import Path
import csv


out_dir = Path("data/derived")

# Fields that must appear exactly this way to link to units in maps
UNIT_FIELDS = ["State", "County", "HUC6", "HUC8", "HUC12", "ECO3", "ECO4"]

METRIC_FIELDS = [
    "UpstreamMiles",
    "DownstreamMiles",
    # TODO: can gainmiles and totalnetworkmiles be calculated on frontend for display?
    "GainMiles",
    "TotalNetworkMiles",
    "Landcover",
]

# fields used to filter dams and small barriers
FILTER_FIELDS = [
    "SizeClasses",
    "StreamOrder",
    "GainMilesClass",
    "SinuosityClass",
    "LandcoverClass",
    "TESppClass",
    "StreamOrderClass",
]

# fields generic to both barrier types
BARRIER_FIELDS = ["HasNetwork", "lat", "lon", "Basin", "COUNTYFIPS"]

# fields specific to dams
DAM_FIELDS = [
    "SARPUniqueID",
    "NIDID",
    "Source",
    "Name",
    "Year",
    "River",
    "Height",
    "Feasibility",
    "Construction",
    "Condition",
    "Purpose",
]

DAM_FILTER_FIELDS = ["HeightClass"]

# fields specific to small barriers
SB_FIELDS = [
    "CrossingCode",
    "LocalID",
    "Source",
    "Stream",
    "Road",
    "RoadType",
    "CrossingType",
    "Condition",
    "PotentialProject",
]

SB_FILTER_FIELDS = [
    "ConditionClass",
    "SeverityClass",
    "CrossingTypeClass",
    "RoadTypeClass",
]


def to_tippecanoe(df, network_type):
    """Export data for tippecanoe.
    Creates a file for barriers with networks, and barriers without
    
    Parameters
    ----------
    df : DataFrame
    network_type : str
        dams or small_barriers
    """

    type_fields = (
        DAM_FIELDS + DAM_FILTER_FIELDS
        if network_type == "dams"
        else SB_FIELDS + SB_FILTER_FIELDS
    )

    tier_fields = [c for c in df.columns if c.endswith("_tier")]

    # Drop any fields we don't need to export
    keep_cols = (
        BARRIER_FIELDS
        + type_fields
        + UNIT_FIELDS
        + METRIC_FIELDS
        + FILTER_FIELDS
        + tier_fields
    )

    df = df[df.columns.intersection(keep_cols)].copy()

    # Rename columns for easier use
    df = df.rename(
        columns={
            "County": "CountyName",
            "COUNTYFIPS": "County",
            "SinuosityClass": "Sinuosity",  # Decoded to a label on frontend
        }
    )

    # create duplicate columns for those dropped by tippecanoe
    # tippecanoe will use these ones and leave lat / lon
    # so that we can use them for display in the frontend
    # TODO: can this be replaced with the actual geometry available to mapbox GL?
    df["latitude"] = df.lat
    df["longitude"] = df.lon

    # Split datasets based on those that have networks
    # This is done to control the size of the dam vector tiles, so that those without
    # networks are only used when zoomed in further.  Otherwise, the full vector tiles
    # get too large, and points that we want to display are dropped by tippecanoe.
    print("Writing {} with networks...".format(network_type))

    # lowercase all fields except those for unit IDs
    with_network = (
        df.loc[df.HasNetwork]
        .drop(columns=["HasNetwork"])
        .rename(columns={k: k.lower() for k in df.columns if k not in UNIT_FIELDS})
    )

    with_network.to_csv(
        out_dir / "{}_with_networks.csv".format(network_type),
        index_label="id",
        quoting=csv.QUOTE_NONNUMERIC,
    )

    # Drop columns we don't need from dams that have no networks, since we do not filter or display
    # these fields.
    print("Writing {} without networks...".format(network_type))

    keep_cols = BARRIER_FIELDS + type_fields + ["CountyName", "Basin"]
    without_network = (
        df.loc[~df.HasNetwork, df.columns.intersection(keep_cols)]
        .drop(columns=["HasNetwork"])
        .rename(columns={k: k.lower() for k in df.columns if k not in UNIT_FIELDS})
    )
    without_network.to_csv(
        out_dir / "{}_without_networks.csv".format(network_type),
        index_label="id",
        quoting=csv.QUOTE_NONNUMERIC,
    )
