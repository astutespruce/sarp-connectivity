from collections import defaultdict
from numba import types
from numba import njit
from numba.typed import List

import numpy as np


@njit("(i8[:],i8[:])")
def make_adj_matrix(source, target):
    # NOTE: drop dups first before calling this!
    out = dict()
    for i in range(len(source)):
        key = source[i]
        if key not in out:
            out[key] = List.empty_list(types.int64)
        out[key].append(target[i])
    return out


@njit
def descendants(adj_matrix, root_ids):
    out = []
    for i in range(len(root_ids)):
        node = root_ids[i]
        collected = set()  # per row
        if node in adj_matrix:
            next_nodes = set(adj_matrix[node])
            while next_nodes:
                nodes = next_nodes
                next_nodes = set()
                for next_node in nodes:
                    if not next_node in collected:
                        collected.add(next_node)
                        if next_node in adj_matrix:
                            next_nodes.update(adj_matrix[next_node])
        out.append(collected)
    return out


@njit
def components(adj_matrix):
    groups = []
    seen = set()
    for node in adj_matrix.keys():
        if not node in seen:
            # add current node with all descendants
            adj_nodes = {node} | descendants(adj_matrix, [node])[0]
            seen.update(adj_nodes)
            groups.append(adj_nodes)

    return groups


class DirectedGraph(object):
    def __init__(self, source, target):
        """Create DirectedGraph from source and target ndarrays.

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

    def components(self):
        return components(self.adj_matrix)

    def descendants(self, sources):
        return descendants(self.adj_matrix, sources)
