"""Data models for Mini-Courier Planner."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class Location:
    """Represents a physical courier location (depot or customer drop-off)."""
    location_id: str
    location_name: str
    is_depot: bool = False

    def to_dict(self) -> dict:
        return {
            "location_id": self.location_id,
            "location_name": self.location_name,
            "is_depot": self.is_depot
        }


@dataclass
class Parcel:
    """Represents a parcel with delivery priority, weight, value, and deadline."""
    parcel_id: str
    destination_id: str
    weight: float
    value: float
    priority: int       # Higher number indicates higher urgency (e.g., 5 = Urgent, 1 = Low)
    deadline: float     # Hours from start (lower number indicates earlier deadline)

    def to_dict(self) -> dict:
        return {
            "parcel_id": self.parcel_id,
            "destination_id": self.destination_id,
            "weight": self.weight,
            "value": self.value,
            "priority": self.priority,
            "deadline": self.deadline
        }


@dataclass
class RoadEdge:
    """Represents an undirected road between two locations with non-negative distance in km."""
    u: str
    v: str
    distance: float


class RoadGraph:
    """Weighted undirected graph representation using adjacency lists."""

    def __init__(self):
        self.adj: Dict[str, Dict[str, float]] = {}
        self.nodes: Set[str] = set()

    def add_node(self, node: str) -> None:
        self.nodes.add(node)
        if node not in self.adj:
            self.adj[node] = {}

    def add_edge(self, u: str, v: str, distance: float, bidirectional: bool = True) -> None:
        if distance < 0:
            raise ValueError(f"Distance cannot be negative for edge ({u}, {v}): {distance}")
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = distance
        if bidirectional:
            self.adj[v][u] = distance

    def get_neighbors(self, u: str) -> Dict[str, float]:
        return self.adj.get(u, {})

    def get_edge_distance(self, u: str, v: str) -> Optional[float]:
        return self.adj.get(u, {}).get(v, None)

    def to_dict(self) -> dict:
        edges = []
        visited_pairs = set()
        for u in self.adj:
            for v, dist in self.adj[u].items():
                edge_pair = tuple(sorted([u, v]))
                if edge_pair not in visited_pairs:
                    visited_pairs.add(edge_pair)
                    edges.append({"u": u, "v": v, "distance": dist})
        return {
            "nodes": sorted(list(self.nodes)),
            "edges": edges
        }

