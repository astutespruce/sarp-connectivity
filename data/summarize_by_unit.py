from collections import defaultdict
import csv
import json
import pandas as pd
import geopandas as gp


# TODO: derive other HUCs from HUC12 if they don't already exist
df = pd.read_csv(
    "data/src/sarp_dams.csv",
    dtype={"HUC12": str, "HUC8": str, "HUC4": str, "Ecoregion3": str},
)

# Lookup state domain codes to state names
states = pd.read_csv("data/src/state_domain.csv").set_index(["State"])
df = df.join(states, on=("State"))
df = df.drop("State", axis=1).rename(columns={"StateName": "states"})

# Calculate any HUC codes that are missing
# TODO: fix missing HUC12s, for now, just filter them out
df = df[df["HUC12"].notnull()].copy()

cols = set(df.columns)
if "HUC2" not in cols:
    df["HUC2"] = df.apply(lambda row: row["HUC12"][:2], axis=1)
# if 'HUC4' not in cols:
# HUC4 had issues, make it right
df["HUC4"] = df.apply(lambda row: row["HUC12"][:4], axis=1)
# if 'HUC8' not in cols:
#     df['HUC8'] = df.apply(lambda row: row['HUC12'][:8], axis=1)

df["Ecoregion1"] = df.apply(
    lambda row: row["Ecoregion3"].split(".")[0]
    if not pd.isnull(row["Ecoregion3"])
    else "",
    axis=1,
)
df["Ecoregion2"] = df.apply(
    lambda row: row["Ecoregion3"][: row["Ecoregion3"].rindex(".")]
    if not pd.isnull(row["Ecoregion3"])
    else "",
    axis=1,
)


stats = defaultdict(defaultdict)
cols = ["dams", "connectedmiles"]

geo_join_lut = {
    "states": "NAME",
    "HUC2": "HUC2",
    "HUC4": "HUC4",
    "HUC8": "HUC8",
    "Ecoregion1": "NA_L1CODE",
    "Ecoregion2": "NA_L2CODE",
    "Ecoregion3": "NA_L3CODE",
    "Ecoregion4": "L4_KEY",
}

# Group by state, HUC level, ecoregion level
for unit in (
    "states",
    "HUC2",
    "HUC4",
    "HUC8",
    "Ecoregion1",
    "Ecoregion2",
    "Ecoregion3",
    "Ecoregion4",
):
    group_cols = [unit]
    if unit == "HUC4":
        group_cols.append("HUC2")
    elif unit == "HUC8":
        group_cols.extend(["HUC4", "HUC2"])
    elif unit == "Ecoregion2":
        group_cols.append("Ecoregion1")
    elif unit == "Ecoregion3":
        group_cols.extend(["Ecoregion2", "Ecoregion1"])
    elif unit == "Ecoregion4":
        group_cols.extend(["Ecoregion3", "Ecoregion2", "Ecoregion1"])

    g = df.groupby(group_cols).agg(
        {"UniqueID": {"dams": "count"}, "AbsoluteGainMi": {"connectedmiles": "mean"}}
    )

    index_cols = [geo_join_lut[unit]] + group_cols[1:]
    g.to_csv(
        "data/summary/{}.csv".format(unit),
        header=["dams", "connectedmiles"],
        index_label=[geo_join_lut[c] for c in group_cols],
        quoting=csv.QUOTE_NONNUMERIC,
    )

    level_stats = g.agg(["min", "max"])
    level_stats.columns = cols
    for col in cols:
        stats[unit][col] = level_stats[col].tolist()


with open("ui/src/data/summary_stats.json", "w") as outfile:
    outfile.write(json.dumps(stats))


# state_df = gp.read_file(
#     "data/src/SARP_Bounds.gdb", layer="SARP_Sates_PR_Albers83"
# ).set_index(["STATE"])
# state_df = state_df[~state_df.index.isin(["Puerto Rico", "U.S. Virgin Islands"])]


# # group_cols = ['State', 'HUC8', 'HUC4', 'HUC12', 'StateName']
# group_cols = ["NA_L3CODE"]  # ['Ecoregion', 'HUC4', 'State']
# data_cols = [
#     "AbsoluteGainMi",
#     "UpstreamMiles",
#     "DownstreamMiles",
#     "TotalNetworkMiles",
#     "PctNatFloodplain",
#     "NetworkSinuosity",
#     "NumSizeClassGained",
# ]
# stats = ["min", "median", "max"]

# agg = {col: {"{}_{}".format(col, stat): stat for stat in stats} for col in data_cols}
# agg["AbsoluteGainMi"]["NumDams"] = "count"


# import matplotlib
# matplotlib.use("Agg")

# for group_col in group_cols:
#     print("Grouping by {}".format(group_col))
#     g = df.groupby(group_col)[data_cols].agg(agg)
#     print("Size of join {}".format(len(g)))
#     g.to_csv("{}_summary.csv".format(group_col))

#     edgecolor = None
#     on = None

#     if group_col == "State":
#         geo_df = state_df
#         edgecolor = "#AAAAAA"

#     elif group_col == "HUC4":
#         # TODO: this is in SARP_Bounds.gdb
#         geo_df = gp.read_file("/users/bcward/Documents/SARP/HUC8.shp").rename(
#             columns={"HUC_8": "HUC8"}
#         )
#         geo_df["HUC4"] = geo_df.apply(lambda row: row.HUC8[:4], axis=1)
#         on = group_col

#     elif group_col == "NA_L3CODE":
#         geo_df = gp.read_file(
#             "src/us_eco_l3.shp"
#         )  # .rename(columns={'NA_L3NAME': 'Ecoregion'})
#         on = group_col

#     geo_df = geo_df.join(g, on=on, how="inner")

#     for col in data_cols:
#         print("Plotting {}".format(col))
#         stat = "{}_max".format(col)
#         base = geo_df[geo_df[stat].notnull()].plot(
#             column=stat, cmap="OrRd", legend=True
#         )
#         p = state_df.plot(ax=base, facecolor="none", edgecolor="#AAAAAA", linewidth=0.5)
#         p.set_axis_off()
#         p.set_title(stat)
#         p.get_figure().savefig("{0}_{1}.png".format(group_col, stat))

#     base = geo_df.plot(
#         column="NumDams", cmap="OrRd", legend=True, edgecolor=edgecolor, linewidth=0.5
#     )
#     p = state_df.plot(ax=base, facecolor="none", edgecolor="#AAAAAA", linewidth=0.5)
#     p.set_axis_off()
#     p.set_title("Number of Dams")
#     p.get_figure().savefig("{0}_numdams.png".format(group_col))
