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
        collected = {node}  # per root node
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
def descendants2(adj_matrix, root_ids):
    # like the above, but with a global "seen" set
    out = []
    seen = set()
    for i in range(len(root_ids)):
        node = root_ids[i]

        if node in seen:
            print(f"already seen node: {node}")

        collected = {node}  # per root node
        seen.add(node)
        if node in adj_matrix:
            next_nodes = set(adj_matrix[node])
            while next_nodes:
                nodes = next_nodes
                next_nodes = set()
                for next_node in nodes:
                    if not next_node in seen:
                        seen.add(next_node)
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


@njit
def _is_reachable_pair(adj_matrix, source_node, target_node, max_depth):
    """Return True for which there exists a route within the adjacency matrix
    between source_node and target_node that is less than max_depth.

    Parameters
    ----------
    adj_matrix : dict of numba lists
        adjacency list created from above function
    source_node : int
        source node ID
    target_node : int
        target node ID
    max_depth : int
        number of vertices to traverse searching for route from source to target nodes

    Returns
    -------
    bool
        True if there is a route from source_node to target_node
    """
    depth = 0
    seen = set()
    next_nodes = set(adj_matrix[source_node])

    # breadth-first traversal up to max_depth
    while next_nodes and depth <= max_depth:
        depth += 1
        nodes = next_nodes
        next_nodes = set()
        for next_node in nodes:
            if next_node == target_node:
                return True

            if not next_node in seen:
                seen.add(next_node)
                if next_node in adj_matrix:
                    next_nodes.update(adj_matrix[next_node])

    return False


@njit
def is_reachable(adj_matrix, sources, targets, max_depth=None):
    """Return True for each pair in sources and targets for which there exists a
    route within the adjacency matrix.

    Parameters
    ----------
    adj_matrix : dict of numba lists
        adjacency list created from above function
    sources : 1d ndarray of source nodes
    targets : 1d array of target nodes
        must be same length as source
    max_depth : int, optional (default: None)
        If set, will be the maximum number of descendants of each source
        to search for a route to any of targets.  By default will search
        through all nodes in graph.

    Returns
    -------
    ndarray (bool)
    """

    if not len(sources) == len(targets):
        raise ValueError("sources and targets must be same length")

    max_depth = max_depth or len(adj_matrix)

    out = np.zeros(shape=sources.shape, dtype="bool")
    for i in range(len(sources)):
        out[i] = sources[i] in adj_matrix and _is_reachable_pair(
            adj_matrix, sources[i], targets[i], max_depth
        )

    return out


@njit
def find_loops(adj_matrix, sources, max_depth=None):
    """Find loops in the network.

    Uses a depth-first search to create a list of loops that join to nodes
    already seen during traversal.

    Parameters
    ----------
    adj_matrix : dict, adjacency matrix
    adj_matrix : dict of numba lists
        adjacency list created from above function
    max_depth : int, optional (default: None)
        If set, will be the maximum number of descendants of each source
        to search for a route to any of targets.  By default will search
        through all nodes in graph.

    Returns
    -------
    set of nodes that are loops
    """
    if max_depth is None:
        max_depth = len(adj_matrix)

    seen = set()
    loops = set()
    for start_node in sources:
        depth = 0
        stack = [start_node]
        prev_node = start_node
        while len(stack):
            depth += 1
            if depth >= max_depth:
                break

            node = stack.pop()
            if node in seen:
                loops.add(prev_node)
            else:
                seen.add(node)
                if node in adj_matrix:
                    stack.extend(adj_matrix[node][::-1])

            prev_node = node

    return loops


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

    def is_reachable(self, sources, targets, max_depth=None):
        return is_reachable(self.adj_matrix, sources, targets, max_depth)

    def find_loops(self, sources, max_depth=None):
        return find_loops(self.adj_matrix, sources, max_depth)
