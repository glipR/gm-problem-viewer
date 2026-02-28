import collections
from heapq import heappop, heappush
from queue import Queue
import random
from typing import Callable

from .random import select_k_distinct

ValueGen = int | Callable[tuple[int, int], int]


class Graph:
    """
    Graph object. Tracks both the edge list, and adjacency list representations simultaneously.

    - Supports edge/node randomisation for varied output.
    - Supports value randomisation based on end nodes.
    - Supports Basic distance metrics.

    See subclasses for generating specific types of graphs.
    https://csacademy.com/app/graph_editor/ is a great tool for visualising graphs.
    """

    def __init__(self, n: int, *, one_indexed: bool = True):
        self.n = n
        self.forward_adj = [[] for _ in range(self.n + 1)]
        self.backward_adj = [[] for _ in range(self.n + 1)]
        self.edge_list = []
        self.one_indexed = one_indexed

    def vertices(self):
        return range(self.n) if not self.one_indexed else range(1, self.n + 1)

    def add_edge(self, a: int, b: int, c: ValueGen = 1) -> "Graph":
        if isinstance(c, Callable):
            # Compute weight of edge
            c = c(a, b)
        self.forward_adj[a].append((b, c))
        self.backward_adj[b].append((a, c))
        self.edge_list.append((a, b, c))
        return self

    def reverse_all_edges(self) -> "Graph":
        self.forward_adj, self.backward_adj = self.backward_adj, self.forward_adj
        self.edge_list = [(b, a, c) for a, b, c in self.edge_list]
        return self

    def randomise_edge_dir(self) -> "Graph":
        self.edge_list = [
            (b, a, c) if random.random() > 0.5 else (a, b, c)
            for a, b, c in self.edge_list
        ]
        return self

    def randomise_nodes(self) -> tuple["Graph", dict[int, int], dict[int, int]]:
        m = list(range(self.n))
        random.shuffle(m)
        if self.one_indexed:
            forward_map = {i + 1: m[i] + 1 for i in range(self.n)}
            backward_map = {m[i] + 1: i + 1 for i in range(self.n)}
        else:
            forward_map = {i: m[i] for i in range(self.n)}
            backward_map = {m[i]: i for i in range(self.n)}

        new_graph = Graph(self.n, one_indexed=self.one_indexed)
        for a, b, c in self.edge_list:
            new_graph.add_edge(forward_map[a], forward_map[b], c)
        return new_graph, forward_map, backward_map

    def edges(self, randomise=True, include_weight=True):
        edge_copy = self.edge_list[::]
        if randomise:
            random.shuffle(edge_copy)
        if include_weight:
            return edge_copy
        else:
            return [(a, b) for a, b, c in edge_copy]

    def distance(
        self,
        source: int,
        *,
        respect_direction: bool = True,
        reduce_distance=lambda r, c: r + c,
        start_distance=0,
        default_distance=float("inf"),
    ) -> tuple[dict[int, float], dict[int, int | None]]:
        distance = collections.defaultdict(lambda: default_distance)
        distance[source] = start_distance
        parent = collections.defaultdict(lambda: None)
        # Dijkstra
        heap = []
        heappush(heap, (distance[source], source))
        while heap:
            dist, node = heappop(heap)
            if dist > distance[node]:
                continue
            for adj, w in self.forward_adj[node]:
                combined = reduce_distance(dist, w)
                if combined < distance[adj]:
                    distance[adj] = combined
                    heappush(heap, (distance[adj], adj))
                    parent[adj] = node
            if not respect_direction:
                for adj, w in self.forward_adj[node]:
                    combined = reduce_distance(dist, w)
                    if combined < distance[adj]:
                        distance[adj] = combined
                        heappush(heap, (distance[adj], adj))
                        parent[adj] = node
        return distance, parent


### Trees


class Path(Graph):
    """
    Path from 1 to N (or 0 to N-1)
    """

    def __init__(self, n: int, *, one_indexed: bool = True, c: ValueGen = 1):
        super().__init__(n, one_indexed=one_indexed)
        # Add edges from start to finish
        for i in self.vertices():
            if i + 1 in self.vertices():
                self.add_edge(i, i + 1, c)


class CompleteTree(Graph):
    """
    Perfect k-ary tree that fills out N nodes.
    """

    def __init__(
        self, n: int, *, one_indexed: bool = True, k: int = 2, c: ValueGen = 1
    ):
        super().__init__(n, one_indexed=one_indexed)
        if one_indexed:
            child_map = lambda x: [k * (x - 1) + i + 1 for i in range(1, k + 1)]
        else:
            child_map = lambda x: [k * x + i for i in range(1, k + 1)]
        for i in self.vertices():
            for child in child_map(i):
                if child in self.vertices():
                    self.add_edge(i, child, c)


class StarTree(Graph):
    """
    Star Tree, where everything is connected to the first node.
    """

    def __init__(self, n: int, *, one_indexed: bool = True, c: ValueGen = 1):
        super().__init__(n, one_indexed=one_indexed)
        for i in self.vertices():
            if i != int(one_indexed):
                self.add_edge(int(one_indexed), i, c)


class SkinnyTree(Graph):
    """
    A tree which isn't quite a path but has lots of small branching paths (Much closer to a path than a complete tree).
    """

    def __init__(
        self, n: int, *, one_indexed: bool = True, bf: int = 3, c: ValueGen = 1
    ):
        super().__init__(n, one_indexed=one_indexed)
        off = int(one_indexed)
        # Every node except the first:
        for i in range(1 + off, n + off):
            # Select a parent from at most bf steps back
            j = random.randint(max(off, i - bf), i - 1)
            self.add_edge(j, i, c)


class RandomTree(Graph):
    """
    Purely random tree by randomly adding leaves to an existing tree at any random node.
    """

    def __init__(self, n: int, *, one_indexed: bool = True, c: ValueGen = 1):
        super().__init__(n, one_indexed=one_indexed)
        off = int(one_indexed)
        for i in range(1 + off, n + off):
            j = random.randint(off, i - 1)
            self.add_edge(j, i, c)


### Other Graphs


class Complete(Graph):
    """
    Path from a to any b > a
    """

    def __init__(self, n: int, *, one_indexed: bool = True, c: ValueGen = 1):
        super().__init__(n, one_indexed=one_indexed)
        # Add edges from start to finish
        for i in self.vertices():
            for j in self.vertices():
                if j > i:
                    self.add_edge(i, j, c)


class RandomGraph(Graph):
    """
    Purely random graph, edge selection routine depends on relative size of edge set.

    No guarantee of connectivity
    """

    def __init__(
        self,
        n: int,
        m: int,
        *,
        one_indexed: bool = True,
        c: ValueGen = 1,
        fixed_edges: list[tuple[int, int]] = [],
    ):
        super().__init__(n, one_indexed=one_indexed)
        off = int(one_indexed)
        fixed_ordered = set((min(a, b), max(a, b)) for a, b in fixed_edges)
        if m > n**2 / 20:
            # We're already generating a tenth of the total edge set, so just generate the full edge set and randomise.
            edge_set = [
                (i, j)
                for i in self.vertices()
                for j in self.vertices()
                if i < j and (i, j) not in fixed_ordered
            ]
            edge_actual = select_k_distinct(edge_set, m)
            for i, j in edge_actual:
                self.add_edge(i, j, c)
            self.randomise_edge_dir()
        else:
            # The edges make up a small selection of the possible options, so randomly select
            try_limit = 10
            edge_set = fixed_ordered
            edge_list = fixed_edges
            tries = 0
            while len(edge_list) < m and tries < try_limit:
                i = random.randint(off, off + n - 1)
                j = random.randint(off, off + n - 1)
                if i == j:
                    tries += 1
                    continue
                i, j = min(i, j), max(i, j)
                if (i, j) in edge_set:
                    tries += 1
                    continue
                tries = 0
                edge_set.add((i, j))
                edge_list.append((i, j))
            if len(edge_list) < m:
                raise ValueError(f"Failed to generate {m} edges for {n} vertex graph")
            for i, j in edge_list:
                self.add_edge(i, j, c)
            self.randomise_edge_dir()


class RandomConnectedGraph(RandomGraph):
    def __init__(self, n: int, m: int, *, one_indexed: bool = True, c: ValueGen = 1):
        # Generate tree_edges, to be used as the basis for RandomGraph.
        off = int(one_indexed)
        tree_edges = []
        for i in range(1 + off, n + off):
            j = random.randint(off, i - 1)
            tree_edges.append((j, i))

        super().__init__(n, m, one_indexed=one_indexed, fixed_edges=tree_edges, c=c)


class Cycle(Graph):
    def __init__(self, n: int, *, one_indexed: bool = True, c: ValueGen = 1):
        super().__init__(n, one_indexed=one_indexed)
        off = int(one_indexed)
        for i in self.vertices():
            ni = i + 1
            if ni >= off + n:
                ni -= n
            self.add_edge(i, ni, c)
