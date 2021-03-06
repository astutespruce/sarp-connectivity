import json
import geopandas as gp
import pandas as pd

units = {
    "HUC6": {"filename": "HUC6"},
    "HUC8": {"filename": "HUC8"},
    "HUC12": {"filename": "HUC12"},
    "ECO3": {"filename": "SARP_ecoregion3", "id": "NA_L3CODE", "name": "NA_L3NAME"},
    "ECO4": {"filename": "SARP_ecoregion4", "id": "US_L4CODE", "name": "US_L4NAME"},
}


state_df = (
    gp.read_file("data/src/states.shp")
    .rename(columns={"NAME": "name", "GEOID": "id"})
    .to_crs(epsg="4326")
)

# create a copy for spatial join
states = state_df[["id", "geometry"]].rename(columns={"id": "state"})
states.sindex

county_df = (
    gp.read_file("data/src/counties.shp")
    .rename(columns={"GEOID": "id", "NAME": "name", "STATEFP": "state"})
    .to_crs(epsg="4326")
)

state_df["bbox"] = state_df.geometry.apply(lambda g: [round(x, 1) for x in g.bounds])
county_df["bbox"] = county_df.geometry.apply(lambda g: [round(x, 2) for x in g.bounds])

out = {
    "State": state_df[["id", "bbox"]].to_dict(
        orient="records"
    ),  # Name will be joined in on frontend
    "County": county_df[["id", "name", "state", "bbox"]].to_dict(orient="records"),
}


for unit in units:
    print("Extracting {}".format(unit))
    props = units[unit]

    filename = "data/src/{}.shp".format(units[unit]["filename"])
    col_map = {"NAME": "name"}
    col_map[props.get("id", unit)] = "id"
    col_map[props.get("name", "NAME")] = "name"
    df = gp.read_file(filename).rename(columns=col_map).set_index("id", drop=False)

    if not ("init" in df.crs and df.crs["init"] == "epsg:4326"):
        print("projecting to WGS84")
        df = df.to_crs(epsg="4326")

    # Ecoregions have multipart features and need to be dissolved to extract proper bounding boxes and spatial joins
    if unit.startswith("ECO"):
        print("Dissolving features...")
        df["dissolve_id"] = df.id
        df = df.dissolve(by="dissolve_id")

    df.sindex

    # do a spatial join of the unit against states to get list of FIPS codes per unit
    print("Spatial join against states...")
    unit_states = (
        gp.sjoin(df[["id", "geometry"]], states)
        .groupby("id")["state"]
        .apply(list)
        .reset_index()
        .set_index("id")
    )
    df = df.join(unit_states)
    df["state"] = df.state.fillna("").apply(lambda x: ",".join(x))

    # extract bounding box and round to 1-2 decimals.  Good enough for approximate zoom of map.
    precision = 2 if unit == "HUC12" else 2
    df["bbox"] = df.geometry.apply(lambda g: [round(x, precision) for x in g.bounds])

    out[unit] = df[["id", "name", "state", "bbox"]].to_dict(orient="records")

with open("data/derived/unit_bounds.json", "w") as outfile:
    outfile.write(json.dumps(out))
