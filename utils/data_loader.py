"""Data loader and serializer module for Mini-Courier Planner."""

import json
import os
from typing import List, Tuple, Dict, Any
from utils.models import Location, Parcel, RoadEdge, RoadGraph
from utils.validation import validate_dataset


def load_locations_from_file(file_path: str) -> List[Location]:
    """Loads location records from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    locations = []
    for item in data:
        locations.append(Location(
            location_id=str(item["location_id"]),
            location_name=str(item["location_name"]),
            is_depot=bool(item.get("is_depot", False))
        ))
    return locations


def load_parcels_from_file(file_path: str) -> List[Parcel]:
    """Loads parcel records from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    parcels = []
    for item in data:
        parcels.append(Parcel(
            parcel_id=str(item["parcel_id"]),
            destination_id=str(item["destination_id"]),
            weight=float(item["weight"]),
            value=float(item["value"]),
            priority=int(item["priority"]),
            deadline=float(item["deadline"])
        ))
    return parcels


def load_roads_from_file(file_path: str) -> List[RoadEdge]:
    """Loads road connections from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    roads = []
    for item in data:
        roads.append(RoadEdge(
            u=str(item["u"]),
            v=str(item["v"]),
            distance=float(item["distance"])
        ))
    return roads


def build_road_graph(locations: List[Location], roads: List[RoadEdge]) -> RoadGraph:
    """Builds a RoadGraph adjacency representation from locations and edges."""
    graph = RoadGraph()
    for loc in locations:
        graph.add_node(loc.location_id)
    for road in roads:
        graph.add_edge(road.u, road.v, road.distance)
    return graph


def load_courier_environment(data_dir: str, depot_id: str = "DEPOT",
                             vehicle_capacity: float = 25.0) -> Tuple[List[Location], List[Parcel], RoadGraph]:
    """
    Loads, parses, validates, and builds the full courier environment from a directory.
    Returns (locations, parcels, road_graph).
    """
    loc_file = os.path.join(data_dir, "locations.json")
    parcels_file = os.path.join(data_dir, "parcels.json")
    roads_file = os.path.join(data_dir, "roads.json")

    locations = load_locations_from_file(loc_file)
    parcels = load_parcels_from_file(parcels_file)
    roads = load_roads_from_file(roads_file)

    # Validate dataset consistency
    validate_dataset(locations, parcels, roads, depot_id, vehicle_capacity)

    graph = build_road_graph(locations, roads)
    return locations, parcels, graph


def save_dataset_to_dir(data_dir: str, locations: List[Location], parcels: List[Parcel],
                        roads: List[RoadEdge]) -> None:
    """Saves locations, parcels, and roads to JSON files in the specified directory."""
    os.makedirs(data_dir, exist_ok=True)

    with open(os.path.join(data_dir, "locations.json"), "w", encoding="utf-8") as f:
        json.dump([l.to_dict() for l in locations], f, indent=2)

    with open(os.path.join(data_dir, "parcels.json"), "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in parcels], f, indent=2)

    with open(os.path.join(data_dir, "roads.json"), "w", encoding="utf-8") as f:
        json.dump([{"u": r.u, "v": r.v, "distance": r.distance} for r in roads], f, indent=2)

