def pagerank(graph: dict[str, dict[str, int]]) -> dict[str, float]:

    nodes = set(graph)
    for edges in graph.values():
        nodes.update(edges)
    N = len(nodes)

    # outgoing weights handling
    outgoing_weights = {}
    dangling = []
    for n in nodes:
        outgoing_weights[n] = sum(graph.get(n, {}).values())
        if outgoing_weights[n] == 0:
            dangling.append(n)

    # reverse adjacency: for each node, who points at it and with what weight
    incoming = {n: [] for n in nodes}
    for source, edges in graph.items():
        for target, weight in edges.items():
            incoming[target].append((source, weight))

    # hyperparameters
    d = 0.85
    tol = 1e-6
    max_iter = 100

    # initialize scores uniformly
    scores = {n: 1 / N for n in nodes}

    # power iteration
    for _ in range(max_iter):
        # compute dangling mass from current scores, before building new ones
        dangling_mass = sum(scores[n] for n in dangling)

        new_scores = {}
        for w in nodes:
            # contributions from incoming edges
            rank_sum = 0
            for source, weight in incoming[w]:
                rank_sum += scores[source] * weight / outgoing_weights[source]

            # full recurrence: teleport + d * (incoming + dangling redistribution)
            new_scores[w] = (1 - d) / N + d * (rank_sum + dangling_mass / N)

        # convergence check (L1 distance)
        diff = sum(abs(new_scores[n] - scores[n]) for n in nodes)
        scores = new_scores
        if diff < tol:
            break

    return scores