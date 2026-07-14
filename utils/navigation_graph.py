"""
Stadium indoor navigation graph built with NetworkX.
Uses Dijkstra shortest-path algorithm — NO Groq API calls.
"""
from __future__ import annotations

import pandas as pd
import networkx as nx
import streamlit as st

from utils.data_loader import load_navigation_nodes


# ── Node type → display colour (for Plotly) ────────────────────────────────────
NODE_COLORS: dict[str, str] = {
    "entrance":    "#00d4ff",
    "circulation": "#8b5cf6",
    "seating":     "#10b981",
    "premium":     "#f59e0b",
    "media":       "#e879f9",
    "amenity":     "#fb923c",
    "emergency":   "#ef4444",
    "service":     "#64748b",
    "restroom":    "#475569",
}

NODE_SYMBOLS: dict[str, str] = {
    "entrance":    "🚪",
    "seating":     "🪑",
    "premium":     "⭐",
    "amenity":     "🍔",
    "emergency":   "🏥",
    "service":     "ℹ️",
    "restroom":    "🚻",
    "circulation": "🔀",
    "media":       "📹",
}


@st.cache_resource(show_spinner=False)
def build_graph() -> nx.Graph:
    """
    Build and cache a NetworkX undirected weighted graph from navigation_nodes.csv.

    Edge weights are walking distances in metres.
    The graph is cached as a Streamlit resource so it is only built once per session.
    """
    nodes_df: pd.DataFrame = load_navigation_nodes()
    G: nx.Graph = nx.Graph()

    # Add nodes with metadata
    for _, row in nodes_df.iterrows():
        G.add_node(
            row["node_id"],
            name=row["name"],
            type=row["type"],
            x=float(row["x"]),
            y=float(row["y"]),
        )

    # Add edges from the pipe-separated 'neighbors' column
    for _, row in nodes_df.iterrows():
        src = row["node_id"]
        if pd.isna(row["neighbors"]) or not str(row["neighbors"]).strip():
            continue
        for entry in str(row["neighbors"]).split("|"):
            entry = entry.strip()
            if ":" not in entry:
                continue
            dst, dist_str = entry.rsplit(":", 1)
            dst = dst.strip()
            try:
                dist = float(dist_str.strip())
            except ValueError:
                continue
            # add_edge is idempotent for the same pair — no duplicate edges
            G.add_edge(src, dst, distance=dist)

    return G


def get_shortest_path(
    G: nx.Graph,
    source: str,
    target: str,
) -> tuple[list[str] | None, float | None]:
    """
    Compute the shortest walking path between two nodes using Dijkstra.

    Returns:
        (path, total_distance_metres)  — both None if no path exists.
    """
    if source not in G or target not in G:
        return None, None
    if source == target:
        return [source], 0.0
    try:
        path: list[str] = nx.shortest_path(G, source, target, weight="distance")
        dist: float = nx.shortest_path_length(G, source, target, weight="distance")
        return path, round(dist, 1)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None, None


def node_display_name(G: nx.Graph, node_id: str) -> str:
    """Return the human-readable name for a node ID."""
    return G.nodes[node_id].get("name", node_id) if node_id in G else node_id


def all_node_options(G: nx.Graph) -> list[tuple[str, str]]:
    """Return list of (node_id, display_label) sorted by display label."""
    options = [
        (nid, f"{NODE_SYMBOLS.get(data.get('type',''), '📍')}  {data.get('name', nid)}")
        for nid, data in G.nodes(data=True)
    ]
    return sorted(options, key=lambda x: x[1])
