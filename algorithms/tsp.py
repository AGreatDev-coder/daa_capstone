"""Delivery route sequencing using Nearest Neighbor TSP heuristic and Dijkstra shortest paths."""

from dataclasses import dataclass, field
from typing import List, Set, Dict, Tuple, Optional, Any
from utils.models import RoadGraph
from algorithms.dijkstra import compute_all_pairs_shortest_paths


@dataclass
class RouteLeg:
    """Represents one segment of the courier tour between two stops."""
    from_node: str
    to_node: str
    distance: float
    segment_path: List[str]


@dataclass
class TSPResult:
    """Encapsulates the result of the Nearest Neighbor TSP tour."""
    visit_order: List[str]
    expanded_path: List[str]
    total_distance: float
    legs: List[RouteLeg]
    unreachable_locations: List[str]
    returns_to_depot: bool

    def format_summary(self) -> str:
        lines = []
        lines.append(f"Visit Sequence : {' -> '.join(self.visit_order)}")
        lines.append(f"Expanded Path  : {' -> '.join(self.expanded_path) if self.expanded_path else 'None'}")
        lines.append(f"Total Distance : {self.total_distance:.2f} km")
        lines.append(f"Return to Depot: {self.returns_to_depot}")
        if self.unreachable_locations:
            lines.append(f"WARNING: Unreachable locations: {', '.join(self.unreachable_locations)}")
        return "\n".join(lines)


def solve_tsp_nearest_neighbor(
    graph: RoadGraph,
    depot: str,
    delivery_locations: Set[str],
    return_to_depot: bool = True
) -> TSPResult:
    """
    Constructs a delivery route using the Nearest Neighbor heuristic.
    
    Uses Dijkstra shortest-path distances as the metric between delivery stops,
    ensuring valid travel even if direct road edges do not connect all pairs.
    
    Parameters:
    - graph: RoadGraph instance.
    - depot: Starting (and ending) warehouse node ID.
    - delivery_locations: Set of target location IDs to visit.
    - return_to_depot: Whether the courier returns to the depot at the end.
    
    Returns:
    - TSPResult with visit order, expanded road path, total distance, and legs.
    """
    if depot not in graph.nodes:
        raise ValueError(f"Depot node '{depot}' does not exist in the road graph.")

    # Distinct targets excluding the depot
    unvisited = set(delivery_locations) - {depot}

    if not unvisited:
        return TSPResult(
            visit_order=[depot],
            expanded_path=[depot],
            total_distance=0.0,
            legs=[],
            unreachable_locations=[],
            returns_to_depot=return_to_depot
        )

    # 1. Compute all-pairs shortest paths and distances between all relevant nodes
    relevant_nodes = set(unvisited) | {depot}
    pair_distances, pair_paths = compute_all_pairs_shortest_paths(graph, relevant_nodes)

    current_node = depot
    visit_order = [depot]
    legs: List[RouteLeg] = []
    total_dist = 0.0
    unreachable: List[str] = []

    # 2. Greedily visit the nearest unvisited neighbor
    while unvisited:
        nearest_node = None
        min_dist = float("inf")

        # Deterministic sorting of candidate keys for tie-breaking
        for candidate in sorted(list(unvisited)):
            dist = pair_distances.get((current_node, candidate), float("inf"))
            if dist < min_dist:
                min_dist = dist
                nearest_node = candidate

        if nearest_node is None or min_dist == float("inf"):
            # All remaining unvisited nodes are disconnected/unreachable from current_node
            unreachable = sorted(list(unvisited))
            break

        # Move to nearest_node
        leg_path = pair_paths.get((current_node, nearest_node), [current_node, nearest_node])
        legs.append(RouteLeg(
            from_node=current_node,
            to_node=nearest_node,
            distance=min_dist,
            segment_path=leg_path
        ))
        total_dist += min_dist
        visit_order.append(nearest_node)
        unvisited.remove(nearest_node)
        current_node = nearest_node

    # 3. Optional return to depot
    if return_to_depot and len(visit_order) > 1 and current_node != depot:
        return_dist = pair_distances.get((current_node, depot), float("inf"))
        if return_dist < float("inf"):
            return_path = pair_paths.get((current_node, depot), [current_node, depot])
            legs.append(RouteLeg(
                from_node=current_node,
                to_node=depot,
                distance=return_dist,
                segment_path=return_path
            ))
            total_dist += return_dist
            visit_order.append(depot)
        else:
            # Cannot return to depot
            unreachable.append(depot)

    # 4. Construct complete expanded path stitching together Dijkstra road segments
    expanded_path: List[str] = []
    if legs:
        for i, leg in enumerate(legs):
            if i == 0:
                expanded_path.extend(leg.segment_path)
            else:
                # Omit duplicate starting node of consecutive segment
                expanded_path.extend(leg.segment_path[1:])
    else:
        expanded_path = [depot]

    return TSPResult(
        visit_order=visit_order,
        expanded_path=expanded_path,
        total_distance=round(total_dist, 4),
        legs=legs,
        unreachable_locations=unreachable,
        returns_to_depot=return_to_depot
    )

