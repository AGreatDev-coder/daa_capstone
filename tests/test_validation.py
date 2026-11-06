"""Unit tests for data models, validation, and data loading."""

import unittest
import os
from utils.models import Location, Parcel, RoadEdge, RoadGraph
from utils.validation import (
    validate_dataset,
    validate_locations,
    validate_parcels,
    validate_roads,
    ValidationError
)
from utils.data_loader import load_courier_environment


class TestDataValidation(unittest.TestCase):

    def setUp(self):
        self.locations = [
            Location("DEPOT", "Central Hub", is_depot=True),
            Location("LOC_1", "Drop Point 1"),
            Location("LOC_2", "Drop Point 2"),
        ]
        self.parcels = [
            Parcel("P1", "LOC_1", weight=2.0, value=30.0, priority=5, deadline=2.0),
            Parcel("P2", "LOC_2", weight=3.5, value=50.0, priority=3, deadline=4.0),
        ]
        self.roads = [
            RoadEdge("DEPOT", "LOC_1", 5.0),
            RoadEdge("LOC_1", "LOC_2", 3.0),
        ]
        self.depot_id = "DEPOT"
        self.capacity = 10.0

    def test_valid_dataset_passes(self):
        """A valid dataset should pass without raising ValidationError."""
        try:
            validate_dataset(self.locations, self.parcels, self.roads, self.depot_id, self.capacity)
        except ValidationError as e:
            self.fail(f"validate_dataset raised ValidationError unexpectedly: {e}")

    def test_missing_depot_raises_error(self):
        """Missing depot ID should raise ValidationError."""
        with self.assertRaises(ValidationError):
            validate_locations(self.locations, depot_id="NON_EXISTENT_DEPOT")

    def test_empty_locations_raises_error(self):
        """Empty location list should raise ValidationError."""
        with self.assertRaises(ValidationError):
            validate_locations([], depot_id="DEPOT")

    def test_negative_weight_raises_error(self):
        """Parcels with negative weights should raise ValidationError."""
        bad_parcels = [Parcel("P_BAD", "LOC_1", weight=-1.0, value=20.0, priority=1, deadline=2.0)]
        with self.assertRaises(ValidationError):
            validate_parcels(bad_parcels, {"DEPOT", "LOC_1", "LOC_2"})

    def test_negative_value_raises_error(self):
        """Parcels with negative values should raise ValidationError."""
        bad_parcels = [Parcel("P_BAD", "LOC_1", weight=2.0, value=-10.0, priority=1, deadline=2.0)]
        with self.assertRaises(ValidationError):
            validate_parcels(bad_parcels, {"DEPOT", "LOC_1", "LOC_2"})

    def test_negative_road_distance_raises_error(self):
        """Road edges with negative distances must raise ValidationError (Dijkstra requirement)."""
        bad_roads = [RoadEdge("DEPOT", "LOC_1", distance=-4.0)]
        with self.assertRaises(ValidationError):
            validate_roads(bad_roads, {"DEPOT", "LOC_1", "LOC_2"})

    def test_unregistered_destination_raises_error(self):
        """Parcel with destination not in location list should fail validation."""
        bad_parcels = [Parcel("P_BAD", "UNKNOWN_LOC", weight=2.0, value=10.0, priority=1, deadline=1.0)]
        with self.assertRaises(ValidationError):
            validate_parcels(bad_parcels, {"DEPOT", "LOC_1", "LOC_2"})

    def test_duplicate_parcel_id_raises_error(self):
        """Duplicate parcel IDs should raise ValidationError."""
        dup_parcels = [
            Parcel("P1", "LOC_1", weight=2.0, value=30.0, priority=5, deadline=2.0),
            Parcel("P1", "LOC_2", weight=1.0, value=20.0, priority=4, deadline=1.0),
        ]
        with self.assertRaises(ValidationError):
            validate_parcels(dup_parcels, {"DEPOT", "LOC_1", "LOC_2"})

    def test_load_sample_data_from_disk(self):
        """Verify the sample data files created in data/ load and validate successfully."""
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        locations, parcels, graph = load_courier_environment(data_dir, "DEPOT", 25.0)
        self.assertEqual(len(locations), 8)
        self.assertEqual(len(parcels), 10)
        self.assertEqual(len(graph.nodes), 8)
        self.assertTrue("DEPOT" in graph.nodes)
        self.assertEqual(graph.get_edge_distance("DEPOT", "LOC_A"), 4.0)


if __name__ == "__main__":
    unittest.main()

