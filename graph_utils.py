Graph = dict[str, dict[str, int]]


def filter_for_viz(graph: Graph, min_weight: int, drop_isolates: bool) -> Graph:
  """Filter the graph for visualization by removing edges below a certain weight and optionally dropping isolated nodes."""
  filtered: Graph = {}

  for node, neighbors in graph.items():
    kept = {n: w for n, w in neighbors.items() if w >= min_weight}
    filtered[node] = kept

  if drop_isolates:
    in_degree: dict[str, int] = {node: 0 for node in filtered}
    for neighbors in filtered.values():
      for n in neighbors:
        if n in in_degree:
          in_degree[n] += 1

    filtered = {
      node: {n: w for n, w in neighbors.items() if filtered.get(n) or in_degree.get(n, 0) > 0}
      for node, neighbors in filtered.items()
      if neighbors or in_degree.get(node, 0) > 0
    }

  return filtered


def edge_count(graph: Graph) -> int:
  return sum(len(neighbors) for neighbors in graph.values())


def node_strengths(graph: Graph) -> dict[str, int]:
  out = {n: sum(graph[n].values()) for n in graph}
  inn: dict[str, int] = {n: 0 for n in graph}
  for src, neighbors in graph.items():
    for dst, w in neighbors.items():
      if dst in inn:
        inn[dst] += w
  return {n: out[n] + inn[n] for n in graph}


def to_cy_elements(
  graph: Graph,
  *,
  node_classes: dict[str, str] | None = None,
  edge_classes: dict[tuple[str, str], str] | None = None,
) -> list[dict]:
  """
  Convert the graph to a list of elements suitable for Cytoscape visualization, with optional classes for nodes and edges."""
  elements: list[dict] = []
  node_classes = node_classes or {}
  edge_classes = edge_classes or {}

  for node in graph:
    el: dict = {"data": {"id": node, "label": node}}
    cls = node_classes.get(node)
    if cls:
      el["classes"] = cls
    elements.append(el)

  for src, neighbors in graph.items():
    for dst, weight in neighbors.items():
      if dst not in graph:
        continue
      el = {"data": {"source": src, "target": dst, "weight": weight, "label": str(weight)}}
      cls = edge_classes.get((src, dst))
      if cls:
        el["classes"] = cls
      elements.append(el)

  return elements


def subgraph_from_path(graph: Graph, path: list[str]) -> Graph:
  """Extract a subgraph containing only the nodes and edges along the given path."""
  sub: Graph = {node: {} for node in path}

  for i in range(len(path) - 1):
    src, dst = path[i], path[i + 1]
    weight = graph.get(src, {}).get(dst)
    if weight is not None:
      sub[src][dst] = weight

  return sub


def subgraph_from_paths(graph: Graph, paths: list[list[str]]) -> Graph:
  """Extract a subgraph containing only the nodes and edges along the given paths."""
  sub: Graph = {}

  for path in paths:
    for node in path:
      sub.setdefault(node, {})
    for i in range(len(path) - 1):
      src, dst = path[i], path[i + 1]
      weight = graph.get(src, {}).get(dst)
      if weight is not None:
        sub[src][dst] = weight

  return sub


def subgraph_from_sccs(
  graph: Graph,
  sccs: list[list[str]],
  *,
  min_size: int = 2,
) -> tuple[Graph, dict[str, str]]:
  """Extract a subgraph containing only the nodes and edges within strongly connected components that meet the minimum size requirement, and return a mapping of nodes to their SCC classes."""
  kept = [scc for scc in sccs if len(scc) >= min_size]
  node_class_map: dict[str, str] = {}
  members: set[str] = set()

  for idx, scc in enumerate(kept):
    cls = f"scc-{idx % 10}"
    for node in scc:
      node_class_map[node] = cls
      members.add(node)

  sub: Graph = {node: {} for node in members}
  for src in members:
    for dst, weight in graph.get(src, {}).items():
      if dst in members:
        sub[src][dst] = weight

  return sub, node_class_map
