import heapq

def dijkstra(graph: dict[str, dict[str, int]], source: str) -> dict[str, float]:
  dist = {node: float('inf') for node in graph}
  dist[source] = 0
  pq = [(0, source)]

  while pq:
    distance, curr_node = heapq.heappop(pq)

    # stale
    if distance > dist[curr_node]:
      continue

    for neighbor, weight in graph[curr_node].items():
      new_dist = distance + weight

      if new_dist < dist[neighbor]:
        dist[neighbor] = new_dist
        heapq.heappush(pq, (new_dist, neighbor))

  return dist

def dijkstra_path(graph: dict[str, dict[str, int]], source: str, target: str) -> tuple[float, list[str]]:
  if source not in graph or target not in graph:
    return float('inf'), []

  dist = {node: float('inf') for node in graph}
  prev: dict[str, str | None] = {node: None for node in graph}
  dist[source] = 0
  pq = [(0, source)]

  while pq:
    distance, curr_node = heapq.heappop(pq)

    if curr_node == target:
      break

    if distance > dist[curr_node]:
      continue

    for neighbor, weight in graph[curr_node].items():
      new_dist = distance + weight

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
