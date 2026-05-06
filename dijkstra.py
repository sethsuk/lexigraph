import heapq
import math
from typing import Callable

# cost modes:
#   "weight" — sum of raw edge weights (path through rarest transitions)
#   "neglog" — sum of -log(P(next|curr)) (path with highest joint probability)
def _make_cost_fn(graph: dict[str, dict[str, int]], mode: str) -> Callable[[str, int], float]:
  if mode == "weight":
    return lambda _u, w: float(w)
  if mode == "neglog":
    out_strength = {n: sum(graph[n].values()) or 1 for n in graph}
    return lambda u, w: -math.log(w / out_strength[u])
  raise ValueError(f"unknown cost mode: {mode!r}")

def dijkstra(graph: dict[str, dict[str, int]], source: str, *, cost: str = "weight") -> dict[str, float]:
  edge_cost = _make_cost_fn(graph, cost)
  dist = {node: float('inf') for node in graph}
  dist[source] = 0
  pq: list[tuple[float, str]] = [(0.0, source)]

  while pq:
    distance, curr_node = heapq.heappop(pq)

    # stale
    if distance > dist[curr_node]:
      continue

    for neighbor, weight in graph[curr_node].items():
      new_dist = distance + edge_cost(curr_node, weight)

      if new_dist < dist[neighbor]:
        dist[neighbor] = new_dist
        heapq.heappush(pq, (new_dist, neighbor))

  return dist

def dijkstra_path(graph: dict[str, dict[str, int]], source: str, target: str, *, cost: str = "weight") -> tuple[float, list[str]]:
  if source not in graph or target not in graph:
    return float('inf'), []

  edge_cost = _make_cost_fn(graph, cost)
  dist = {node: float('inf') for node in graph}
  prev: dict[str, str | None] = {node: None for node in graph}
  dist[source] = 0
  pq: list[tuple[float, str]] = [(0.0, source)]

  while pq:
    distance, curr_node = heapq.heappop(pq)

    if curr_node == target:
      break

    if distance > dist[curr_node]:
      continue

    for neighbor, weight in graph[curr_node].items():
      new_dist = distance + edge_cost(curr_node, weight)

      if new_dist < dist[neighbor]:
        dist[neighbor] = new_dist
        prev[neighbor] = curr_node
        heapq.heappush(pq, (new_dist, neighbor))

  if dist[target] == float('inf'):
    return float('inf'), []

  path: list[str] = []
  node: str | None = target
  while node is not None:
    path.append(node)
    node = prev[node]
  path.reverse()

  return dist[target], path
