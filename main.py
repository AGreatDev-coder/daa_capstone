"""
Mini-Courier Planner - Main Application Entry Point
Design & Analysis of Algorithms (ETCCDA302) - Capstone Project
K.R. Mangalam University
"""

import argparse
import sys
import os
from typing import List, Set, Dict

from utils.models import Location, Parcel, RoadGraph
from utils.data_loader import load_courier_environment
from utils.validation import ValidationError
from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import get_shortest_path, compute_all_pairs_shortest_paths
from algorithms.tsp import solve_tsp_nearest_neighbor


def print_banner():
    banner = """
================================================================================
                    MINI-COURIER PLANNER (DAA CAPSTONE)
              Algorithmic Parcel Dispatch and Route Optimization
================================================================================
"""
    print(banner)


def display_loaded_data(locations: List[Location], parcels: List[Parcel], graph: RoadGraph, depot_id: str):
    print("--------------------------------------------------------------------------------")
    print(" [PHASE 1] DATA LOADING & INTEGRITY VERIFICATION")
    print("--------------------------------------------------------------------------------")
    print(f"[*] Depot Location         : {depot_id}")
    print(f"[*] Total Locations Loaded : {len(locations)}")
    print(f"[*] Total Road Nodes       : {len(graph.nodes)}")
    print(f"[*] Total Parcels Loaded   : {len(parcels)}\n")

    print(f"{'Parcel ID':<10} | {'Destination':<10} | {'Weight (kg)':<12} | {'Value (Rs)':<12} | {'Priority':<10} | {'Deadline (hrs)':<14}")
    print("-" * 78)
    for p in parcels:
        print(f"{p.parcel_id:<10} | {p.destination_id:<10} | {p.weight:<12.1f} | {p.value:<12.1f} | {p.priority:<10} | {p.deadline:<14.1f}")
    print("-" * 78 + "\n")


def run_pipeline(data_dir: str, depot_id: str, capacity: float, return_to_depot: bool = True, verbose: bool = False):
    print_banner()

    # Step 1: Load and Validate Data
    try:
        locations, parcels, graph = load_courier_environment(data_dir, depot_id, capacity)
    except ValidationError as e:
        print(f"[FATAL ERROR] Dataset validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL ERROR] Failed to load data from '{data_dir}': {e}")
        sys.exit(1)

    display_loaded_data(locations, parcels, graph, depot_id)

    # Step 2: Parcel Prioritization using Merge Sort
    print("--------------------------------------------------------------------------------")
    print(" [PHASE 2A] PARCEL PRIORITIZATION (ALGORITHM: MERGE SORT)")
    print(" Rule: Higher Priority -> Earlier Deadline -> Deterministic ID Tie-breaker")
    print("--------------------------------------------------------------------------------")
    sorted_parcels, comp_count = merge_sort(parcels)
    print(f"[+] Total Divide-and-Conquer Comparisons Performed: {comp_count}\n")
    print(f"{'Rank':<6} | {'Parcel ID':<10} | {'Destination':<10} | {'Priority':<10} | {'Deadline':<10} | {'Weight':<8} | {'Value':<8}")
    print("-" * 74)
    for rank, p in enumerate(sorted_parcels, 1):
        print(f"{rank:<6} | {p.parcel_id:<10} | {p.destination_id:<10} | {p.priority:<10} | {p.deadline:<10.1f} | {p.weight:<8.1f} | {p.value:<8.1f}")
    print("-" * 74 + "\n")

    # Step 3: Vehicle Packing using 0/1 Knapsack Dynamic Programming
    print("--------------------------------------------------------------------------------")
    print(" [PHASE 2B] VEHICLE PACKING (ALGORITHM: 0/1 KNAPSACK DYNAMIC PROGRAMMING)")
    print(f" Vehicle Maximum Weight Capacity: {capacity:.1f} kg")
    print("--------------------------------------------------------------------------------")
    knapsack_res = knapsack_01(sorted_parcels, capacity=capacity, weight_scale=10)
    print(f"[+] Optimal Subset Selected   : {[p.parcel_id for p in knapsack_res.selected_parcels]}")
    print(f"[+] Total Packed Weight        : {knapsack_res.total_weight:.1f} / {capacity:.1f} kg ({knapsack_res.capacity_utilization_pct:.1f}% capacity utilized)")
    print(f"[+] Total Delivery Value Earned: Rs. {knapsack_res.total_value:.2f}\n")

    print("Selected Parcels Breakdown:")
    print(f"{'Parcel ID':<10} | {'Destination':<10} | {'Weight (kg)':<12} | {'Value (Rs)':<12} | {'Priority':<8}")
    print("-" * 60)
    for p in knapsack_res.selected_parcels:
        print(f"{p.parcel_id:<10} | {p.destination_id:<10} | {p.weight:<12.1f} | {p.value:<12.1f} | {p.priority:<8}")
    print("-" * 60)

    if verbose or len(parcels) <= 15:
        print("\nDynamic Programming Table (Sample Output):")
        print(knapsack_res.format_table_summary(max_cols=12))
    print("\n")

    # Step 4: Extract Unique Delivery Destinations
    print("--------------------------------------------------------------------------------")
    print(" [PHASE 3A] DELIVERY DESTINATIONS EXTRACTION")
    print("--------------------------------------------------------------------------------")
    destinations: Set[str] = {p.destination_id for p in knapsack_res.selected_parcels}
    dest_to_parcels: Dict[str, List[str]] = {}
    for p in knapsack_res.selected_parcels:
        dest_to_parcels.setdefault(p.destination_id, []).append(p.parcel_id)

    print(f"Unique Delivery Stops Required ({len(destinations)} stops):")
    for d in sorted(list(destinations)):
        print(f"  - Location '{d}': Delivers parcel(s) {dest_to_parcels[d]}")
    print()

    # Step 5: Shortest Path Routing using Dijkstra
    print("--------------------------------------------------------------------------------")
    print(" [PHASE 3B] SHORTEST PATH ANALYSIS (ALGORITHM: DIJKSTRA'S ALGORITHM)")
    print(f" Source Depot: '{depot_id}'")
    print("--------------------------------------------------------------------------------")
    print(f"{'Target Destination':<20} | {'Shortest Distance':<18} | {'Shortest Path Trajectory':<35}")
    print("-" * 78)
    for dest in sorted(list(destinations)):
        dist, path = get_shortest_path(graph, depot_id, dest)
        path_str = " -> ".join(path) if path else "UNREACHABLE"
        dist_str = f"{dist:.2f} km" if dist < float("inf") else "INF"
        print(f"{dest:<20} | {dist_str:<18} | {path_str:<35}")
    print("-" * 78 + "\n")

    # Step 6: Complete Courier Route Tour using Nearest Neighbor TSP
    print("--------------------------------------------------------------------------------")
    print(" [PHASE 3C] DELIVERY TOUR SEQUENCING (ALGORITHM: NEAREST NEIGHBOR TSP)")
    print(" Approximation heuristic with Dijkstra distance matrix")
    print("--------------------------------------------------------------------------------")
    tsp_res = solve_tsp_nearest_neighbor(graph, depot_id, destinations, return_to_depot=return_to_depot)

    print(f"[*] Planned Stop Order : {' -> '.join(tsp_res.visit_order)}")
    print(f"[*] Expanded Road Path : {' -> '.join(tsp_res.expanded_path)}")
    print(f"[*] Total Trip Distance: {tsp_res.total_distance:.2f} km")
    print(f"[*] Returned to Depot  : {tsp_res.returns_to_depot}\n")

    if tsp_res.unreachable_locations:
        print(f"[!] WARNING: Could not reach locations: {tsp_res.unreachable_locations}")

    print("Detailed Leg Breakdown:")
    print(f"{'Leg':<5} | {'From':<10} | {'To':<10} | {'Distance':<10} | {'Road Path Segment':<35}")
    print("-" * 75)
    for idx, leg in enumerate(tsp_res.legs, 1):
        print(f"{idx:<5} | {leg.from_node:<10} | {leg.to_node:<10} | {leg.distance:<10.2f} | {' -> '.join(leg.segment_path):<35}")
    print("-" * 75 + "\n")

    # Step 7: Final Dispatch Manifest Summary
    print("=================================================================================")
    print("                           FINAL COURIER DISPATCH MANIFEST")
    print("=================================================================================")
    print(f" Vehicle Capacity       : {capacity:.1f} kg")
    print(f" Total Weight Loaded    : {knapsack_res.total_weight:.1f} kg ({knapsack_res.capacity_utilization_pct:.1f}% utilized)")
    print(f" Total Parcels Loaded   : {len(knapsack_res.selected_parcels)}")
    print(f" Total Delivery Revenue : Rs. {knapsack_res.total_value:.2f}")
    print(f" Total Travel Distance  : {tsp_res.total_distance:.2f} km")
    print(f" Planned Tour Sequence  : {' -> '.join(tsp_res.visit_order)}")
    print(f" Expanded Road Segments : {' -> '.join(tsp_res.expanded_path)}")
    print("=================================================================================\n")

    return {
        "sorted_parcels": sorted_parcels,
        "knapsack_result": knapsack_res,
        "tsp_result": tsp_res,
        "destinations": destinations
    }


def main():
    parser = argparse.ArgumentParser(description="Mini-Courier Planner - DAA University Capstone Project")
    parser.add_argument("--data-dir", default="data", help="Directory containing locations.json, parcels.json, roads.json")
    parser.add_argument("--depot", default="DEPOT", help="Depot/warehouse location identifier (default: DEPOT)")
    parser.add_argument("--capacity", type=float, default=25.0, help="Vehicle maximum weight capacity in kg (default: 25.0)")
    parser.add_argument("--no-return", dest="return_to_depot", action="store_false", help="Do not return vehicle to depot after deliveries")
    parser.add_argument("--verbose", action="store_true", help="Print verbose execution and DP table")
    parser.add_argument("--benchmark", action="store_true", help="Run performance testing suite across multiple dataset sizes")

    args = parser.parse_args()

    if args.benchmark:
        from utils.performance import run_performance_benchmarks
        run_performance_benchmarks()
    else:
        run_pipeline(
            data_dir=args.data_dir,
            depot_id=args.depot,
            capacity=args.capacity,
            return_to_depot=args.return_to_depot,
            verbose=args.verbose
        )


if __name__ == "__main__":
    main()

