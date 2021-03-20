import pandas as pd


def find_adjacent_groups(left, right):
    """Find groups of adjacent nodes between left and right.  Assumes that
    left and right have symmetric pairs (e.g., result of spatial self-join).

    Adapted from networkx::connected_components

    Parameters
    ----------
    left : ndarray of indexes
    right : ndarray of indexes
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

    adj_matrix = (
        pd.DataFrame({"left": left, "right": right})
        .groupby("left")
        .right.apply(set)
        .to_dict()
    )

    # TODO: update this to use faster method if we know that pairs are always unique
    # e.g., flowline joins

    groups = []
    seen = set()
    for node in adj_matrix.keys():
        if not node in seen:
            adj_nodes = _all_adj(adj_matrix, node)
            seen.update(adj_nodes)
            groups.append(adj_nodes)

    return groups
