import base64
import hashlib
from typing import Any

import dash
import dash_cytoscape as cyto
from dash import Input, Output, State, dcc, html

import dijkstra
import graph_utils
import kosaraju
import loader
import markov
import path_finder

_GRAPH_CACHE: dict[str, dict[str, Any]] = {}

SCC_COLORS = ["#e63946", "#f4a261", "#e9c46a", "#2a9d8f", "#264653", "#9d4edd", "#ff6b6b", "#06d6a0", "#118ab2", "#7209b7"]
PATH_COLOR = "#e63946"
DEFAULT_NODE_COLOR = "#4a5568"
DEFAULT_EDGE_COLOR = "#cbd5e0"

STYLESHEET = [
  {"selector": "node", "style": {
    "label": "data(label)",
    "background-color": DEFAULT_NODE_COLOR,
    "color": "#fff",
    "text-valign": "center",
    "text-halign": "center",
    "font-size": "11px",
    "width": 28,
    "height": 28,
    "text-outline-width": 1,
    "text-outline-color": DEFAULT_NODE_COLOR,
  }},
  {"selector": "edge", "style": {
    "width": "mapData(weight, 1, 20, 1, 8)",
    "line-color": DEFAULT_EDGE_COLOR,
    "target-arrow-color": DEFAULT_EDGE_COLOR,
    "target-arrow-shape": "triangle",
    "curve-style": "bezier",
    "arrow-scale": 0.8,
    "label": "data(label)",
    "font-size": "8px",
    "color": "#94a3b8",
    "text-rotation": "autorotate",
    "text-background-color": "#fff",
    "text-background-opacity": 0.7,
    "text-background-padding": 1,
  }},
  {"selector": ".path", "style": {
    "background-color": PATH_COLOR,
    "text-outline-color": PATH_COLOR,
    "line-color": PATH_COLOR,
    "target-arrow-color": PATH_COLOR,
    "width": 36,
    "height": 36,
  }},
  {"selector": "edge.path", "style": {
    "width": 4,
    "label": "data(label)",
    "font-size": "10px",
    "color": "#222",
    "text-background-color": "#fff",
    "text-background-opacity": 0.8,
    "text-background-padding": 2,
  }},
] + [
  {"selector": f".scc-{i}", "style": {
    "background-color": color,
    "text-outline-color": color,
  }} for i, color in enumerate(SCC_COLORS)
]

PARAM_STYLE = {"display": "block", "marginBottom": "16px"}
HIDDEN = {"display": "none"}
LABEL_STYLE = {"display": "block", "fontSize": "12px", "fontWeight": "600", "marginBottom": "4px", "color": "#4a5568"}
INPUT_STYLE = {"width": "100%", "padding": "6px 8px", "border": "1px solid #cbd5e0", "borderRadius": "4px"}

app = dash.Dash(__name__, title="Lexigraph")

app.layout = html.Div(style={"fontFamily": "system-ui, sans-serif", "maxWidth": "1400px", "margin": "0 auto", "padding": "20px"}, children=[
  html.H1("Lexigraph", style={"marginBottom": "4px"}),
  html.Div("Upload a text corpus and explore its word graph.", style={"color": "#666", "marginBottom": "20px"}),

  dcc.Upload(
    id="upload-corpus",
    children=html.Div(["Drag and drop or ", html.A("select a .txt file", style={"color": "#3182ce", "textDecoration": "underline"})]),
    style={
      "borderWidth": "2px", "borderStyle": "dashed", "borderColor": "#cbd5e0",
      "borderRadius": "8px", "padding": "30px", "textAlign": "center",
      "cursor": "pointer", "marginBottom": "16px",
    },
    multiple=False,
  ),
  dcc.Loading(html.Div(id="corpus-info", style={"marginBottom": "20px", "padding": "12px", "background": "#f7fafc", "borderRadius": "6px", "minHeight": "20px"})),
  dcc.Store(id="corpus-hash"),

  html.Div(style={"display": "flex", "gap": "20px"}, children=[
    html.Div(style={"width": "300px", "flexShrink": 0, "padding": "16px", "background": "#f7fafc", "borderRadius": "8px"}, children=[
      html.Label("Mode", style=LABEL_STYLE),
      dcc.RadioItems(
        id="mode",
        options=[
          {"label": "Full graph", "value": "full_graph"},
          {"label": "Dijkstra (shortest path)", "value": "dijkstra"},
          {"label": "Strongly connected components", "value": "scc"},
          {"label": "Markov chain", "value": "markov"},
          {"label": "Top phrases", "value": "top_phrases"},
        ],
        value="full_graph",
        labelStyle={"display": "block", "marginBottom": "4px"},
        style={"marginBottom": "20px"},
      ),

      html.Div(id="params-full_graph", style=PARAM_STYLE, children=[
        html.Label("Minimum edge weight", style=LABEL_STYLE),
        dcc.Slider(id="full-min-weight", min=1, max=10, step=1, value=2, marks={i: str(i) for i in range(1, 11)}),
        html.Div(style={"height": "12px"}),
        dcc.Checklist(id="full-drop-isolates", options=[{"label": " Hide isolated nodes", "value": "on"}], value=["on"]),
      ]),

      html.Div(id="params-dijkstra", style=HIDDEN, children=[
        html.Label("Source word", style=LABEL_STYLE),
        dcc.Dropdown(id="dijkstra-source", placeholder="Upload a corpus first", options=[], searchable=True, clearable=True),
        html.Div(style={"height": "12px"}),
        html.Label("Target word", style=LABEL_STYLE),
        dcc.Dropdown(id="dijkstra-target", placeholder="Upload a corpus first", options=[], searchable=True, clearable=True),
        html.Div("Words ranked by total edge weight (most-connected first).", style={"color": "#666", "fontSize": "11px", "marginTop": "8px"}),
      ]),

      html.Div(id="params-scc", style=HIDDEN, children=[
        html.Label("Edge weight threshold", style=LABEL_STYLE),
        dcc.Slider(id="scc-min-weight", min=1, max=10, step=1, value=2, marks={i: str(i) for i in range(1, 11)}),
      ]),

      html.Div(id="params-markov", style=HIDDEN, children=[
        html.Label("Start word", style=LABEL_STYLE),
        dcc.Dropdown(id="markov-start", placeholder="Upload a corpus first", options=[], searchable=True, clearable=True),
        html.Div(style={"height": "12px"}),
        html.Label("Length", style=LABEL_STYLE),
        dcc.Input(id="markov-length", type="number", value=20, min=2, max=200, style=INPUT_STYLE, debounce=True),
        html.Div(style={"height": "12px"}),
        html.Button("Re-roll", id="markov-reroll", n_clicks=0, style={"padding": "6px 12px", "cursor": "pointer"}),
        html.Div("Words from the raw graph (stopwords kept).", style={"color": "#666", "fontSize": "11px", "marginTop": "8px"}),
      ]),

      html.Div(id="params-top_phrases", style=HIDDEN, children=[
        html.Label("Start word", style=LABEL_STYLE),
        dcc.Dropdown(id="top-start", placeholder="Upload a corpus first", options=[], searchable=True, clearable=True),
        html.Div(style={"height": "12px"}),
        html.Label("Path length (k)", style=LABEL_STYLE),
        dcc.Input(id="top-k", type="number", value=3, min=2, max=8, style=INPUT_STYLE, debounce=True),
        html.Div(style={"height": "12px"}),
        html.Label("Top N", style=LABEL_STYLE),
        dcc.Input(id="top-n", type="number", value=5, min=1, max=20, style=INPUT_STYLE, debounce=True),
      ]),
    ]),

    html.Div(style={"flex": 1, "minWidth": 0}, children=[
      dcc.Loading(cyto.Cytoscape(
        id="graph",
        layout={"name": "cose", "animate": False},
        style={"height": "600px", "width": "100%", "border": "1px solid #e2e8f0", "borderRadius": "8px", "background": "#fff"},
        elements=[],
        stylesheet=STYLESHEET,
      )),
      html.Div(id="results", style={"marginTop": "20px"}),
    ]),
  ]),
])


# Toggle param panel visibility
@app.callback(
  [Output(f"params-{m}", "style") for m in ("full_graph", "dijkstra", "scc", "markov", "top_phrases")],
  Input("mode", "value"),
)
def toggle_panels(mode):
  modes = ("full_graph", "dijkstra", "scc", "markov", "top_phrases")
  return [PARAM_STYLE if m == mode else HIDDEN for m in modes]


@app.callback(
  Output("corpus-info", "children"),
  Output("corpus-hash", "data"),
  Input("upload-corpus", "contents"),
  State("upload-corpus", "filename"),
  prevent_initial_call=True,
)
def on_upload(contents, filename):
  if not contents:
    return dash.no_update, dash.no_update

  _, b64 = contents.split(",", 1)
  raw = base64.b64decode(b64)
  try:
    text = raw.decode("utf-8")
  except UnicodeDecodeError:
    text = raw.decode("latin-1")

  digest = hashlib.sha1(raw).hexdigest()

  if digest not in _GRAPH_CACHE:
    clean = loader.loader_clean_from_text(text)
    raw_g = loader.loader_raw_from_text(text)
    _GRAPH_CACHE[digest] = {
      "clean": clean,
      "raw": raw_g,
      "filename": filename,
      "clean_options": _ranked_options(clean),
      "raw_options": _ranked_options(raw_g),
    }

  entry = _GRAPH_CACHE[digest]
  clean_n = len(entry["clean"])
  clean_e = graph_utils.edge_count(entry["clean"])
  raw_n = len(entry["raw"])
  raw_e = graph_utils.edge_count(entry["raw"])

  info = html.Div([
    html.Strong(filename or "uploaded corpus"),
    html.Span(f"  ·  clean graph: {clean_n:,} words / {clean_e:,} edges"),
    html.Span(f"  ·  raw graph: {raw_n:,} tokens / {raw_e:,} edges", style={"marginLeft": "8px"}),
  ])
  return info, digest


def _ranked_options(graph) -> list[dict]:
  strengths = graph_utils.node_strengths(graph)
  ranked = sorted(strengths.items(), key=lambda kv: (-kv[1], kv[0]))
  return [{"label": f"{word} ({strength})", "value": word} for word, strength in ranked]


@app.callback(
  Output("dijkstra-source", "options"),
  Output("dijkstra-target", "options"),
  Output("markov-start", "options"),
  Output("top-start", "options"),
  Input("corpus-hash", "data"),
)
def populate_dropdowns(corpus_hash):
  if not corpus_hash or corpus_hash not in _GRAPH_CACHE:
    return [], [], [], []
  entry = _GRAPH_CACHE[corpus_hash]
  clean_opts = entry["clean_options"]
  raw_opts = entry["raw_options"]
  return clean_opts, clean_opts, raw_opts, clean_opts


def _empty(message: str):
  return [], html.Div(message, style={"color": "#666", "fontStyle": "italic"})


@app.callback(
  Output("graph", "elements"),
  Output("graph", "layout"),
  Output("results", "children"),
  Input("corpus-hash", "data"),
  Input("mode", "value"),
  Input("full-min-weight", "value"),
  Input("full-drop-isolates", "value"),
  Input("dijkstra-source", "value"),
  Input("dijkstra-target", "value"),
  Input("scc-min-weight", "value"),
  Input("markov-start", "value"),
  Input("markov-length", "value"),
  Input("markov-reroll", "n_clicks"),
  Input("top-start", "value"),
  Input("top-k", "value"),
  Input("top-n", "value"),
)
def update(
  corpus_hash, mode,
  full_min_weight, full_drop_isolates,
  dij_source, dij_target,
  scc_min_weight,
  markov_start, markov_length, _markov_reroll,
  top_start, top_k, top_n,
):
  if not corpus_hash or corpus_hash not in _GRAPH_CACHE:
    elements, results = _empty("Upload a corpus to begin.")
    return elements, {"name": "preset"}, results

  entry = _GRAPH_CACHE[corpus_hash]
  clean = entry["clean"]
  raw_g = entry["raw"]

  if mode == "full_graph":
    return _full_graph(clean, full_min_weight or 2, "on" in (full_drop_isolates or []))

  if mode == "dijkstra":
    return _dijkstra(clean, (dij_source or "").strip().lower(), (dij_target or "").strip().lower())

  if mode == "scc":
    return _scc(clean, scc_min_weight or 2)

  if mode == "markov":
    return _markov(raw_g, (markov_start or "").strip().lower(), markov_length or 20)

  if mode == "top_phrases":
    return _top_phrases(clean, (top_start or "").strip().lower(), top_k or 3, top_n or 5)

  elements, results = _empty("Pick a mode.")
  return elements, {"name": "preset"}, results


def _full_graph(graph, min_weight, drop_isolates):
  filtered = graph_utils.filter_for_viz(graph, min_weight, drop_isolates)
  n = len(filtered)
  e = graph_utils.edge_count(filtered)
  total_n = len(graph)
  total_e = graph_utils.edge_count(graph)

  caption = html.Div([
    html.Div(f"Showing {n:,} nodes and {e:,} edges (of {total_n:,} / {total_e:,} total).", style={"marginBottom": "8px"}),
    html.Div("Tip: increase the min weight to declutter, or pick a focused mode (Dijkstra, SCC, Top phrases) for sub-graph views.", style={"color": "#666", "fontSize": "13px"}),
  ])

  if n > 500:
    return [], {"name": "preset"}, html.Div([
      html.Div(f"Filtered graph still has {n:,} nodes — too large to render responsively.", style={"color": "#c53030", "fontWeight": "600", "marginBottom": "8px"}),
      html.Div("Increase the minimum edge weight to shrink the graph below 500 nodes."),
    ])

  layout = {"name": "cose", "animate": False, "nodeRepulsion": 8000, "idealEdgeLength": 80}
  return graph_utils.to_cy_elements(filtered), layout, caption


def _dijkstra(graph, source, target):
  if not source or not target:
    elements, results = _empty("Enter both a source and a target word.")
    return elements, {"name": "preset"}, results

  if source not in graph:
    elements, results = _empty(f"Source word '{source}' is not in the clean graph.")
    return elements, {"name": "preset"}, results

  if target not in graph:
    elements, results = _empty(f"Target word '{target}' is not in the clean graph.")
    return elements, {"name": "preset"}, results

  distance, path = dijkstra.dijkstra_path(graph, source, target)

  if not path:
    distances_table = _distance_table(graph, source)
    return [], {"name": "preset"}, html.Div([
      html.Div(f"No path from '{source}' to '{target}'.", style={"color": "#c53030", "marginBottom": "12px"}),
      distances_table,
    ])

  sub = graph_utils.subgraph_from_path(graph, path)
  elements = graph_utils.to_cy_elements(
    sub,
    node_classes={n: "path" for n in path},
    edge_classes={(path[i], path[i+1]): "path" for i in range(len(path)-1)},
  )

  results = html.Div([
    html.Div([
      html.Strong("Shortest path: "),
      html.Span(" → ".join(path)),
      html.Span(f"  (total weight {int(distance)})", style={"color": "#666", "marginLeft": "8px"}),
    ], style={"marginBottom": "16px"}),
    _distance_table(graph, source),
  ])

  return elements, {"name": "breadthfirst", "directed": True, "roots": f"#{source}", "spacingFactor": 1.2, "animate": False}, results


def _distance_table(graph, source):
  distances = dijkstra.dijkstra(graph, source)
  reachable = sorted(((w, n) for n, w in distances.items() if w != float("inf") and n != source), key=lambda x: x[0])

  if not reachable:
    return html.Div("(no other reachable words)", style={"color": "#666", "fontStyle": "italic"})

  rows = [html.Tr([html.Td(n, style={"padding": "2px 12px 2px 0"}), html.Td(int(w))]) for w, n in reachable[:50]]
  more = html.Div(f"… {len(reachable) - 50} more", style={"color": "#666", "fontSize": "12px", "marginTop": "4px"}) if len(reachable) > 50 else None

  return html.Div([
    html.Div(f"Distances from '{source}' (top 50 nearest)", style=LABEL_STYLE),
    html.Table([html.Tbody(rows)], style={"borderCollapse": "collapse", "fontSize": "13px"}),
    more,
  ])


def _scc(graph, min_weight):
  sccs = kosaraju.scc(graph, min_weight)
  non_trivial = [s for s in sccs if len(s) >= 2]
  non_trivial.sort(key=len, reverse=True)

  sub, classes = graph_utils.subgraph_from_sccs(graph, non_trivial, min_size=2)

  if not sub:
    return [], {"name": "preset"}, html.Div(f"No SCCs of size ≥ 2 with edge weight ≥ {min_weight}.", style={"color": "#666"})

  elements = graph_utils.to_cy_elements(sub, node_classes=classes)

  list_items = [
    html.Li(f"({len(s)}) " + ", ".join(s), style={"marginBottom": "4px"})
    for s in non_trivial[:30]
  ]
  more = html.Div(f"… {len(non_trivial) - 30} more SCCs", style={"color": "#666", "fontSize": "12px"}) if len(non_trivial) > 30 else None

  results = html.Div([
    html.Div(f"Found {len(non_trivial)} SCCs of size ≥ 2 (showing largest first).", style={"marginBottom": "8px"}),
    html.Ol(list_items, style={"fontSize": "13px"}),
    more,
  ])

  layout_name = "cose" if len(sub) > 30 else "circle"
  return elements, {"name": layout_name, "animate": False}, results


def _markov(raw_graph, start, length):
  if not start:
    elements, results = _empty("Enter a start word.")
    return elements, {"name": "preset"}, results

  if start not in raw_graph:
    elements, results = _empty(f"Start word '{start}' is not in the raw graph. (Try a stopword like 'the' — the raw loader keeps them.)")
    return elements, {"name": "preset"}, results

  walk = markov.generate_markov_chain(raw_graph, start, int(length))
  sub = graph_utils.subgraph_from_path(raw_graph, walk)

  elements = graph_utils.to_cy_elements(
    sub,
    node_classes={n: "path" for n in walk},
    edge_classes={(walk[i], walk[i+1]): "path" for i in range(len(walk)-1)},
  )

  results = html.Div([
    html.Div("Generated text", style=LABEL_STYLE),
    html.Div(" ".join(walk), style={"padding": "12px", "background": "#f7fafc", "borderRadius": "6px", "fontStyle": "italic", "lineHeight": "1.6"}),
    html.Div("Click 'Re-roll' to sample a different walk.", style={"color": "#666", "fontSize": "12px", "marginTop": "8px"}),
  ])

  return elements, {"name": "breadthfirst", "directed": True, "roots": f"#{start}", "spacingFactor": 1.0, "animate": False}, results


def _top_phrases(graph, start, k, n):
  if not start:
    elements, results = _empty("Enter a start word.")
    return elements, {"name": "preset"}, results

  if start not in graph:
    elements, results = _empty(f"Start word '{start}' is not in the clean graph.")
    return elements, {"name": "preset"}, results

  phrases = path_finder.top_phrases(graph, start, int(k), int(n))

  if not phrases:
    elements, results = _empty(f"No length-{k} paths starting at '{start}'.")
    return elements, {"name": "preset"}, results

  paths = [p for p, _ in phrases]
  sub = graph_utils.subgraph_from_paths(graph, paths)

  node_classes = {start: "path"}
  edge_classes: dict[tuple[str, str], str] = {}
  for path, _ in phrases:
    for node in path:
      node_classes.setdefault(node, "path")
    for i in range(len(path) - 1):
      edge_classes[(path[i], path[i+1])] = "path"

  elements = graph_utils.to_cy_elements(sub, node_classes=node_classes, edge_classes=edge_classes)

  list_items = [
    html.Li([
      html.Span(" → ".join(path)),
      html.Span(f"  (weight {weight})", style={"color": "#666", "marginLeft": "8px"}),
    ], style={"marginBottom": "4px"})
    for path, weight in phrases
  ]
  results = html.Div([
    html.Div(f"Top {len(phrases)} length-{k} phrases starting at '{start}'.", style={"marginBottom": "8px"}),
    html.Ol(list_items, style={"fontSize": "13px"}),
  ])

  return elements, {"name": "breadthfirst", "directed": True, "roots": f"#{start}", "spacingFactor": 1.2, "animate": False}, results


if __name__ == "__main__":
  import argparse
  parser = argparse.ArgumentParser(description="Lexigraph interactive UI")
  parser.add_argument("--port", type=int, default=8050, help="Port to bind (default: 8050)")
  parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
  parser.add_argument("--no-debug", action="store_true", help="Disable Dash debug mode")
  args = parser.parse_args()
  app.run(host=args.host, port=args.port, debug=not args.no_debug)
