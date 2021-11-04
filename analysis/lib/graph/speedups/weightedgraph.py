from heapq import heappush as push, heappop as pop

from numba import types
from numba import njit
from numba.typed import List, Dict
import numpy as np


@njit("(i8[:],f4[:])")
def make_length_dict(keys, lengths):
    out = dict()
    for i in range(len(keys)):
        out[keys[i]] = lengths[i]
    return out


@njit
def _dijkstra_route(adj_matrix, lengths, source_node, target_node, max_distance=None):
    """Find minimum path from source_node to target_node using Dijkstra's
    algorithm.

    Adapted from networkx::_dijkstra_multisource

    Parameters
    ----------
    adj_matrix : typed dict of int64 keys pointing to lists of int64 values
    lengths : typed dict of int64 keys pointing to float32 values
        each key in adj_matrix is expected to have a corresponding length
    source_node : int64
    target_node : int64
    max_distance : float32, optional (default: None)
        If present, the maximum distance to search for target_node.

    Returns
    -------
    (distance, [path])
        tuple of distance (float32) and typed list (int64) of nodes from
        source_node to target_node, including source_node and target_node.
        Returns (None, None) when no path can be found within the max_distance.
        NOTE: distances returned include the length from the start of one
        segment to the start of another; it DOES NOT include the length of the
        final segment itself.
    """
    dist = Dict.empty(types.int64, types.float32)
    seen = Dict.empty(types.int64, types.float32)
    paths = dict()

    seen[source_node] = np.float32(0.0)
    paths[source_node] = List([source_node])
    nodes_to_check = [(np.float32(0.0), source_node)]
    while nodes_to_check:
        dist_to_node, node = pop(nodes_to_check)
        if node in dist:
            continue  # already searched this node, skip it.

        dist[node] = dist_to_node

        if node == target_node:
            break

        if node not in adj_matrix:
            continue

        length = lengths[node]

        for next_node in adj_matrix[node]:
            cumulative_dist = dist_to_node + length

            if max_distance is not None and cumulative_dist > max_distance:
                continue

            if next_node in dist:
                continue  # already searched this node, skip it

            if next_node not in seen or cumulative_dist < seen[next_node]:
                seen[next_node] = cumulative_dist
                push(nodes_to_check, (cumulative_dist, next_node))
                path = paths[node].copy()
                path.append(next_node)
                paths[next_node] = path

    return dist.get(target_node, None), paths.get(target_node, None)

