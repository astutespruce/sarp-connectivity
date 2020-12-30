import pandas as pd


def connected_groups(pairs, make_symmetric=False):
    """Find all connected pairs and use these to create groups.

    Note: isolated nodes must be handled separately.

    Adapted from networkx::connected_components

    Parameters
    ----------
    pairs : DataFrame of [left series, right series]
    make_symmetric : bool, optional (default: False)
        if False, pairs must be symmetric (typically true from spatial self-joins).
        If True, pairs will be made symmetric by adding their inverse.

    Returns
    -------
    Series
        indexed on values of left and right side of pairs, contains groups.
    """

    def _all_adj(adj_matrix, node):
        """Traverse adjacency matrix to find all connected notes for a given
        starting node.

        Parameters
        ----------
        node : number or string
            Starting node from which to find all adjacent nodes

        Returns
        -------
        set of adjacent nodes
        """
        out = set()
        next_nodes = {node}
        while next_nodes:
            nodes = next_nodes
            next_nodes = set()
            for node in nodes:
                if not node in out:
                    out.add(node)
                    next_nodes.update(adj_matrix[node])
        return out

    left_name, right_name = pairs.columns

    if make_symmetric:
        pairs = pairs.append(
            pairs.rename(columns={left_name: right_name, right_name: left_name}),
            sort=False,
            ignore_index=True,
        )

    # construct adjacency matrix (as a dict) from left to right
    adj_matrix = pairs.groupby(left_name)[right_name].apply(set).to_dict()

    groups = []
    seen = set()
    for node in adj_matrix.keys():
        if not node in seen:
            adj_nodes = _all_adj(adj_matrix, node)
            seen.update(adj_nodes)
            groups.append(adj_nodes)

    if not len(groups):
        groups = pd.Series([], dtype="uint32", name="group")
        groups.index.name = left_name
        return groups

    groups = pd.DataFrame(pd.Series(groups).apply(list).explode().rename("next_index"))
    groups.index.name = "group"
    groups = groups.reset_index().set_index("next_index")
    groups.index.name = left_name

    return groups.group
