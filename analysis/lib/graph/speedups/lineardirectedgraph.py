from numba import types
from numba import njit
from numba.typed import Dict
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
