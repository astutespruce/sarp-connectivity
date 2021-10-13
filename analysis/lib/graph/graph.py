import pandas as pd
import numpy as np


# DEPRECATED: replace with below DirectedGraph::components
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
                    next_nodes.update(adj_matrix.get(node, []))
        return out

    adj_matrix = (
        pd.DataFrame({"left": left, "right": right})
        .groupby("left")
        .right.apply(set)
        .to_dict()
    )

    groups = []
    seen = set()
    for node in adj_matrix.keys():
        if not node in seen:
            adj_nodes = _all_adj(adj_matrix, node)
            seen.update(adj_nodes)
            groups.append(adj_nodes)

    return groups


class DirectedGraph(object):
    def __init__(self, df, source, target):
        """Create DirectedGraph from data frame with source and target columns.

        Parameters
        ----------
        df : DataFrame,
        source : str
            name of source column
        target : str
            name of target_column
        """

        # save only unique combinations of source => target
        df = df.drop_duplicates(subset=[source, target])

        self.adj_matrix = df.set_index(target).groupby(source).groups
        self._size = len(self.adj_matrix)

    def __len__(self):
        return self._size

    @classmethod
    def from_arrays(cls, source, target):
        """Create DirectedGraph from arrays of sources and arrays of targets.

        Arrays must be the same length.

        Parameters
        ----------
        source : ndarray
        target : ndarray

        Returns
        -------
        DirectedGraph
        """

        return cls(
            pd.DataFrame({"source": source, "target": target}),
            source="source",
            target="target",
        )

    def descendants(self, sources):
        """Find all descendants of sources as a 1d array (one entry per node in
        sources) using a breadth-first search.

        Parameters
        ----------
        nodes : list-like or singular node
            1d ndarray if sources is list-like, else singular list of nodes
        """

        def _descendants(node):
            """Traverse adjacency matrix using breadth-first search to find all
            connected notes for a given starting node.

            Parameters
            ----------
            node : number or string
                Starting node from which to find all adjacent nodes

            Returns
            -------
            set of adjacent nodes
            """
            out = set()
            next_nodes = set(self.adj_matrix.get(node, []))
            while next_nodes:
                nodes = next_nodes
                next_nodes = set()
                for next_node in nodes:
                    if not next_node in out:
                        out.add(next_node)
                        next_nodes.update(self.adj_matrix.get(next_node, []))
            return out

        f = np.frompyfunc(_descendants, 1, 1)
        return f(sources)

    def terminal_descendants(self, sources):
        """Find all terminal descendants (have no descendants themselves) of sources
        as a 1d array (one entry per node in sources).

        Parameters
        ----------
        nodes : list-like or singular node
            1d ndarray if sources is list-like, else singular list of nodes
        """

        def _terminal_descendants(node):
            """Traverse graph starting from the children of node"""
            out = set()
            next_nodes = set(self.adj_matrix.get(node, []))
            while next_nodes:
                nodes = next_nodes
                next_nodes = set()
                for next_node in nodes:
                    if not next_node in out:
                        children = self.adj_matrix.get(next_node, [])
                        if len(children) == 0:
                            out.add(next_node)
                        else:
                            next_nodes.update(children)
            return out

        f = np.frompyfunc(_terminal_descendants, 1, 1)
        return f(sources)

    def components(self):
        """Find all connected components in graph.

        Adapted from networkx::connected_component

        Returns
        -------
        list of sets
            each set is the connected nodes in the graph
        """
        groups = []
        seen = set()
        for node in self.adj_matrix.keys():
            if not node in seen:
                # add current node with all descendants
                adj_nodes = {node} | self.descendants(node)
                seen.update(adj_nodes)
                groups.append(adj_nodes)

        return groups

    def _is_reachable(self, node, target_nodes, max_depth=None):
        try:
            target_nodes = set(target_nodes)
        except TypeError:
            target_nodes = set([target_nodes])

        if max_depth is None:
            max_depth = self._size

        depth = 0
        seen = set()
        next_nodes = set(self.adj_matrix.get(node, []))
        while next_nodes and depth <= max_depth:
            depth += 1
            nodes = next_nodes
            next_nodes = set()
            for next_node in nodes:
                if next_node in target_nodes:
                    return True

                if not next_node in seen:
                    seen.add(next_node)
                    next_nodes.update(self.adj_matrix.get(next_node, []))

        return False

    def is_reachable(self, sources, targets, max_depth=None):
        """Return True for each pair of source in sources and targets in targets
        for which there exists a route within the adjacency matrix.

        Parameters
        ----------
        sources : 1d ndarray of source nodes
        targets : 1d array of list-like of target nodes
            must be same length as sources; list-like of targets per source
        max_depth : [type], optional (default: None)
            If set, will be the maximum number of descendants of each source
            to search for a route to any of targets.  By default will search
            through all nodes in graph.

        Returns
        -------
        ndarray (bool)
        """

        if not len(sources) == len(targets):
            raise ValueError("sources and targets must be same length")

        if max_depth is None:
            max_depth = self._size

        out = np.zeros(shape=(len(sources)), dtype="bool")
        for i in range(len(sources)):
            out[i] = self._is_reachable(sources[i], targets[i], max_depth)
        return out

    def find_all_parents(self, sources, max_depth=None):
        out = np.empty(shape=(len(sources),), dtype="object")

        def _find_parents(nodes, max_depth):
            # first eliminate any for which there are no children
            search_nodes = {n for n in nodes if n in self.adj_matrix}
            parents = set()
            for node in search_nodes:
                if self._is_reachable(node, search_nodes - {node}, max_depth):
                    parents.add(node)

            return parents

        if max_depth is None:
            max_depth = self._size
        for i in range(len(sources)):
            out[i] = _find_parents(sources[i], max_depth=max_depth)

        return out

    def find_loops(self, sources, max_depth=None):
        # use depth-first search to create a list of loops that join to nodes
        # already seen during traversal

        if max_depth is None:
            max_depth = self._size

        seen = set()
        loops = set()
        for start_node in sources:
            depth = 0
            stack = [start_node]
            prev_node = start_node
            while stack:
                depth += 1
                if max_depth and depth >= max_depth:
                    break

                node = stack.pop()
                # print(f"{depth}: visiting {node}")
                if node in seen:
                    # add parent node; it is the loop
                    loops.add(prev_node)
                    # print(f"loop: {prev_node} => {node}")
                else:
                    seen.add(node)
                    stack.extend(reversed(self.adj_matrix.get(node, [])))

                prev_node = node

        return loops
