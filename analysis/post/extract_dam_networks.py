from pathlib import Path

from geofeather.pygeos import from_geofeather
from pgpkg import to_gpkg
from nhdnet.io import deserialize_dfs

from analysis.constants import REGION_GROUPS, CRS_WKT

data_dir = Path("data")
networks_dir = data_dir / "networks"

df = deserialize_dfs(
    [
        networks_dir / region / "dams/barriers_network.feather"
        for region in REGION_GROUPS
    ],
)

networkIDs = df.loc[df.kind == "dam"].upNetID.unique()

for region in list(REGION_GROUPS.keys()):
    print("\n----------------\n processing {}".format(region))

    networks = from_geofeather(networks_dir / region / "dams" / "network.feather")

    # Extract only the networks associated with small barriers, the rest are dams
    networks = networks.loc[
        networks.networkID.isin(networkIDs), ["networkID", "geometry"]
    ]

    if len(networks) == 0:
        print("No small barriers in this region, skipping")
        continue

    print("Writing to GPKG")
    to_gpkg(
        networks.reset_index(drop=True),
        data_dir / "tiles" / "dam_networks{}".format(region),
        index=False,
        name="networks",
        crs=CRS_WKT,
    )


### Region 21 is a special case
region = "21"
print("\n----------------\n processing {}".format(region))
df = from_geofeather(networks_dir / region / "dams" / "barriers.feather")
networkIDs = df.upNetID.unique()

networks = from_geofeather(networks_dir / region / "dams" / "network.feather")
networks = networks.loc[networks.networkID.isin(networkIDs)]

print("Writing to GPKG")
to_gpkg(
    networks[['networkID']].reset_index(drop=True),
    data_dir / "tiles" / "dam_networks{}".format(region),
    index=False,
    name="networks",
    crs=CRS_WKT,
)
