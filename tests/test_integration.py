"""Integration tests for the complete Mini-Courier Planner pipeline."""

import unittest
import os
from main import run_pipeline
from utils.models import Location, Parcel, RoadGraph
from utils.data_loader import load_courier_environment
from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import get_shortest_path
from algorithms.tsp import solve_tsp_nearest_neighbor


class TestIntegrationPipeline(unittest.TestCase):

    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    def test_full_pipeline_sample_data(self):
        """Runs the complete integrated pipeline on standard data and verifies all invariants."""
        res = run_pipeline(
            data_dir=self.data_dir,
            depot_id="DEPOT",
            capacity=25.0,
            return_to_depot=True,
            verbose=False
        )

        sorted_parcels = res["sorted_parcels"]
        knapsack_res = res["knapsack_result"]
        tsp_res = res["tsp_result"]
        destinations = res["destinations"]

        # Invariant 1: Total selected weight must not exceed vehicle capacity
        self.assertLessEqual(knapsack_res.total_weight, 25.0)

        # Invariant 2: No duplicate parcels in selection
        selected_ids = [p.parcel_id for p in knapsack_res.selected_parcels]
        self.assertEqual(len(selected_ids), len(set(selected_ids)))

        # Invariant 3: Selected parcel destinations must match required tour destinations
        expected_dests = {p.destination_id for p in knapsack_res.selected_parcels}
        self.assertEqual(destinations, expected_dests)

        # Invariant 4: Every required destination must be present in visit sequence
        for dest in destinations:
            self.assertIn(dest, tsp_res.visit_order)

        # Invariant 5: TSP tour must start and end at the configured depot
        self.assertEqual(tsp_res.visit_order[0], "DEPOT")
        self.assertEqual(tsp_res.visit_order[-1], "DEPOT")

        # Invariant 6: Route distance must equal the sum of its constituent legs
        computed_legs_sum = sum(leg.distance for leg in tsp_res.legs)
        self.assertAlmostEqual(tsp_res.total_distance, computed_legs_sum, places=4)

        # Invariant 7: Expanded road path must be a contiguous walk
        expanded = tsp_res.expanded_path
        self.assertGreater(len(expanded), 1)
        self.assertEqual(expanded[0], "DEPOT")
        self.assertEqual(expanded[-1], "DEPOT")

    def test_pipeline_zero_capacity(self):
        """Pipeline should handle zero vehicle capacity without crashing."""
        res = run_pipeline(
            data_dir=self.data_dir,
            depot_id="DEPOT",
            capacity=0.0,
            return_to_depot=True,
            verbose=False
        )
        self.assertEqual(res["knapsack_result"].selected_parcels, [])
        self.assertEqual(res["knapsack_result"].total_weight, 0.0)
        self.assertEqual(res["tsp_result"].visit_order, ["DEPOT"])
        self.assertEqual(res["tsp_result"].total_distance, 0.0)


if __name__ == "__main__":
    unittest.main()

