def scc(graph: dict[str, dict[str, int]], weight_req: int) -> list[list[str]]:
  visited = set()
  finish_stack = []

  def dfs(node: str):
    visited.add(node)

    for neighbor, weight in graph[node].items():
      if neighbor not in visited and weight >= weight_req:
        dfs(neighbor)

    finish_stack.append(node)

  # run dfs on the graph to get finish times
  for node in graph:
    if node not in visited:
      dfs(node)

  # reverse graph
  reversed_graph = {node: {} for node in graph}

  for node, neighbors in graph.items():
    for neighbor, weight in neighbors.items():
      if weight >= weight_req:
        reversed_graph[neighbor][node] = weight

  # second pass
  visited.clear()
  sccs = []

  def reverse_dfs(node: str, current_scc: list[str]):
    visited.add(node)
    current_scc.append(node)

    for neighbor, weight in reversed_graph[node].items():
      if neighbor not in visited and weight >= weight_req:
        reverse_dfs(neighbor, current_scc)

  # process nodes in decreasing finish time order --> from top of stack first
  while finish_stack:
    node = finish_stack.pop()

    if node not in visited:
      current_scc = []
      reverse_dfs(node, current_scc)
      sccs.append(current_scc)

  return sccs