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

# outputs
# dict: word (string) -> (dict: next_word (string) -> weight (int))
def loader(filename: str) -> dict[str, dict[str, int]]:
  with open(filename, "r") as file:
    content = file.read().lower()

  # clean text
  tokens = [t.strip(".,!?;:\"()[]{}'") for t in word_tokenize(content)]
  tokens = [t for t in tokens if t.isalpha()]
  tagged = pos_tag(tokens)
  words = [lemmatizer.lemmatize(tok, _wordnet_pos(tag)) for tok, tag in tagged]
  words = [w for w in words if w not in stop_words]

  res_graph = {}

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
