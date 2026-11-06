"""Parcel prioritization using Merge Sort algorithm."""

from typing import List, Tuple
from utils.models import Parcel


def compare_parcels(p1: Parcel, p2: Parcel) -> bool:
    """
    Comparison predicate for parcel prioritization.
    Returns True if p1 has higher dispatch priority than p2, or should come earlier.
    
    Priority Rules:
    1. Higher priority value first (e.g., 5 > 4).
    2. If priority is equal, earlier deadline first (smaller deadline hours).
    3. If both priority and deadline are identical, deterministic tie-break on parcel_id (ascending).
    """
    if p1.priority != p2.priority:
        return p1.priority > p2.priority
    if p1.deadline != p2.deadline:
        return p1.deadline < p2.deadline
    return p1.parcel_id < p2.parcel_id


def merge(left: List[Parcel], right: List[Parcel]) -> Tuple[List[Parcel], int]:
    """
    Merges two sorted sublists into a single sorted list based on compare_parcels.
    Returns (merged_list, comparison_count).
    """
    merged: List[Parcel] = []
    i = 0
    j = 0
    comparisons = 0

    while i < len(left) and j < len(right):
        comparisons += 1
        if compare_parcels(left[i], right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append remaining elements
    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged, comparisons


def merge_sort(parcels: List[Parcel]) -> Tuple[List[Parcel], int]:
    """
    Sorts a list of parcels using the Divide-and-Conquer Merge Sort algorithm.
    Time Complexity: O(n log n) in all cases (best, average, worst).
    Space Complexity: O(n) auxiliary space.
    
    Returns (sorted_parcels, total_comparisons).
    """
    if len(parcels) <= 1:
        return list(parcels), 0

    mid = len(parcels) // 2
    left_sorted, comp_left = merge_sort(parcels[:mid])
    right_sorted, comp_right = merge_sort(parcels[mid:])

    merged, comp_merge = merge(left_sorted, right_sorted)
    return merged, (comp_left + comp_right + comp_merge)


def prioritize_parcels(parcels: List[Parcel]) -> List[Parcel]:
    """
    Convenience function returning strictly the sorted parcels list.
    """
    sorted_parcels, _ = merge_sort(parcels)
    return sorted_parcels

