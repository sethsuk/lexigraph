import loader
import dijkstra

def main():
  graph = loader.loader("lexigraph/test.txt")
  
  for word in graph:
    print(f"{word}: {graph[word]}")

  dijkstra_test = dijkstra.dijkstra(graph, "brown")

  print(dijkstra_test)


if __name__ == "__main__":
  main()