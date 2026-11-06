"""Shortest path calculations on weighted graphs using Dijkstra's algorithm."""

import heapq
from typing import Dict, List, Optional, Tuple, Set
from utils.models import RoadGraph


def dijkstra(graph: RoadGraph, source: str) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Computes single-source shortest paths from `source` to all reachable nodes.
    
    Time Complexity: O((V + E) log V) using a binary min-heap.
    Space Complexity: O(V) for distances, predecessors, and heap storage.
    
    Parameters:
    - graph: RoadGraph instance containing nodes and non-negative edge weights.
    - source: Identifier of the starting location.
    
    Returns:
    - distances: Dict mapping each node to its shortest distance from `source`.
    - predecessors: Dict mapping each node to its predecessor on the shortest path.
    """
    if source not in graph.nodes:
        raise ValueError(f"Source node '{source}' does not exist in graph.")

    distances: Dict[str, float] = {node: float("inf") for node in graph.nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in graph.nodes}

    distances[source] = 0.0
    # Min-heap storing tuples: (current_distance, node_id)
    pq: List[Tuple[float, str]] = [(0.0, source)]

    visited: Set[str] = set()

    while pq:
        curr_dist, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        for v, weight in graph.get_neighbors(u).items():
            if weight < 0:
                raise ValueError(f"Negative edge weight encountered ({u} -> {v}: {weight}). "
                                 f"Dijkstra requires non-negative edges.")

            if distances[u] + weight < distances[v]:
                distances[v] = distances[u] + weight
                predecessors[v] = u
                heapq.heappush(pq, (distances[v], v))

    return distances, predecessors


def reconstruct_path(predecessors: Dict[str, Optional[str]], source: str, destination: str) -> List[str]:
    """
    Reconstructs the node sequence on the shortest path from `source` to `destination`.
    Returns an empty list [] if `destination` is unreachable.
    """
    if source == destination:
        return [source]

    path: List[str] = []
    curr: Optional[str] = destination

    while curr is not None:
        path.append(curr)
        if curr == source:
            break
        curr = predecessors.get(curr)

    if not path or path[-1] != source:
        # Destination was not reachable from source
        return []

    path.reverse()
    return path


def get_shortest_path(graph: RoadGraph, source: str, destination: str) -> Tuple[float, List[str]]:
    """
    Convenience function returning (distance, path_list) between source and destination.
    """
    distances, predecessors = dijkstra(graph, source)
    dist = distances.get(destination, float("inf"))
    if dist == float("inf"):
        return float("inf"), []
    path = reconstruct_path(predecessors, source, destination)
    return dist, path


def compute_all_pairs_shortest_paths(
    graph: RoadGraph,
    nodes_of_interest: Set[str]
) -> Tuple[Dict[Tuple[str, str], float], Dict[Tuple[str, str], List[str]]]:
    """
    Runs Dijkstra from each node in `nodes_of_interest` to compute pairwise distances
    and shortest path node sequences among that subset of nodes.
    
    Returns:
    - pair_distances: Dict mapping (u, v) -> distance
    - pair_paths: Dict mapping (u, v) -> [u, ..., v]
    """
    pair_distances: Dict[Tuple[str, str], float] = {}
    pair_paths: Dict[Tuple[str, str], List[str]] = {}

    for u in nodes_of_interest:
        if u not in graph.nodes:
            continue
        distances, predecessors = dijkstra(graph, u)
        for v in nodes_of_interest:
            dist = distances.get(v, float("inf"))
            pair_distances[(u, v)] = dist
            if dist < float("inf"):
                pair_paths[(u, v)] = reconstruct_path(predecessors, u, v)
            else:
                pair_paths[(u, v)] = []

    return pair_distances, pair_paths

