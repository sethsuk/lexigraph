import random

def generate_markov_chain(graph: dict[str, dict[str, int]], start_word: str, length: int) -> list[str]:
  if start_word not in graph:
    raise ValueError(f"Start word '{start_word}' not in graph")

  current_word = start_word
  result = [current_word]

  for _ in range(length - 1):
    next_words = graph[current_word]

    # check if next word exists
    if not next_words:
      break

    # weighted random choice of next word
    total_weight = sum(next_words.values())
    rand_weight = random.randint(1, total_weight)
    cumulative_weight = 0

    for next_word, weight in next_words.items():
      cumulative_weight += weight

      if rand_weight <= cumulative_weight:
        current_word = next_word
        result.append(current_word)
        break

  return result