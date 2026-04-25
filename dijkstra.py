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
