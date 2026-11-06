"""
Mini-Courier Planner - Streamlit Web Dashboard
Interactive Visualization of DAA Capstone Algorithms:
- Merge Sort Parcel Prioritization
- 0/1 Knapsack Dynamic Programming Vehicle Packing
- Dijkstra Shortest Paths on Weighted Graph
- Nearest Neighbor TSP Route Sequencing and Graph Visualization
"""

import os
import sys
import tempfile
import pandas as pd
import numpy as np

# Configure matplotlib temporary cache directory
os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.models import Location, Parcel, RoadGraph
from utils.data_loader import load_courier_environment
from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import get_shortest_path, compute_all_pairs_shortest_paths
from algorithms.tsp import solve_tsp_nearest_neighbor
from utils.performance import run_performance_benchmarks

# Page Configuration
st.set_page_config(
    page_title="Mini-Courier Planner | DAA Capstone",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 15px;
        border-left: 4px solid #2563EB;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_base_data():
    """Loads default sample datasets."""
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    locations, parcels, graph = load_courier_environment(data_dir, depot_id="DEPOT", vehicle_capacity=25.0)
    return locations, parcels, graph


def draw_network_graph(graph: RoadGraph, locations: list, depot_id: str, tsp_result=None, highlight_destination: str = None):
    """
    Renders the road network graph using Matplotlib.
    Highlights depot, delivery stops, and planned TSP route if provided.
    """
    fig, ax = plt.subplots(figsize=(10, 7), facecolor="#FAFAFA")
    ax.set_facecolor("#FAFAFA")

    # Fixed clean layout positions for the standard 8 nodes
    fixed_positions = {
        "DEPOT": (0.0, 0.0),
        "LOC_A": (2.0, 3.5),
        "LOC_B": (5.0, 3.8),
        "LOC_C": (8.0, 2.5),
        "LOC_D": (2.5, -2.8),
        "LOC_E": (6.5, 0.0),
        "LOC_F": (9.5, -1.5),
        "LOC_G": (7.5, -3.8)
    }

    # If new nodes exist outside fixed positions, compute circular layout
    pos = {}
    for loc in locations:
        nid = loc.location_id
        if nid in fixed_positions:
            pos[nid] = fixed_positions[nid]
        else:
            angle = len(pos) * (2 * np.pi / len(locations))
            pos[nid] = (5.0 * np.cos(angle), 5.0 * np.sin(angle))

    # Identify TSP tour edges and order
    tsp_edges = set()
    expanded_edges = set()
    if tsp_result and tsp_result.legs:
        for leg in tsp_result.legs:
            # High-level tour connection
            u, v = leg.from_node, leg.to_node
            tsp_edges.add((u, v))
            tsp_edges.add((v, u))
            # Expanded road segments
            seg = leg.segment_path
            for i in range(len(seg) - 1):
                expanded_edges.add((seg[i], seg[i + 1]))
                expanded_edges.add((seg[i + 1], seg[i]))

    # 1. Draw base road network edges
    drawn_edges = set()
    for u in graph.nodes:
        for v, dist in graph.get_neighbors(u).items():
            edge_key = tuple(sorted([u, v]))
            if edge_key not in drawn_edges:
                drawn_edges.add(edge_key)
                x1, y1 = pos[u]
                x2, y2 = pos[v]

                # Check if edge is in active tour
                is_active = (u, v) in expanded_edges

                edge_color = "#DC2626" if is_active else "#9CA3AF"
                edge_width = 3.5 if is_active else 1.5
                edge_alpha = 0.95 if is_active else 0.55
                zorder = 3 if is_active else 1

                ax.plot([x1, x2], [y1, y2], color=edge_color, linewidth=edge_width,
                        alpha=edge_alpha, zorder=zorder,
                        linestyle="-" if is_active else "--")

                # Distance label
                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2
                # Small offset perpendicular to edge
                dx = x2 - x1
                dy = y2 - y1
                length = np.hypot(dx, dy)
                if length > 0:
                    offset_x = -dy / length * 0.22
                    offset_y = dx / length * 0.22
                else:
                    offset_x, offset_y = 0, 0

                bbox_props = dict(boxstyle="round,pad=0.2",
                                  fc="#FFFFFF",
                                  ec=edge_color,
                                  lw=1 if is_active else 0.5,
                                  alpha=0.9)
                ax.text(mid_x + offset_x, mid_y + offset_y, f"{dist:.1f} km",
                        fontsize=8, ha="center", va="center",
                        color="#111827" if is_active else "#6B7280",
                        fontweight="bold" if is_active else "normal",
                        bbox=bbox_props, zorder=4)

    # 2. Draw nodes
    visited_nodes = set(tsp_result.visit_order) if tsp_result else set()

    for loc in locations:
        nid = loc.location_id
        x, y = pos[nid]

        if nid == depot_id:
            node_color = "#10B981"  # Emerald green for depot
            border_color = "#047857"
            size = 900
            shape = "s"  # Square
        elif highlight_destination and nid == highlight_destination:
            node_color = "#F59E0B"  # Amber for targeted destination
            border_color = "#B45309"
            size = 750
            shape = "o"
        elif nid in visited_nodes:
            node_color = "#EF4444"  # Red for visited customer stops
            border_color = "#991B1B"
            size = 700
            shape = "o"
        else:
            node_color = "#60A5FA"  # Light blue for unvisited locations
            border_color = "#1E40AF"
            size = 550
            shape = "o"

        ax.scatter([x], [y], s=size, color=node_color, edgecolors=border_color,
                   linewidth=2.5, marker=shape, zorder=5)

        # Label node ID
        label_text = f"{nid}\n(Depot)" if nid == depot_id else nid
        ax.text(x, y, label_text, fontsize=9, fontweight="bold",
                color="#FFFFFF" if (nid in visited_nodes or nid == depot_id) else "#1E293B",
                ha="center", va="center", zorder=6)

        # Location name below node
        ax.text(x, y - 0.45, loc.location_name, fontsize=7.5,
                color="#374151", ha="center", va="top",
                bbox=dict(boxstyle="round,pad=0.15", fc="#FFFFFF", ec="#E5E7EB", alpha=0.85),
                zorder=4)

    # Legend
    legend_patches = [
        mpatches.Patch(color="#10B981", label="Depot (Warehouse)"),
        mpatches.Patch(color="#EF4444", label="Selected Delivery Stop"),
        mpatches.Patch(color="#60A5FA", label="Other Location"),
        mpatches.Patch(color="#DC2626", label="Active Courier Route")
    ]
    ax.legend(handles=legend_patches, loc="upper right", framealpha=0.92, fontsize=8.5)

    title = "City Logistics Road Network & Real-Time Tour Walk"
    if tsp_result:
        title += f" (Total: {tsp_result.total_distance:.2f} km)"
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)

    ax.axis("off")
    plt.tight_layout()
    return fig


def main_dashboard():
    locations, default_parcels, graph = get_base_data()

    # Header
    st.markdown('<div class="main-title">🚚 Mini-Courier Planner</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Algorithmic Parcel Dispatch & Route Optimization Dashboard | <b>DAA Capstone (ETCCDA302)</b></div>', unsafe_allow_html=True)

    # Sidebar Controls
    st.sidebar.header("⚙️ Dispatch Controls")

    depot_list = [loc.location_id for loc in locations]
    selected_depot = st.sidebar.selectbox("Central Depot / Warehouse", depot_list, index=0)

    vehicle_capacity = st.sidebar.slider(
        "Vehicle Weight Capacity (kg)",
        min_value=5.0,
        max_value=50.0,
        value=25.0,
        step=0.5,
        help="Adjust vehicle payload limit to dynamically recalculate 0/1 Knapsack packing"
    )

    return_trip = st.sidebar.checkbox("Return to Depot after Deliveries", value=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 Implemented Algorithms")
    st.sidebar.markdown("""
    - **Prioritization:** Merge Sort $O(N \\log N)$
    - **Vehicle Packing:** 0/1 Knapsack DP $O(N \\cdot W)$
    - **Shortest Paths:** Dijkstra's Algorithm $O((V+E)\\log V)$
    - **Tour Routing:** Nearest Neighbor TSP $O(K^2)$
    """)

    # --- STEP 1: PARCEL PRIORITIZATION (MERGE SORT) ---
    sorted_parcels, comparisons_count = merge_sort(default_parcels)

    # --- STEP 2: VEHICLE PACKING (0/1 KNAPSACK DP) ---
    knapsack_res = knapsack_01(sorted_parcels, capacity=vehicle_capacity, weight_scale=10)
    selected_ids = {p.parcel_id for p in knapsack_res.selected_parcels}

    # Extract delivery destinations
    selected_destinations = {p.destination_id for p in knapsack_res.selected_parcels}

    # --- STEP 3: ROUTE SEQUENCING (DIJKSTRA + TSP) ---
    tsp_res = solve_tsp_nearest_neighbor(
        graph,
        depot=selected_depot,
        delivery_locations=selected_destinations,
        return_to_depot=return_trip
    )

    # Top KPI Metrics Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Parcels Loaded", f"{len(knapsack_res.selected_parcels)} / {len(default_parcels)}")
    with col2:
        st.metric("Packed Weight", f"{knapsack_res.total_weight:.1f} kg", f"{knapsack_res.capacity_utilization_pct:.1f}% Capacity")
    with col3:
        st.metric("Delivery Revenue", f"₹ {knapsack_res.total_value:,.2f}")
    with col4:
        st.metric("Total Travel Distance", f"{tsp_res.total_distance:.2f} km", f"{len(selected_destinations)} Stops")

    # Main Tabs
    tab_map, tab_sorting, tab_knapsack, tab_dijkstra, tab_tsp, tab_bench, tab_viva = st.tabs([
        "🗺️ Route Map & Graph",
        "📑 1. Merge Sort Prioritization",
        "📦 2. Knapsack Vehicle Packing",
        "⚡ 3. Dijkstra Shortest Paths",
        "🔄 4. Nearest Neighbor TSP Tour",
        "📊 5. Runtime Benchmark",
        "🎓 Viva & Theory"
    ])

    # TAB 1: ROUTE MAP & GRAPH VISUALIZATION
    with tab_map:
        st.subheader("Interactive Road Network & Delivery Tour Walk")
        st.write("Visualizes the road network graph (edges labeled in km). The red path highlights the complete multi-hop courier tour generated using Dijkstra-expanded road segments.")

        fig_map = draw_network_graph(graph, locations, selected_depot, tsp_result=tsp_res)
        st.pyplot(fig_map)

        st.info(f"**Tour Sequence:** `{' ➔ '.join(tsp_res.visit_order)}`\n\n"
                f"**Expanded Road Trajectory:** `{' ➔ '.join(tsp_res.expanded_path)}`")

    # TAB 2: MERGE SORT PRIORITIZATION
    with tab_sorting:
        st.subheader("Parcel Prioritization via Merge Sort")
        st.markdown("""
        **Sorting Rule:**
        1. Higher Priority first (`5 = Urgent ➔ 1 = Low`)
        2. Equal Priority ➔ Earlier delivery deadline first
        3. Equal Priority & Deadline ➔ Deterministic tie-breaker (`parcel_id`)
        """)
        st.caption(f"✓ Manual Divide-and-Conquer Merge Sort performed **{comparisons_count}** comparisons on {len(default_parcels)} items.")

        sort_rows = []
        for rank, p in enumerate(sorted_parcels, 1):
            is_packed = "✅ PACKED" if p.parcel_id in selected_ids else "❌ LEFT BEHIND"
            sort_rows.append({
                "Rank": rank,
                "Parcel ID": p.parcel_id,
                "Destination": p.destination_id,
                "Priority": p.priority,
                "Deadline (hrs)": f"{p.deadline:.1f}",
                "Weight (kg)": f"{p.weight:.1f}",
                "Value (₹)": f"₹ {p.value:.2f}",
                "Dispatch Status": is_packed
            })
        st.dataframe(pd.DataFrame(sort_rows), use_container_width=True)

    # TAB 3: 0/1 KNAPSACK PACKING
    with tab_knapsack:
        st.subheader("Vehicle Packing via 0/1 Knapsack Dynamic Programming")
        st.write(f"Vehicle payload capacity: **{vehicle_capacity:.1f} kg** (scaled integer capacity: `{int(round(vehicle_capacity * 10))}` units).")

        kp_col1, kp_col2 = st.columns([1, 1])
        with kp_col1:
            st.markdown("#### Selected Parcels (Van Manifest)")
            if knapsack_res.selected_parcels:
                manifest_data = [{
                    "Parcel ID": p.parcel_id,
                    "Destination": p.destination_id,
                    "Weight (kg)": p.weight,
                    "Value (₹)": f"₹ {p.value:.2f}",
                    "Priority": p.priority
                } for p in knapsack_res.selected_parcels]
                st.dataframe(pd.DataFrame(manifest_data), use_container_width=True)
            else:
                st.warning("No parcels fit within current capacity.")

        with kp_col2:
            st.markdown("#### Packing Efficiency")
            st.progress(min(1.0, knapsack_res.total_weight / max(1.0, vehicle_capacity)))
            st.markdown(f"""
            - **Capacity Used:** {knapsack_res.total_weight:.1f} / {vehicle_capacity:.1f} kg ({knapsack_res.capacity_utilization_pct:.1f}%)
            - **Remaining Payload:** {max(0.0, vehicle_capacity - knapsack_res.total_weight):.1f} kg
            - **Total Parcels Chosen:** {len(knapsack_res.selected_parcels)} items
            - **Total Value Generated:** ₹ {knapsack_res.total_value:,.2f}
            """)

        with st.expander("🔍 View Dynamic Programming Table (Sample Columns)"):
            st.text(knapsack_res.format_table_summary(max_cols=14))

    # TAB 4: DIJKSTRA SHORTEST PATHS
    with tab_dijkstra:
        st.subheader(f"Single-Source Shortest Paths from Depot ('{selected_depot}')")
        st.write("Computed using custom Min-Heap Dijkstra's Algorithm ($O((V+E)\\log V)$).")

        dijkstra_rows = []
        for loc in locations:
            if loc.location_id != selected_depot:
                dist, path = get_shortest_path(graph, selected_depot, loc.location_id)
                dijkstra_rows.append({
                    "Target Destination": loc.location_id,
                    "Location Name": loc.location_name,
                    "Shortest Distance (km)": f"{dist:.2f} km" if dist < float("inf") else "UNREACHABLE",
                    "Road Path Sequence": " ➔ ".join(path) if path else "None"
                })
        st.dataframe(pd.DataFrame(dijkstra_rows), use_container_width=True)

    # TAB 5: NEAREST NEIGHBOR TSP TOUR
    with tab_tsp:
        st.subheader("Nearest Neighbor TSP Delivery Tour")
        st.markdown(f"**Stop Sequence:** `{' ➔ '.join(tsp_res.visit_order)}`")

        if tsp_res.legs:
            leg_rows = []
            for i, leg in enumerate(tsp_res.legs, 1):
                leg_rows.append({
                    "Leg #": i,
                    "From Stop": leg.from_node,
                    "To Stop": leg.to_node,
                    "Leg Distance (km)": f"{leg.distance:.2f} km",
                    "Turn-by-Turn Road Segments": " ➔ ".join(leg.segment_path)
                })
            st.dataframe(pd.DataFrame(leg_rows), use_container_width=True)
            st.success(f"**Total Courier Trip Distance:** {tsp_res.total_distance:.2f} km across {len(tsp_res.legs)} legs.")
        else:
            st.info("No delivery destinations scheduled.")

    # TAB 6: PERFORMANCE BENCHMARK
    with tab_bench:
        st.subheader("Empirical Algorithm Runtime Scaling")
        st.write("Measures execution times across 5 dataset sizes using Python's `time.perf_counter()`.")

        csv_path = os.path.join(os.path.dirname(__file__), "results", "performance_results.csv")
        chart_path = os.path.join(os.path.dirname(__file__), "results", "runtime_chart.png")

        if os.path.exists(csv_path):
            bench_df = pd.read_csv(csv_path)
            st.dataframe(bench_df, use_container_width=True)

        if os.path.exists(chart_path):
            st.image(chart_path, caption="Algorithm Execution Latencies across Dataset Scales (N=10 to 500)")

        if st.button("🚀 Re-run Live Benchmark"):
            with st.spinner("Running performance benchmarks across multiple input sizes..."):
                run_performance_benchmarks()
            st.success("Benchmarks completed and updated!")
            st.rerun()

    # TAB 7: VIVA & THEORY
    with tab_viva:
        st.subheader("DAA Capstone Viva Voce Preparation")
        viva_file = os.path.join(os.path.dirname(__file__), "docs", "viva_questions.md")
        if os.path.exists(viva_file):
            with open(viva_file, "r", encoding="utf-8") as f:
                viva_content = f.read()
            st.markdown(viva_content)


if __name__ == "__main__":
    main_dashboard()

