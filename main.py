import loader
import dijkstra
import kosaraju
import markov

def main():
  graph_lemmatized = loader.loader_clean("lexigraph/three_little_pigs.txt")
  graph_raw = loader.loader_raw("lexigraph/alice-in-wonderland.txt")

  # for word in graph:
  #   print(f"{word}: {graph[word]}")

  # dijkstra_test = dijkstra.dijkstra(graph, "brown")

  # print(dijkstra_test)

  # kosaraju_test = kosaraju.scc(graph, 3)
  # print([scc for scc in kosaraju_test if len(scc) > 1])

  generate_markov_chain_test = markov.generate_markov_chain(graph_raw, "the", 15)
  print(generate_markov_chain_test)

if __name__ == "__main__":
  main()