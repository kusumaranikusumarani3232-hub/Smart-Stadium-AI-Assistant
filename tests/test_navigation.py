"""
tests/test_navigation.py
========================
Unit tests for utils/navigation_graph.py

Tests only the *pure Python* functions that do NOT require a Streamlit session:
  - get_shortest_path()
  - node_display_name()
  - all_node_options()
  - NODE_COLORS / NODE_SYMBOLS dictionaries

The `build_graph()` function is decorated with @st.cache_resource and requires a
Streamlit runtime, so it is NOT tested here — instead we use the `simple_graph`
fixture from conftest.py as a drop-in replacement.
"""
import pytest
import networkx as nx

from utils.navigation_graph import (
    get_shortest_path,
    node_display_name,
    all_node_options,
    NODE_COLORS,
    NODE_SYMBOLS,
)


# ── get_shortest_path ──────────────────────────────────────────────────────────

class TestGetShortestPath:
    """Tests for get_shortest_path(G, source, target)."""

    def test_same_node_returns_zero_distance(self, simple_graph):
        """When source == target the path is [source] and distance is 0.0."""
        path, dist = get_shortest_path(simple_graph, "A", "A")
        assert path == ["A"]
        assert dist == 0.0

    def test_missing_source_returns_none(self, simple_graph):
        """A node_id that doesn't exist in the graph returns (None, None)."""
        path, dist = get_shortest_path(simple_graph, "MISSING", "C")
        assert path is None
        assert dist is None

    def test_missing_target_returns_none(self, simple_graph):
        """A target node_id that doesn't exist returns (None, None)."""
        path, dist = get_shortest_path(simple_graph, "A", "MISSING")
        assert path is None
        assert dist is None

    def test_both_missing_returns_none(self, simple_graph):
        """Both nodes missing → (None, None)."""
        path, dist = get_shortest_path(simple_graph, "FOO", "BAR")
        assert path is None
        assert dist is None

    def test_disconnected_node_returns_none(self, simple_graph):
        """Node X is isolated — no path from A to X."""
        path, dist = get_shortest_path(simple_graph, "A", "X")
        assert path is None
        assert dist is None

    def test_valid_direct_edge(self, simple_graph):
        """A→B is a direct edge of weight 10."""
        path, dist = get_shortest_path(simple_graph, "A", "B")
        assert path == ["A", "B"]
        assert dist == 10.0

    def test_valid_multi_hop_path(self, simple_graph):
        """A→C requires going through B: total distance 10+20=30."""
        path, dist = get_shortest_path(simple_graph, "A", "C")
        assert path == ["A", "B", "C"]
        assert dist == 30.0

    def test_path_uses_shortest_route(self, simple_graph):
        """A→D: via B is 10+15=25; no direct edge so must use B."""
        path, dist = get_shortest_path(simple_graph, "A", "D")
        assert path == ["A", "B", "D"]
        assert dist == 25.0

    def test_distance_is_rounded_to_one_decimal(self, simple_graph):
        """The returned distance is rounded to 1 decimal place."""
        _, dist = get_shortest_path(simple_graph, "A", "B")
        # 10.0 has at most 1 decimal digit
        assert isinstance(dist, float)
        assert dist == round(dist, 1)


# ── node_display_name ──────────────────────────────────────────────────────────

class TestNodeDisplayName:
    """Tests for node_display_name(G, node_id)."""

    def test_known_node_returns_name_attribute(self, simple_graph):
        """For a node in the graph, return its 'name' attribute."""
        assert node_display_name(simple_graph, "A") == "Node A"
        assert node_display_name(simple_graph, "C") == "Node C"

    def test_unknown_node_returns_node_id(self, simple_graph):
        """For a node_id NOT in the graph, return the raw node_id string."""
        result = node_display_name(simple_graph, "GHOST_NODE")
        assert result == "GHOST_NODE"


# ── all_node_options ───────────────────────────────────────────────────────────

class TestAllNodeOptions:
    """Tests for all_node_options(G)."""

    def test_returns_list_of_tuples(self, simple_graph):
        """Result is a list of (node_id, label) tuples."""
        opts = all_node_options(simple_graph)
        assert isinstance(opts, list)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in opts)

    def test_all_nodes_represented(self, simple_graph):
        """Every node in the graph appears in the output."""
        opts = all_node_options(simple_graph)
        node_ids = {nid for nid, _ in opts}
        assert node_ids == set(simple_graph.nodes)

    def test_labels_are_sorted(self, simple_graph):
        """The list must be sorted alphabetically by display label."""
        opts = all_node_options(simple_graph)
        labels = [label for _, label in opts]
        assert labels == sorted(labels)

    def test_label_contains_node_name(self, simple_graph):
        """Each label string should contain the node's human-readable name."""
        opts = all_node_options(simple_graph)
        name_map = dict(simple_graph.nodes(data="name"))
        for nid, label in opts:
            assert name_map[nid] in label


# ── NODE_COLORS / NODE_SYMBOLS ─────────────────────────────────────────────────

class TestNodeColorSymbolDicts:
    """Sanity checks on the colour and symbol lookup dictionaries."""

    EXPECTED_TYPES = {
        "entrance", "circulation", "seating", "premium",
        "media", "amenity", "emergency", "service", "restroom",
    }

    def test_node_colors_covers_all_types(self):
        """NODE_COLORS must have an entry for every expected node type."""
        assert self.EXPECTED_TYPES == set(NODE_COLORS.keys())

    def test_node_colors_are_hex_strings(self):
        """Every colour value must be a 7-char hex string starting with '#'."""
        for ntype, color in NODE_COLORS.items():
            assert isinstance(color, str), f"{ntype} colour is not a string"
            assert color.startswith("#") and len(color) == 7, (
                f"{ntype} colour '{color}' is not a valid 7-char hex"
            )

    def test_node_symbols_are_strings(self):
        """Every symbol in NODE_SYMBOLS must be a non-empty string."""
        for ntype, symbol in NODE_SYMBOLS.items():
            assert isinstance(symbol, str) and len(symbol) > 0, (
                f"Symbol for {ntype!r} is empty or not a string"
            )
