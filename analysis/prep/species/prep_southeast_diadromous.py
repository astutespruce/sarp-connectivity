from pathlib import Path

import geopandas as gp
import pyarrow as pa
import pyarrow.compute as pc
from pyogrio import read_dataframe, write_dataframe
import shapely

from analysis.constants import CRS
from analysis.lib.io import read_arrow_tables


data_dir = Path("data")
src_dir = data_dir / "species/source"
# must use raw data to be able to join on NHDPlusID later
nhd_dir = data_dir / "nhd/raw"
out_dir = data_dir / "species/derived"

infilename = src_dir / "SARP_Diadromous_V3.gdb"
layer = "Diadromous_Networks_V3_05192025"

# HUC2s that overlap SARP states
huc2s = ["02", "03", "05", "06", "07", "08", "10", "11", "12", "13"]

spp_names = {
    "Acipenser_destoi": "gulf_sturgeon_habitat",
    "Alosa_alabamae": "alabama_shad_habitat",
    "Alosa_sapidissima": "american_shad_habitat",
    # NOTE: ignore  Alligator gar per direction from SARP
    # "Atractosteus_spatula": "alligator_gar",
    "Anguilla_rostrata": "american_eel_habitat",
    "Alosa_chrysochloris": "skipjack_herring_habitat",
    "Alosa_aestivalis": "blueback_herring_habitat",
    "Alosa_pseudoharengus": "alewife_habitat",
    "Acipenser_oxyrinchus": "atlantic_sturgeon_habitat",
    "Morone_saxatilis": "striped_bass_habitat",
    "Acipenser_brevirostrum": "shortnose_sturgeon_habitat",
    "Alosa_mediocris": "hickory_shad_habitat",
}

df = (
    read_dataframe(infilename, layer=layer, columns=["NHDPlusID"] + list(spp_names.keys()), use_arrow=True)
    .rename(columns=spp_names)
    .explode(ignore_index=True)
)
df["NHDPlusID"] = df.NHDPlusID.astype("uint64")
df["length"] = shapely.length(df.geometry.values) / 1000

spp_cols = list(spp_names.values())
for col in spp_cols:
    df[col] = df[col].isin([1, 2, 3]).astype("bool")

df = df.loc[df[spp_cols].any(axis=1)].reset_index(drop=True)

df = df.groupby("NHDPlusID").agg({**{c: "max" for c in spp_cols}, "length": "sum"})
df["southeast_diadromous_habitat"] = True
spp_cols.append("southeast_diadromous_habitat")

flowlines = read_arrow_tables(
    [nhd_dir / huc2 / "flowlines.feather" for huc2 in huc2s],
    columns=[
        "geometry",
        "NHDPlusID",
    ],
    filter=pc.is_in(pc.field("NHDPlusID"), pa.array(df.index.values)),
    new_fields={"HUC2": huc2s},
)

flowlines = gp.GeoDataFrame(
    flowlines.select([c for c in flowlines.column_names if c not in {"geometry"}]).to_pandas(),
    geometry=shapely.from_wkb(flowlines.column("geometry")),
    crs=CRS,
).set_index("NHDPlusID")

flowlines = flowlines.join(df[spp_cols]).reset_index()


for col in spp_cols:
    print("\n------------------")
    print(
        f"{col} habitat: {df.loc[df[col], 'length'].sum():,.1f} km; "
        f"extracted {shapely.length(flowlines.loc[flowlines[col]].geometry.values).sum() / 1000:,.1f} km from NHD"
    )

    # DEBUG:
    write_dataframe(flowlines.loc[flowlines[col]], f"/tmp/{col}.fgb")

write_dataframe(flowlines, out_dir / "southeast_diadromous_habitat.fgb")
flowlines[["NHDPlusID", "HUC2"] + spp_cols].to_feather(out_dir / "southeast_diadromous_habitat.feather")
