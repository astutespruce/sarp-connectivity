from numba import njit, types
from numba.typed import Dict, List
import numpy as np


@njit("(i8[:],i8[:])", cache=True)
def make_adj_matrix(source, target):
    out = Dict.empty(key_type=types.int64, value_type=types.int64)
    for i in range(len(source)):
        out[source[i]] = target[i]

    return out


@njit(cache=True)
def descendants(adj_matrix, root_ids):
    out = []
    for i in range(len(root_ids)):
        node = root_ids[i]
        collected = set()  # per root node
        if node in adj_matrix:
            next_node = adj_matrix[node]
            while next_node is not None:
                collected.add(next_node)
                if next_node in adj_matrix:
                    next_node = adj_matrix[next_node]
                else:
                    break
        out.append(collected)
    return out


@njit(cache=True)
def network_pairs(adj_matrix, root_ids):
    pairs = []
    for i in range(len(root_ids)):
        node = root_ids[i]
        # add self
        pairs.append([node, node])

        if node in adj_matrix:
            next_node = adj_matrix[node]
            while next_node is not None:
                pairs.append([node, next_node])

                if next_node in adj_matrix:
                    next_node = adj_matrix[next_node]
                else:
                    break
    return np.asarray(pairs, dtype="int64")


@njit(cache=True)
def extract_paths(adj_matrix, start_ids, stop_ids, max_depth=100):
    """Extract the linear path from each node in start_ids up to the first
    node in stop_ids encountered, up to max_depth.  If there is no path within
    that limit, an empty list is returned for that start node.

    Parameters
    ----------
    adj_matrix : dict
    start_ids : array of int64 values
    stop_ids : array of int64 values
    max_depth : int, optional (default: 100)
        the maximum depth to traverse per start node

    Returns
    -------
    array of lists
        where each list is the node ids of contained in the path
        between each start node and the first stop node encountered
    """
    stop_ids = set(stop_ids)

    out = []
    for i in range(len(start_ids)):
        node = start_ids[i]
        collected = List.empty_list(types.int64)
        if node in adj_matrix:
            next_node = adj_matrix[node]
            depth = 0
            found_path = False
            while next_node is not None and depth < max_depth:
                collected.append(next_node)

                if next_node in stop_ids:
                    found_path = True
                    break

                if next_node in adj_matrix:
                    next_node = adj_matrix[next_node]
                else:
                    break
                depth += 1

            if not found_path:
                collected = List.empty_list(types.int64)

        out.append(collected)

    return out


class LinearDirectedGraph(object):
    def __init__(self, source, target):
        """Create LinearDirectedGraph from source and target ndarrays.

        A linear directed graph is one that has one and only one outgoing edge
        per incoming edge.

        source and target must be the same length

        Parameters
        ----------
        df : DataFrame,
        source : ndarray(int64)
        target : ndarray(int64)
        """

        self.adj_matrix = make_adj_matrix(source, target)
        self._size = len(self.adj_matrix)

    def __len__(self):
        return self._size

    def descendants(self, sources):
        return descendants(self.adj_matrix, sources)

    def network_pairs(self, sources):
        return network_pairs(self.adj_matrix, sources)

    def extract_paths(self, start_ids, stop_ids, max_depth=100):
        return extract_paths(self.adj_matrix, start_ids, stop_ids, max_depth=max_depth)
