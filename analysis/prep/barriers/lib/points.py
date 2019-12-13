import geopandas as gp
import pandas as pd
import numpy as np
import networkx as nx

from nhdnet.geometry.points import find_nearby

from analysis.util import flatten_series


def find_neighborhoods(df, distance=100):
    nearby = find_nearby(df, distance)

    # Find all nodes that are neighbors of each other
    # WARNING: not all neighbors within a neighborhood are within distance of each other
    network = nx.from_pandas_edgelist(nearby.reset_index(), "index", "index_right")
    components = pd.Series(nx.connected_components(network)).apply(list)
    return (
        pd.DataFrame(components.explode().rename("index_right").reset_index(drop=True))
        .reset_index()
        .rename(columns={"index": "group", "index_right": "index"})
        .set_index("index")
    )
