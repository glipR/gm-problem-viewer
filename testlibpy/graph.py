import collections
from heapq import heappop, heappush
from queue import Queue
import random
from typing import Callable

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
        self, source: int, *, respect_direction: bool = True, use_weights: bool = True
    ) -> tuple[dict[int, float], dict[int, int | None]]:
        distance = collections.defaultdict(lambda: float("inf"))
        distance[source] = 0
        parent = collections.defaultdict(lambda: None)
        if not use_weights:
            # BFS
            queue = Queue()
            queue.put(source)
            expanded = set()
            expanded.add(source)
            while not queue.empty():
                node = queue.get()
                for adj, _w in self.forward_adj[node]:
                    if adj not in expanded:
                        expanded.add(adj)
                        distance[adj] = distance[node] + 1
                        parent[adj] = node
                        queue.put(adj)
                if not respect_direction:
                    for adj, _w in self.backward_adj[node]:
                        if adj not in expanded:
                            expanded.add(adj)
                            distance[adj] = distance[node] + 1
                            parent[adj] = node
                            queue.put(adj)
        else:
            # Dijkstra
            heap = []
            heappush(heap, (distance[source], source))
            while heap:
                dist, node = heappop(heap)
                if dist > distance[node]:
                    continue
                for adj, w in self.forward_adj[node]:
                    if dist + w < distance[adj]:
                        distance[adj] = dist + w
                        heappush(heap, (distance[adj], adj))
                        parent[adj] = node
                if not respect_direction:
                    for adj, w in self.forward_adj[node]:
                        if dist + w < distance[adj]:
                            distance[adj] = dist + w
                            heappush(heap, (distance[adj], adj))
                            parent[adj] = node
        return distance, parent


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
