import loader
import dijkstra
import kosaraju
import markov
import path_finder

def main():
  graph_lemmatized = loader.loader_clean("lexigraph/alice-in-wonderland.txt")
  graph_raw = loader.loader_raw("lexigraph/alice-in-wonderland.txt")

  # for word in graph:
  #   print(f"{word}: {graph[word]}")

  # dijkstra_test = dijkstra.dijkstra(graph, "brown")

  # print(dijkstra_test)

  # kosaraju_test = kosaraju.scc(graph, 3)
  # print([scc for scc in kosaraju_test if len(scc) > 1])

  # generate_markov_chain_test = markov.generate_markov_chain(graph_raw, "the", 15)
  # print(generate_markov_chain_test)

  # use lemmatized so we can get more meaningful paths
  top_phrases_test = path_finder.top_phrases(graph_lemmatized, "alice", 5, 3)
  for path, weight in top_phrases_test:
    print(f"Path: {' '.join(path)}, Total Weight: {weight}")

if __name__ == "__main__":
  main()