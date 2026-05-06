Project Name
---------------------------------------------------------
Lexigraph


Project Description
---------------------------------------------------------
Lexigraph is a program that allows the user to explore a text via graph analysis. The user interacts with the program via a Flask app that uses Dash Cytoscape to render graph interactions. The program parses an uploaded text into a weighted, directed social network graph, where edges represent the frequencies in which words appear consecutively. The user can then analyse the interactions of words in the text with a variety of tools: Dijkstra’s algorithm to find shortest paths between words, Kosaraju’s algorithm to explore strongly connected components, Markov chain simulation to generate probable sentences, and DFS + backtracking to find the most probable phrases.

See README.md for the user manual.


Project Category
---------------------------------------------------------
Implementation


Work Breakdown
---------------------------------------------------------
Seth: Text loader, Kosaraju, Markov, Top phrase finder
Rei: Djikistra’s algorithm, Pagerank 
Grace: Flask app, graph visualization, and user manual


AI usage
---------------------------------------------------------
- Flask + Cytoscape frontend scaffolding (app.py)
- Guiding us through more complex graph algorithm (Kosaraju)
- Brainstorm ways to analyze graph text
