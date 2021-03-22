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

        self._size = len(df)
        self.adj_matrix = df.set_index(target).groupby(source).groups

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

    def _descendents(self, node):
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
                    next_nodes.update(self.adj_matrix.get(node, []))
        return out

    def descendents(self, sources):
        """Find all desendents of sources as a 1d array (one entry per node in sources)

        Parameters
        ----------
        nodes : list-like or singular node
            1d ndarray if sources is list-like, else singular list of nodes
        """

        def _descendents(node):
            """Traverse graph starting from the children of node"""
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

        f = np.frompyfunc(_descendents, 1, 1)
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
                # add current node with all descendents
                adj_nodes = {node} | self.descendents(node)
                seen.update(adj_nodes)
                groups.append(adj_nodes)

        return groups

    def is_reachable(self, sources, targets, max_depth=None):
        def _is_reachable(node, target_nodes, max_depth):
            print(f"source: {node}, targets: {target_nodes}, max_depth: {max_depth}")
            try:
                target_nodes = set(target_nodes)
            except TypeError:
                target_nodes = set([target_nodes])

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

        if not len(sources) == len(targets):
            raise ValueError("sources and targets must be same length")

        if max_depth is None:
            max_depth = self._size

        out = np.zeros(shape=(len(sources)), dtype="bool")
        for i in range(len(sources)):
            out[i] = _is_reachable(sources[i], targets[i], max_depth)
        return out

