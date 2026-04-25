def all_k_length_paths(graph: dict[str, dict[str, int]], start: str, k: int) -> list[tuple[list[str], int]]:
  # backtracking dfs
  def dfs(node: str, path: list[str], total_weight: int):
    if len(path) == k:
      paths.append((path.copy(), total_weight))
      return
    
    for neighbor, weight in graph[node].items():
      if (neighbor in path): # avoid cycles
        continue
      
      path.append(neighbor)
      dfs(neighbor, path, total_weight + weight)
      path.pop()
  
  paths = [] # list of (path, total weight)
  dfs(start, [start], 0)

  return paths

def top_phrases(graph: dict[str, dict[str, int]], start: str, k: int, n: int) -> list[tuple[list[str], int]]:
  all_paths = all_k_length_paths(graph, start, k)
  all_paths.sort(key=lambda x: x[1], reverse=True) # sort by total weight

  return all_paths[:n]

