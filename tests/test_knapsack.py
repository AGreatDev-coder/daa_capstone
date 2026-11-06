"""Unit tests for vehicle packing using 0/1 Knapsack Dynamic Programming."""

import unittest
from utils.models import Parcel
from algorithms.knapsack import knapsack_01, KnapsackResult


class TestKnapsack(unittest.TestCase):

    def test_empty_parcel_list(self):
        """Empty parcels input should return empty selection and zero total."""
        res = knapsack_01([], capacity=20.0)
        self.assertEqual(res.selected_parcels, [])
        self.assertEqual(res.total_weight, 0.0)
        self.assertEqual(res.total_value, 0.0)

    def test_zero_capacity(self):
        """Zero capacity vehicle cannot carry any parcel."""
        p1 = Parcel("P01", "LOC_A", 2.0, 50.0, 3, 2.0)
        res = knapsack_01([p1], capacity=0.0)
        self.assertEqual(res.selected_parcels, [])
        self.assertEqual(res.total_weight, 0.0)
        self.assertEqual(res.total_value, 0.0)

    def test_negative_capacity(self):
        """Negative capacity should gracefully return empty selection."""
        p1 = Parcel("P01", "LOC_A", 2.0, 50.0, 3, 2.0)
        res = knapsack_01([p1], capacity=-5.0)
        self.assertEqual(res.selected_parcels, [])

    def test_parcels_heavier_than_capacity(self):
        """Parcels that exceed vehicle capacity cannot be chosen."""
        p1 = Parcel("P01", "LOC_A", 15.0, 100.0, 5, 1.0)
        p2 = Parcel("P02", "LOC_B", 20.0, 200.0, 5, 1.0)
        res = knapsack_01([p1, p2], capacity=10.0)
        self.assertEqual(res.selected_parcels, [])
        self.assertEqual(res.total_weight, 0.0)
        self.assertEqual(res.total_value, 0.0)

    def test_exact_capacity_fit(self):
        """A parcel exactly matching vehicle capacity should be chosen if optimal."""
        p1 = Parcel("P01", "LOC_A", 10.0, 150.0, 3, 2.0)
        p2 = Parcel("P02", "LOC_B", 5.0, 60.0, 3, 2.0)
        res = knapsack_01([p1, p2], capacity=10.0)
        self.assertEqual(len(res.selected_parcels), 1)
        self.assertEqual(res.selected_parcels[0].parcel_id, "P01")
        self.assertEqual(res.total_value, 150.0)
        self.assertEqual(res.total_weight, 10.0)

    def test_optimal_subset_selection(self):
        """
        Classic textbook 0/1 knapsack test case:
        Weights: [1, 3, 4, 5], Values: [1, 4, 5, 7], Capacity = 7
        Subsets:
        - {1, 4} weight 4, val 5
        - {3, 4} weight 7, val 9
        - {1, 5} weight 6, val 8
        Optimal: {3, 4} with total value 9, or {1, 5} val 8, wait:
        Wait: {3, 4} -> weight 3+4=7, value 4+5=9.
        Can we do {1, 5}? weight 6, value 8.
        So optimal is weight 7, value 9.
        """
        parcels = [
            Parcel("P1", "LOC_1", weight=1.0, value=1.0, priority=1, deadline=1.0),
            Parcel("P2", "LOC_2", weight=3.0, value=4.0, priority=1, deadline=1.0),
            Parcel("P3", "LOC_3", weight=4.0, value=5.0, priority=1, deadline=1.0),
            Parcel("P4", "LOC_4", weight=5.0, value=7.0, priority=1, deadline=1.0),
        ]
        res = knapsack_01(parcels, capacity=7.0, weight_scale=1)
        self.assertEqual(res.total_value, 9.0)
        self.assertEqual(res.total_weight, 7.0)
        selected_ids = {p.parcel_id for p in res.selected_parcels}
        self.assertEqual(selected_ids, {"P2", "P3"})

    def test_decimal_weight_resolution(self):
        """Verify dynamic programming handles decimal weights with scaling."""
        parcels = [
            Parcel("P1", "LOC_1", weight=1.5, value=30.0, priority=3, deadline=2.0),
            Parcel("P2", "LOC_2", weight=2.5, value=55.0, priority=4, deadline=2.0),
            Parcel("P3", "LOC_3", weight=3.5, value=75.0, priority=5, deadline=1.0),
        ]
        # Capacity 4.0 kg:
        # P1 (1.5) + P2 (2.5) = 4.0 kg, value = 85.0
        # P3 alone = 3.5 kg, value = 75.0
        # Optimal selection: P1 + P2 (value 85.0)
        res = knapsack_01(parcels, capacity=4.0, weight_scale=10)
        self.assertEqual(res.total_value, 85.0)
        self.assertEqual(res.total_weight, 4.0)
        self.assertEqual([p.parcel_id for p in res.selected_parcels], ["P1", "P2"])

    def test_no_duplicate_parcels(self):
        """0/1 property: each parcel must appear at most once."""
        parcels = [
            Parcel("P1", "LOC_1", weight=2.0, value=20.0, priority=1, deadline=1.0),
            Parcel("P2", "LOC_2", weight=2.0, value=20.0, priority=1, deadline=1.0),
        ]
        res = knapsack_01(parcels, capacity=5.0)
        ids = [p.parcel_id for p in res.selected_parcels]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertLessEqual(res.total_weight, 5.0)


if __name__ == "__main__":
    unittest.main()

