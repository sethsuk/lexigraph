from nltk.stem import PorterStemmer

def clean_word(word: str) -> str:
  stemmer = PorterStemmer()
  return stemmer.stem(word.lower()).strip(".,!?;:\"()[]{}'")

# (word, (next_word, weight))
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

  return res_graph


graph = loader("lexigraph/test.txt")

for word in graph:
  print(f"{word}: {graph[word]}")