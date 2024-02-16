from pathlib import Path

import pandas as pd
from pyogrio import read_dataframe

from analysis.lib.geometry import dissolve


src_dir = Path("data/tnc_resilience")

# df = read_dataframe(
#     src_dir / "TNC_Freshwater_Resilience_Nov2023.gdb",
#     layer="Scored_Units_HUC12FCN_Ver20230928_resultfields",
#     read_geometry=False,
#     columns=["HUC12", "Resil_Cl"],
#     use_arrow=True,
# ).rename(columns={"Resil_Cl": "resilience"})

df = read_dataframe(
    src_dir / "TNC_Freshwater_Resilience_Nov2023.gdb",
    layer="Scored_Units_HUC12FCN_Ver20230928_resultfields",
    columns=["HUC12", "Resil_Cl"],
    use_arrow=True,
).rename(columns={"Resil_Cl": "resilience"})

df = dissolve(df.explode(ignore_index=True), by="resilience").explode(ignore_index=True)
dissolved = df


id = "041402011606"
