"""
🗺️ Smart Indoor Navigation
NetworkX shortest-path algorithm with Plotly visualization.
NO Groq API calls — fully deterministic, works offline.
"""
import streamlit as st
import plotly.graph_objects as go
import networkx as nx

from utils.ui_helpers import inject_custom_css, page_header, info_card, sidebar_brand, plotly_dark_layout
from utils.navigation_graph import (
    build_graph, get_shortest_path,
    NODE_COLORS, NODE_SYMBOLS, all_node_options, node_display_name,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Navigation | Smart Stadium",
    page_icon="🗺️",
    layout="wide",
)
inject_custom_css()
sidebar_brand()
page_header(
    "Smart Indoor Navigation",
    "Dijkstra shortest-path routing across the stadium — no AI required",
    "🗺️",
)

# ── Build graph (cached) ───────────────────────────────────────────────────────
G: nx.Graph = build_graph()
node_options = all_node_options(G)  # [(node_id, label), ...]
labels_to_id = {label: nid for nid, label in node_options}
id_to_label  = {nid: label for nid, label in node_options}
display_labels = [label for _, label in node_options]

# ── Controls ───────────────────────────────────────────────────────────────────
st.markdown("### Route Planner")
col_from, col_to, col_btn = st.columns([2, 2, 1])
with col_from:
    from_label = st.selectbox(
        "📍 Start Location", display_labels, index=0, key="nav_from",
        help="Select your current location inside the stadium",
    )
with col_to:
    # Default to a different node
    default_to_idx = min(15, len(display_labels) - 1)
    to_label = st.selectbox(
        "🎯 Destination", display_labels, index=default_to_idx, key="nav_to",
        help="Select where you want to go — the shortest walking route will be calculated",
    )
with col_btn:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    find_route = st.button(
        "Find Route →", key="btn_find_route", use_container_width=True,
        help="Calculate the shortest walking path between your selected locations",
    )

source_id = labels_to_id.get(from_label, "")
target_id = labels_to_id.get(to_label, "")

# Compute path on button press or whenever source/target change
path_nodes, total_dist = None, None
if source_id and target_id:
    path_nodes, total_dist = get_shortest_path(G, source_id, target_id)

# ── Route Result ───────────────────────────────────────────────────────────────
if path_nodes is not None:
    path_set = set(zip(path_nodes[:-1], path_nodes[1:]))  # edges on path

    if total_dist == 0:
        st.info("ℹ️ You are already at the destination.")
    else:
        est_min = round(total_dist / 80, 1)   # ~80 m/min walking pace
        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("🛣️ Total Distance", f"{total_dist:.0f} m")
        col_r2.metric("⏱️ Est. Walking Time", f"~{est_min} min")
        col_r3.metric("🔢 Steps / Waypoints", len(path_nodes))

        st.markdown("**Step-by-step directions:**")
        for i, nid in enumerate(path_nodes):
            icon = NODE_SYMBOLS.get(G.nodes[nid].get("type", ""), "📍")
            prefix = "🟢 START" if i == 0 else ("🏁 END" if i == len(path_nodes) - 1 else f"  {i}.")
            if i < len(path_nodes) - 1:
                edge_dist = G.edges[nid, path_nodes[i + 1]].get("distance", 0)
                st.markdown(
                    f"{prefix} &nbsp; {icon} **{node_display_name(G, nid)}** "
                    f"→ *walk {edge_dist:.0f} m*"
                )
            else:
                st.markdown(f"{prefix} &nbsp; {icon} **{node_display_name(G, nid)}**")
elif source_id and target_id:
    st.warning("⚠️ No walkable path found between those two locations.")

st.markdown("---")

# ── Plotly Graph Visualisation ─────────────────────────────────────────────────
st.subheader("Stadium Navigation Map")

# Build edge traces
edge_x, edge_y = [], []
path_edge_x, path_edge_y = [], []

for u, v, data in G.edges(data=True):
    xu, yu = G.nodes[u]["x"], G.nodes[u]["y"]
    xv, yv = G.nodes[v]["x"], G.nodes[v]["y"]
    # Regular edge
    edge_x += [xu, xv, None]
    edge_y += [yu, yv, None]
    # Path edge
    if path_nodes and ((u, v) in path_set or (v, u) in path_set):
        path_edge_x += [xu, xv, None]
        path_edge_y += [yu, yv, None]

fig = go.Figure()

# Background edges (grey)
fig.add_trace(go.Scatter(
    x=edge_x, y=edge_y,
    mode="lines",
    line=dict(color="#2d3748", width=1.5),
    hoverinfo="none",
    name="Corridors",
    showlegend=False,
))

# Highlighted path edges (bright blue)
if path_nodes and path_edge_x:
    fig.add_trace(go.Scatter(
        x=path_edge_x, y=path_edge_y,
        mode="lines",
        line=dict(color="#00d4ff", width=4),
        hoverinfo="none",
        name="Shortest Path",
        showlegend=True,
    ))

# Add nodes by type
node_types_present = set(nx.get_node_attributes(G, "type").values())
path_set_nodes = set(path_nodes) if path_nodes else set()

for ntype in node_types_present:
    nids  = [n for n, d in G.nodes(data=True) if d.get("type") == ntype]
    xs    = [G.nodes[n]["x"] for n in nids]
    ys    = [G.nodes[n]["y"] for n in nids]
    names = [G.nodes[n]["name"] for n in nids]
    color = NODE_COLORS.get(ntype, "#94a3b8")

    # Split into path nodes and non-path nodes to avoid mixed marker.line dicts
    path_nids     = [n for n in nids if n in path_set_nodes]
    nonpath_nids  = [n for n in nids if n not in path_set_nodes]

    for subset, is_on_path in [(nonpath_nids, False), (path_nids, True)]:
        if not subset:
            continue
        sx = [G.nodes[n]["x"] for n in subset]
        sy = [G.nodes[n]["y"] for n in subset]
        sn = [G.nodes[n]["name"] for n in subset]
        fig.add_trace(go.Scatter(
            x=sx, y=sy,
            mode="markers+text",
            name=ntype.capitalize(),
            showlegend=(not is_on_path),   # only legend entry for non-path group
            marker=dict(
                size=18 if is_on_path else 11,
                color=color,
                line=dict(width=3 if is_on_path else 1,
                          color="#ffffff" if is_on_path else "#0a0e1a"),
                symbol="circle",
            ),
            text=[NODE_SYMBOLS.get(ntype, "")] * len(subset),
            textposition="middle center",
            hovertext=[f"<b>{nm}</b><br>Type: {ntype}" for nm in sn],
            hoverinfo="text",
        ))

# Mark START and END with large pins if path exists
if path_nodes and len(path_nodes) >= 2:
    for marker_node, label, color in [
        (path_nodes[0],  "START", "#10b981"),
        (path_nodes[-1], "END",   "#ef4444"),
    ]:
        fig.add_trace(go.Scatter(
            x=[G.nodes[marker_node]["x"]],
            y=[G.nodes[marker_node]["y"]],
            mode="markers+text",
            marker=dict(size=26, color=color, symbol="star",
                        line=dict(width=2, color="#ffffff")),
            text=[label],
            textposition="top center",
            textfont=dict(color=color, size=10, family="Inter"),
            hoverinfo="skip",
            showlegend=False,
        ))

plotly_dark_layout(fig, "Indoor Stadium Navigation Graph", height=560)
fig.update_xaxes(range=[-5, 105], showgrid=False, showticklabels=False, title="")
fig.update_yaxes(range=[-5, 105], showgrid=False, showticklabels=False, title="")
fig.update_layout(legend=dict(
    bgcolor="#1a1f35", bordercolor="#2d3748",
    orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1,
))
st.plotly_chart(fig, use_container_width=True)

# ── Legend ─────────────────────────────────────────────────────────────────────
st.markdown("**Node Types**")
legend_cols = st.columns(len(NODE_COLORS))
for col, (ntype, color) in zip(legend_cols, NODE_COLORS.items()):
    col.markdown(
        f'<div style="display:flex;align-items:center;gap:6px;">'
        f'<div style="width:12px;height:12px;border-radius:50%;background:{color};"></div>'
        f'<span style="font-size:0.75rem;color:#94a3b8;">{ntype.capitalize()}</span></div>',
        unsafe_allow_html=True,
    )

info_card(
    "How it works",
    "This navigator uses <b>NetworkX Dijkstra's shortest-path algorithm</b> on a weighted graph "
    "where edge weights represent walking distances in metres. No AI is involved — "
    "the route is computed in milliseconds entirely on the server.",
    "ℹ️", "#8b5cf6",
)

