from pathlib import Path

import numpy as np
import pyarrow.compute as pc
from pyarrow.dataset import dataset


data_dir = Path("data")
src_dir = data_dir / "species/derived"


def get_diaadromous_ids():
    """Get an array of NHDPlusID values for every flowline associated with
    anadromous or diadromous species habitat

    Returns
    -------
    array
    """
    streamnet_anadromous = dataset(src_dir / "streamnet_habitat.feather", format="feather").to_table(
        columns=["NHDPlusID"],
        filter=pc.field("streamnet_anadromous_habitat") == True,  # noqa: E712
    )["NHDPlusID"]

    ca_anadromous = dataset(src_dir / "ca_baseline_fish_habitat.feather", format="feather").to_table(
        columns=["NHDPlusID"]
    )["NHDPlusID"]

    chesapeake_diadromous = dataset(
        src_dir / "chesapeake_diadromous_species_habitat.feather", format="feather"
    ).to_table(
        columns=["NHDPlusID"],
        filter=pc.field("chesapeake_diadromous_habitat") == True,  # noqa: E712
    )["NHDPlusID"]

    south_atlantic_anadromous = dataset(
        src_dir / "south_atlantic_anadromous_habitat.feather", format="feather"
    ).to_table(columns=["NHDPlusID"])["NHDPlusID"]

    anadromous_ids = np.unique(
        np.concat([streamnet_anadromous, ca_anadromous, chesapeake_diadromous, south_atlantic_anadromous])
    )

    return anadromous_ids
