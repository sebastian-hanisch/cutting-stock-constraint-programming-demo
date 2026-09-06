"""Plotly-Suchbaum, Portierung der Muster aus csbb_visualization.py/
cscp_visualization.py - erweitert um den `prune_infeasible`-Status (nur im
Baseline-Vergleich sichtbar, im Hauptbaum mit Propagation strukturell
unerreichbar) und einen `grade_excluded`-Marker (petrol, analog zu den
Marker-Mustern der vorherigen Stücke dieser Linie)."""

STATUS_STYLE = {
    "root": {"color": "#14233B", "label": "Start"},
    "branch": {"color": "#1f77b4", "label": "Verzweigt (weiter untersucht)"},
    "prune_bound": {"color": "#d68a2e", "label": "Gestutzt (Bound zu schwach)"},
    "prune_infeasible": {"color": "#c0392b", "label": "Verschwendet (Materialsorte unzulässig)"},
    "leaf_new_best": {"color": "#2ca02c", "label": "Neue beste Lösung"},
    "leaf_not_best": {"color": "#c4cbd8", "label": "Vollständig, nicht besser"},
}
STATUS_ORDER = ["root", "branch", "prune_bound", "prune_infeasible", "leaf_new_best", "leaf_not_best"]
GRADE_EXCLUDED_COLOR = "#137a6b"


def _compute_layout(nodes):
    by_id = {n.id: n for n in nodes}
    children = {}
    for n in nodes:
        if n.parent_id is not None:
            children.setdefault(n.parent_id, []).append(n.id)

    x_of = {}
    next_leaf_slot = [0]

    def assign(node_id):
        kids = children.get(node_id, [])
        if not kids:
            x_of[node_id] = next_leaf_slot[0]
            next_leaf_slot[0] += 1
            return x_of[node_id]
        xs = [assign(k) for k in kids]
        x_of[node_id] = sum(xs) / len(xs)
        return x_of[node_id]

    assign(nodes[0].id)
    return {nid: (x_of[nid], -by_id[nid].depth) for nid in x_of}


def _node_label(node):
    if node.status == "root":
        return "Start<br>noch kein Stück platziert"

    kind, idx = node.target
    placement = f"Neues Bin {idx + 1} geöffnet" if kind == "new" else f"In Bin {idx + 1} gelegt"
    label = f"Stück (Breite {node.piece_width}, Sorte {node.piece_grade}) - {placement}"
    if node.status == "prune_infeasible":
        label += "<br><b>Verschwendet: Materialsorte hier unzulässig</b>"
        return label
    label += f"<br>Offene Bins: {node.bins_open}"
    if node.bound is not None:
        label += f"<br>Schranke: {node.bound}"
    if node.grade_excluded > 0:
        label += (
            f"<br><b>×{node.grade_excluded} Bin(s) per Materialsorte ausgeschlossen</b>"
        )
    return label


def build_tree_figure(result, step, render_cap):
    import plotly.graph_objects as go

    layout_nodes = list(result.nodes)[:render_cap]
    layout = _compute_layout(layout_nodes)
    nodes = [n for n in layout_nodes if n.id <= step]
    rendered_ids = {n.id for n in nodes}

    fig = go.Figure()

    edge_x, edge_y = [], []
    for n in nodes:
        if n.parent_id is not None and n.parent_id in rendered_ids:
            x0, y0 = layout[n.parent_id]
            x1, y1 = layout[n.id]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(color="#c4cbd8", width=1.5), hoverinfo="skip", showlegend=False))

    for status in STATUS_ORDER:
        group = [n for n in nodes if n.status == status]
        if not group:
            continue
        style = STATUS_STYLE[status]
        xs = [layout[n.id][0] for n in group]
        ys = [layout[n.id][1] for n in group]
        texts = [_node_label(n) for n in group]
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="markers", name=style["label"],
                marker=dict(size=11 if status != "leaf_new_best" else 15, color=style["color"],
                            line=dict(width=1, color="white"),
                            symbol="x" if status == "prune_infeasible" else ("star" if status == "leaf_new_best" else "circle")),
                hovertext=texts, hoverinfo="text",
            )
        )

    excl_group = [n for n in nodes if n.grade_excluded > 0]
    if excl_group:
        xs = [layout[n.id][0] for n in excl_group]
        ys = [layout[n.id][1] for n in excl_group]
        texts = [_node_label(n) for n in excl_group]
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="markers", name="Materialsorte schloss hier Bins aus",
                marker=dict(size=20, color="rgba(0,0,0,0)", line=dict(width=2.5, color=GRADE_EXCLUDED_COLOR)),
                hovertext=texts, hoverinfo="text",
            )
        )

    fig.update_layout(
        template="plotly_white", height=460,
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=40, l=10, r=10, b=10),
    )
    return fig


def build_comparison_chart(comparison):
    import plotly.graph_objects as go

    labels = ["Baseline (mit verschwendeten Knoten)", "Mit Propagation"]
    values = [comparison["baseline_nodes"], comparison["propagation_nodes"]]
    colors = ["#c4cbd8", "#137a6b"]
    fig = go.Figure(
        go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:,}" for v in values], textposition="outside")
    )
    fig.update_layout(
        template="plotly_white", height=360,
        yaxis=dict(title="Anzahl besuchter Knoten"),
        margin=dict(t=30, l=10, r=10, b=10),
        showlegend=False,
    )
    return fig
