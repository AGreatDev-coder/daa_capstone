"""
Performance benchmarking module for Mini-Courier Planner.
Measures execution time across multiple dataset sizes using time.perf_counter().
Exports results to CSV and generates runtime comparison charts using matplotlib.
"""

import os
import sys
import csv
import time
import random
import tempfile
from typing import List, Dict, Any, Tuple, Set

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure matplotlib to use temporary cache directory on Windows sandbox
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

from utils.models import Location, Parcel, RoadEdge, RoadGraph
from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import compute_all_pairs_shortest_paths
from algorithms.tsp import solve_tsp_nearest_neighbor


def generate_benchmark_dataset(num_parcels: int, num_locations: int, seed: int = 42) -> Tuple[List[Location], List[Parcel], RoadGraph, str, float]:
    """
    Generates a deterministic synthetic courier environment for benchmarking.
    Guarantees graph connectivity and positive road weights.
    """
    rng = random.Random(seed)

    # 1. Generate Locations
    depot_id = "DEPOT"
    locations = [Location(depot_id, "Central Distribution Center", is_depot=True)]
    loc_ids = [depot_id]

    for i in range(1, num_locations):
        lid = f"LOC_{i:03d}"
        locations.append(Location(lid, f"Delivery Sector {i}"))
        loc_ids.append(lid)

    # 2. Generate Connected Road Graph
    graph = RoadGraph()
    for lid in loc_ids:
        graph.add_node(lid)

    # Ensure connected backbone (spanning tree)
    for i in range(1, num_locations):
        parent_idx = rng.randint(0, i - 1)
        dist = round(rng.uniform(2.0, 15.0), 2)
        graph.add_edge(loc_ids[parent_idx], loc_ids[i], dist)

    # Add extra cross-edges to create realistic network mesh
    extra_edges = int(num_locations * 1.5)
    for _ in range(extra_edges):
        u = rng.choice(loc_ids)
        v = rng.choice(loc_ids)
        if u != v:
            dist = round(rng.uniform(1.5, 12.0), 2)
            graph.add_edge(u, v, dist)

    # 3. Generate Parcels
    parcels: List[Parcel] = []
    customer_locs = loc_ids[1:] if len(loc_ids) > 1 else [depot_id]

    for i in range(1, num_parcels + 1):
        pid = f"PKG_{i:04d}"
        dest = rng.choice(customer_locs)
        weight = round(rng.uniform(0.5, 8.0), 1)
        value = round(rng.uniform(10.0, 150.0), 2)
        priority = rng.randint(1, 5)
        deadline = round(rng.uniform(1.0, 12.0), 1)
        parcels.append(Parcel(pid, dest, weight, value, priority, deadline))

    # Realistic vehicle capacity for the batch
    vehicle_capacity = min(100.0, max(20.0, float(num_parcels * 0.4)))

    return locations, parcels, graph, depot_id, vehicle_capacity


def measure_single_dataset(num_parcels: int, num_locations: int, trials: int = 3) -> Dict[str, Any]:
    """
    Benchmarks sorting, knapsack, Dijkstra, and TSP on a given dataset size.
    Returns average execution times in seconds.
    """
    locations, parcels, graph, depot_id, capacity = generate_benchmark_dataset(num_parcels, num_locations)

    sort_times = []
    knap_times = []
    dijkstra_times = []
    tsp_times = []

    for trial in range(trials):
        # 1. Benchmark Merge Sort
        t0 = time.perf_counter()
        sorted_parcels, _ = merge_sort(parcels)
        t_sort = time.perf_counter() - t0
        sort_times.append(t_sort)

        # 2. Benchmark 0/1 Knapsack
        t0 = time.perf_counter()
        knap_res = knapsack_01(sorted_parcels, capacity=capacity, weight_scale=5)
        t_knap = time.perf_counter() - t0
        knap_times.append(t_knap)

        # Identify unique target destinations
        targets: Set[str] = {p.destination_id for p in knap_res.selected_parcels}
        if not targets and len(locations) > 1:
            targets = {locations[1].location_id}

        # 3. Benchmark Dijkstra Shortest Path calculations
        relevant_nodes = set(targets) | {depot_id}
        t0 = time.perf_counter()
        compute_all_pairs_shortest_paths(graph, relevant_nodes)
        t_dijk = time.perf_counter() - t0
        dijkstra_times.append(t_dijk)

        # 4. Benchmark Nearest Neighbor TSP
        t0 = time.perf_counter()
        solve_tsp_nearest_neighbor(graph, depot_id, targets, return_to_depot=True)
        t_tsp = time.perf_counter() - t0
        tsp_times.append(t_tsp)

    avg_sort = sum(sort_times) / trials
    avg_knap = sum(knap_times) / trials
    avg_dijk = sum(dijkstra_times) / trials
    avg_tsp = sum(tsp_times) / trials
    total_time = avg_sort + avg_knap + avg_dijk + avg_tsp

    return {
        "num_parcels": num_parcels,
        "num_locations": num_locations,
        "sorting_sec": avg_sort,
        "knapsack_sec": avg_knap,
        "dijkstra_sec": avg_dijk,
        "tsp_sec": avg_tsp,
        "total_sec": total_time
    }


def run_performance_benchmarks(
    sizes: List[Tuple[int, int]] = None,
    output_csv: str = "results/performance_results.csv",
    output_chart: str = "results/runtime_chart.png"
) -> List[Dict[str, Any]]:
    """
    Executes benchmark across Small (~10), Medium (~100), and Large (~500) inputs.
    Saves CSV and generates comparison chart.
    """
    if sizes is None:
        sizes = [
            (10, 5),     # Small
            (50, 15),    # Small-Medium
            (100, 25),   # Medium
            (250, 40),   # Medium-Large
            (500, 60),   # Large
        ]

    print("\n================================================================================")
    print("                  STARTING DAA ALGORITHM PERFORMANCE BENCHMARK")
    print("================================================================================")
    print(f"{'Parcels':<10} | {'Locations':<10} | {'MergeSort(s)':<14} | {'Knapsack(s)':<14} | {'Dijkstra(s)':<14} | {'TSP(s)':<12} | {'Total(s)':<10}")
    print("-" * 92)

    results = []
    for num_parcels, num_locs in sizes:
        res = measure_single_dataset(num_parcels, num_locs, trials=3)
        results.append(res)
        print(f"{res['num_parcels']:<10} | {res['num_locations']:<10} | "
              f"{res['sorting_sec']:<14.6f} | {res['knapsack_sec']:<14.6f} | "
              f"{res['dijkstra_sec']:<14.6f} | {res['tsp_sec']:<12.6f} | "
              f"{res['total_sec']:<10.6f}")

    print("-" * 92)

    # Save to CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Parcels_N", "Locations_V", "MergeSort_Sec", "Knapsack_Sec", "Dijkstra_Sec", "TSP_Sec", "Total_Sec"])
        for r in results:
            writer.writerow([
                r["num_parcels"],
                r["num_locations"],
                f"{r['sorting_sec']:.6f}",
                f"{r['knapsack_sec']:.6f}",
                f"{r['dijkstra_sec']:.6f}",
                f"{r['tsp_sec']:.6f}",
                f"{r['total_sec']:.6f}"
            ])
    print(f"[+] Performance CSV saved to: {output_csv}")

    # Generate Chart using matplotlib
    try:
        generate_runtime_chart(results, output_chart)
        print(f"[+] Performance runtime chart saved to: {output_chart}")
    except Exception as e:
        print(f"[!] Warning: Could not generate chart: {e}")

    print("================================================================================\n")
    return results


def generate_runtime_chart(results: List[Dict[str, Any]], chart_path: str) -> None:
    """Creates a multi-series comparison chart showing algorithm runtimes vs input size."""
    x = [r["num_parcels"] for r in results]
    sort_y = [r["sorting_sec"] * 1000 for r in results]       # milliseconds
    knap_y = [r["knapsack_sec"] * 1000 for r in results]
    dijk_y = [r["dijkstra_sec"] * 1000 for r in results]
    tsp_y = [r["tsp_sec"] * 1000 for r in results]
    total_y = [r["total_sec"] * 1000 for r in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Subplot 1: Individual Algorithm Scalability
    ax1.plot(x, sort_y, marker="o", color="#1f77b4", label="Merge Sort: O(n log n)", linewidth=2)
    ax1.plot(x, knap_y, marker="s", color="#ff7f0e", label="0/1 Knapsack DP: O(n * W)", linewidth=2)
    ax1.plot(x, dijk_y, marker="^", color="#2ca02c", label="Dijkstra All-Pairs: O(k * (V+E)log V)", linewidth=2)
    ax1.plot(x, tsp_y, marker="d", color="#d62728", label="Nearest Neighbor TSP: O(k^2)", linewidth=2)

    ax1.set_title("Algorithm Execution Runtime vs Dataset Size", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Number of Parcels (N)", fontsize=11)
    ax1.set_ylabel("Execution Time (milliseconds)", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="upper left")

    # Subplot 2: Cumulative Pipeline Runtime
    ax2.plot(x, total_y, marker="o", color="#6a1b9a", label="Total Pipeline Runtime", linewidth=2.5)
    ax2.set_title("Overall Pipeline Latency vs Input Scale", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Number of Parcels (N)", fontsize=11)
    ax2.set_ylabel("Total Latency (milliseconds)", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper left")

    plt.suptitle("Mini-Courier Planner - DAA Performance Empirical Analysis", fontsize=14, fontweight="bold")
    plt.tight_layout()

    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    plt.savefig(chart_path, dpi=200)
    plt.close()


if __name__ == "__main__":
    run_performance_benchmarks()
