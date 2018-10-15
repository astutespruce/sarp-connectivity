import geopandas as gp

# Note: many of the units have multiple polygons, so we need to group by their ID before extracting centroid
units = (
    "states",
    "HUC2",
    "HUC4",
    "HUC8",
    "ecoregion1",
    "ecoregion2",
    "ecoregion3",
    "ecoregion4",
)  # TODO: 'HUC8',

field_lut = {
    "states": "NAME",
    "HUC2": "HUC2",
    "HUC4": "HUC4",
    "HUC8": "HUC8",
    "ecoregion1": "NA_L1CODE",
    "ecoregion2": "NA_L2CODE",
    "ecoregion3": "NA_L3CODE",
    "ecoregion4": "L4_KEY",
}


for unit in units:
    field = field_lut[unit]
    print("Extracting centroids from {}".format(unit))
    filename = "data/src/sarp_{}.shp".format(unit)

    df = gp.read_file(filename)
    df["bnd"] = df.apply(lambda row: row.geometry.envelope, axis=1)

    # Make sure that bounds are in WGS84
    df = (
        df.set_geometry("bnd")[[field, "bnd"]]
        .dissolve(by=field)
        .to_crs({"init": "EPSG:4326"})
    )
    df["center"] = df.apply(lambda row: row.bnd.centroid, axis=1)
    df["x"] = df.apply(lambda row: row.center.x, axis=1)
    df["y"] = df.apply(lambda row: row.center.y, axis=1)

    df[["x", "y"]].to_csv(
        "data/src/sarp_{}_centroids.csv".format(unit), header=True, index_label=field
    )
