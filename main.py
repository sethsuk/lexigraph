import loader
import dijkstra
import kosaraju

def main():
  graph = loader.loader("lexigraph/alice-in-wonderland.txt")
  
  # for word in graph:
  #   print(f"{word}: {graph[word]}")

  # dijkstra_test = dijkstra.dijkstra(graph, "brown")

  # print(dijkstra_test)

  kosaraju_test = kosaraju.scc(graph, 3)
  print([scc for scc in kosaraju_test if len(scc) > 1])

if __name__ == "__main__":
  main()