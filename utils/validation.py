"""Input data validation module for Mini-Courier Planner."""

from typing import List, Dict, Any, Optional
from utils.models import Location, Parcel, RoadEdge


class ValidationError(Exception):
    """Custom exception raised when courier planner input data fails validation."""
    pass


def validate_locations(locations: List[Location], depot_id: str) -> None:
    """Validates location records and ensures the depot location exists."""
    if not locations:
        raise ValidationError("Locations list cannot be empty.")

    seen_ids = set()
    depot_found = False

    for loc in locations:
        if not loc.location_id or not str(loc.location_id).strip():
            raise ValidationError("Location ID cannot be empty.")
        if loc.location_id in seen_ids:
            raise ValidationError(f"Duplicate location ID found: '{loc.location_id}'.")
        seen_ids.add(loc.location_id)

        if not loc.location_name or not str(loc.location_name).strip():
            raise ValidationError(f"Location name for '{loc.location_id}' cannot be empty.")

        if loc.location_id == depot_id or loc.is_depot:
            depot_found = True

    if depot_id not in seen_ids:
        raise ValidationError(f"Depot location ID '{depot_id}' not found in registered locations.")


def validate_parcels(parcels: List[Parcel], valid_location_ids: set) -> None:
    """Validates parcel records, weights, values, and references to destinations."""
    if parcels is None:
        raise ValidationError("Parcels collection cannot be None.")

    seen_parcel_ids = set()
    for p in parcels:
        if not p.parcel_id or not str(p.parcel_id).strip():
            raise ValidationError("Parcel ID cannot be empty.")
        if p.parcel_id in seen_parcel_ids:
            raise ValidationError(f"Duplicate parcel ID found: '{p.parcel_id}'.")
        seen_parcel_ids.add(p.parcel_id)

        if p.destination_id not in valid_location_ids:
            raise ValidationError(
                f"Parcel '{p.parcel_id}' has destination '{p.destination_id}' "
                f"which is not in the registered locations list."
            )

        if p.weight < 0:
            raise ValidationError(f"Parcel '{p.parcel_id}' has invalid negative weight: {p.weight}")

        if p.value < 0:
            raise ValidationError(f"Parcel '{p.parcel_id}' has invalid negative value: {p.value}")

        if not isinstance(p.priority, int):
            raise ValidationError(f"Parcel '{p.parcel_id}' priority must be an integer, got {type(p.priority).__name__}")

        if p.deadline < 0:
            raise ValidationError(f"Parcel '{p.parcel_id}' deadline cannot be negative: {p.deadline}")


def validate_roads(roads: List[RoadEdge], valid_location_ids: set) -> None:
    """Validates road graph edges, endpoints, and non-negative distances."""
    if roads is None:
        raise ValidationError("Roads collection cannot be None.")

    for road in roads:
        if road.u not in valid_location_ids:
            raise ValidationError(f"Road edge endpoint '{road.u}' is not a valid registered location.")
        if road.v not in valid_location_ids:
            raise ValidationError(f"Road edge endpoint '{road.v}' is not a valid registered location.")
        if road.distance < 0:
            raise ValidationError(
                f"Road distance between '{road.u}' and '{road.v}' must be non-negative for Dijkstra's algorithm. "
                f"Got: {road.distance}"
            )


def validate_vehicle_capacity(capacity: float) -> None:
    """Validates vehicle capacity."""
    if capacity < 0:
        raise ValidationError(f"Vehicle capacity cannot be negative: {capacity}")


def validate_dataset(locations: List[Location], parcels: List[Parcel],
                     roads: List[RoadEdge], depot_id: str, vehicle_capacity: float) -> None:
    """Comprehensive validation of the entire courier planning dataset."""
    validate_locations(locations, depot_id)
    valid_location_ids = {loc.location_id for loc in locations}
    validate_parcels(parcels, valid_location_ids)
    validate_roads(roads, valid_location_ids)
    validate_vehicle_capacity(vehicle_capacity)

