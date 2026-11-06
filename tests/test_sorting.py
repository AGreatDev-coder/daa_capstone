"""Unit tests for parcel prioritization using Merge Sort."""

import unittest
from utils.models import Parcel
from algorithms.sorting import merge_sort, prioritize_parcels, compare_parcels


class TestSorting(unittest.TestCase):

    def test_empty_list(self):
        """Empty list should return empty list without error."""
        sorted_parcels, comparisons = merge_sort([])
        self.assertEqual(sorted_parcels, [])
        self.assertEqual(comparisons, 0)

    def test_single_item(self):
        """Single-item list should return the same item without comparisons."""
        p = Parcel("P01", "LOC_A", weight=2.0, value=30.0, priority=3, deadline=2.0)
        sorted_parcels, comparisons = merge_sort([p])
        self.assertEqual(len(sorted_parcels), 1)
        self.assertEqual(sorted_parcels[0].parcel_id, "P01")
        self.assertEqual(comparisons, 0)

    def test_already_sorted_input(self):
        """Already sorted parcels should remain in order."""
        p1 = Parcel("P01", "LOC_A", 2.0, 30.0, priority=5, deadline=1.0)
        p2 = Parcel("P02", "LOC_B", 3.0, 40.0, priority=4, deadline=2.0)
        p3 = Parcel("P03", "LOC_C", 1.0, 10.0, priority=3, deadline=3.0)
        input_list = [p1, p2, p3]
        result = prioritize_parcels(input_list)
        self.assertEqual([p.parcel_id for p in result], ["P01", "P02", "P03"])

    def test_reverse_sorted_input(self):
        """Reverse sorted parcels should be correctly sorted."""
        p1 = Parcel("P01", "LOC_A", 2.0, 30.0, priority=1, deadline=5.0)
        p2 = Parcel("P02", "LOC_B", 3.0, 40.0, priority=3, deadline=3.0)
        p3 = Parcel("P03", "LOC_C", 1.0, 10.0, priority=5, deadline=1.0)
        input_list = [p1, p2, p3]
        result = prioritize_parcels(input_list)
        self.assertEqual([p.parcel_id for p in result], ["P03", "P02", "P01"])

    def test_equal_priorities_earlier_deadline_first(self):
        """When priorities are equal, the parcel with an earlier deadline must come first."""
        p1 = Parcel("P_LATE", "LOC_A", 2.0, 30.0, priority=4, deadline=5.0)
        p2 = Parcel("P_EARLY", "LOC_B", 3.0, 40.0, priority=4, deadline=1.5)
        p3 = Parcel("P_MID", "LOC_C", 1.0, 10.0, priority=4, deadline=3.0)
        result = prioritize_parcels([p1, p2, p3])
        self.assertEqual([p.parcel_id for p in result], ["P_EARLY", "P_MID", "P_LATE"])

    def test_equal_priority_and_deadline_tiebreaker(self):
        """When priority and deadline are identical, parcel_id tie-breaker applies deterministically."""
        p1 = Parcel("P_Z", "LOC_A", 2.0, 30.0, priority=5, deadline=2.0)
        p2 = Parcel("P_A", "LOC_B", 3.0, 40.0, priority=5, deadline=2.0)
        p3 = Parcel("P_M", "LOC_C", 1.0, 10.0, priority=5, deadline=2.0)
        result = prioritize_parcels([p1, p2, p3])
        self.assertEqual([p.parcel_id for p in result], ["P_A", "P_M", "P_Z"])

    def test_multi_factor_sorting(self):
        """Test multi-tier sorting logic across multiple parcels."""
        parcels = [
            Parcel("P1", "LOC_A", 1.0, 10.0, priority=3, deadline=2.0),
            Parcel("P2", "LOC_A", 1.0, 10.0, priority=5, deadline=3.0),
            Parcel("P3", "LOC_A", 1.0, 10.0, priority=5, deadline=1.0),
            Parcel("P4", "LOC_A", 1.0, 10.0, priority=2, deadline=1.0),
        ]
        result = prioritize_parcels(parcels)
        # Expected:
        # P3: priority 5, deadline 1.0
        # P2: priority 5, deadline 3.0
        # P1: priority 3, deadline 2.0
        # P4: priority 2, deadline 1.0
        self.assertEqual([p.parcel_id for p in result], ["P3", "P2", "P1", "P4"])


if __name__ == "__main__":
    unittest.main()

