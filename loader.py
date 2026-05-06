from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk import pos_tag, word_tokenize
import nltk

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# get part of speech tag for lemmatization
def _wordnet_pos(tag: str) -> str:
  if tag.startswith('V'): return 'v'
  if tag.startswith('J'): return 'a'
  if tag.startswith('R'): return 'r'
  return 'n'

def loader_clean_from_text(content: str) -> dict[str, dict[str, int]]:
  """
  Load text and build a directed graph: (word -> (next_word -> weight)).
  Cleans the text by lowercasing, removing punctuation, lemmatizing, and removing stopwords.

  Args:
    content: The raw text content to process.
  """
  content = content.lower()

  # clean text
  tokens = [t.strip(".,!?;:\"()[]{}'") for t in word_tokenize(content)]
  tokens = [t for t in tokens if t.isalpha()]
  tagged = pos_tag(tokens)
  words = [lemmatizer.lemmatize(tok, _wordnet_pos(tag)) for tok, tag in tagged]
  words = [w for w in words if w not in stop_words]

  return _build_adjacency(words)

def loader_raw_from_text(content: str) -> dict[str, dict[str, int]]:
  """
  Load text and build a directed graph: (word -> (next_word -> weight)).
  Does not clean the text, keeps all words as-is.
  
  Args:
    content: The raw text content to process.
  """
  content = content.lower()

  # lowercase + strip punctuation only — keep tense, number, stopwords, contractions
  words = [w.strip(".,!?;:\"()[]{}") for w in content.split()]
  words = [w for w in words if w]

  return _build_adjacency(words)

def loader_clean(filename: str) -> dict[str, dict[str, int]]:
  with open(filename, "r") as file:
    return loader_clean_from_text(file.read())

def loader_raw(filename: str) -> dict[str, dict[str, int]]:
  with open(filename, "r") as file:
    return loader_raw_from_text(file.read())

def _build_adjacency(words: list[str]) -> dict[str, dict[str, int]]:
  """Build a directed graph from a list of words: (word -> (next_word -> weight))."""
  res_graph: dict[str, dict[str, int]] = {}

  if not words:
    return res_graph

  for i in range(len(words) - 1):
    word = words[i]
    next_word = words[i + 1]

    if word not in res_graph:
      res_graph[word] = {}

    if next_word not in res_graph[word]:
      res_graph[word][next_word] = 0

    res_graph[word][next_word] += 1

  # add last word to graph as a sink
  last_word = words[-1]

  if last_word not in res_graph:
    res_graph[last_word] = {}

  return res_graph