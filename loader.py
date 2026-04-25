from nltk.stem import PorterStemmer

# using stemming --> technique from lecture
def clean_word(word: str) -> str:
  stemmer = PorterStemmer()
  return stemmer.stem(word.lower()).strip(".,!?;:\"()[]{}'")

# outputs
# dict: word (string) -> (dict: next_word (string) -> weight (int))
def loader(filename: str) -> dict[str, dict[str, int]]:
  with open(filename, "r") as file:
    content = file.read()
    print(content)

  words = content.split(" ")

  res_graph = {}

  for i in range(len(words) - 1):
    word = clean_word(words[i])
    next_word = clean_word(words[i + 1])

    if word not in res_graph:
      res_graph[word] = {}

    if next_word not in res_graph[word]:
      res_graph[word][next_word] = 0

    res_graph[word][next_word] += 1

  # add last word to graph as a sink
  last_word = clean_word(words[-1])
  
  if last_word not in res_graph:
    res_graph[last_word] = {}

  return res_graph

