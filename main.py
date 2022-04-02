import discord
import os
import random
from collections import defaultdict, Counter
from typing import Optional


#  Markov Chain Engine 

class MarkovChain:
    """
    Probabilistic text generator built on variable-order Markov chains.
    Transition probabilities are derived from observed n-gram frequencies
    in the training corpus.
    """

    def __init__(self, state_size: int = 2):
        self.state_size = state_size
        self._transitions: dict = defaultdict(Counter)
        self._start_states: list = []

    def train(self, corpus: str) -> "MarkovChain":
        """
        Tokenise the corpus and populate the transition table.
        Sentence-initial states (first word capitalised) are tracked
        separately to ensure natural-sounding sentence starts.
        """
        tokens = corpus.split()
        n = self.state_size

        for i in range(len(tokens) - n):
            state = tuple(tokens[i : i + n])
            successor = tokens[i + n]
            self._transitions[state][successor] += 1
            if (i == 0 or tokens[i - 1][-1] in ".!?") and state[0][0].isupper():
                if state not in self._start_states:
                    self._start_states.append(state)

        return self

    def _weighted_next(self, state: tuple) -> Optional[str]:
        """Sample a successor token weighted by observed co-occurrence frequency."""
        counter = self._transitions.get(state)
        if not counter:
            return None
        population = list(counter.keys())
        weights = list(counter.values())
        return random.choices(population, weights=weights, k=1)[0]

    def _is_well_formed(self, tokens: list, min_words: int = 6) -> bool:
        """Return True only if the token sequence reads as a complete sentence."""
        if len(tokens) < min_words:
            return False
        if not tokens[0][0].isupper():
            return False
        if tokens[-1][-1] not in ".!?":
            return False
        return True

    def generate(
        self,
        max_words: int = 60,
        min_words: int = 6,
        max_attempts: int = 200,
    ) -> Optional[str]:
        """
        Walk the transition table from a sentence-initial state, applying
        frequency-weighted sampling at each step. Backtracks and retries
        up to max_attempts times until a well-formed sentence is produced.
        """
        start_pool = self._start_states or list(self._transitions.keys())
        if not start_pool:
            return None

        for _ in range(max_attempts):
            state = random.choice(start_pool)
            tokens = list(state)

            for _ in range(max_words - self.state_size):
                next_token = self._weighted_next(state)
                if next_token is None:
                    break
                tokens.append(next_token)
                state = tuple(tokens[-self.state_size :])

                # Terminate early on a sentence-boundary token
                if next_token[-1] in ".!?" and len(tokens) >= min_words:
                    break

            if self._is_well_formed(tokens, min_words):
                return " ".join(tokens)

        return None


#  Corpus Loading 

def load_corpus(*file_paths: str, encoding: str = "utf-8") -> str:
    """
    Stream multiple source files into a single normalised corpus string.
    Missing files are skipped with a warning rather than raising.
    """
    segments: list = []
    for path in file_paths:
        try:
            with open(path, "r", encoding=encoding, errors="ignore") as fh:
                segments.append(fh.read())
        except FileNotFoundError:
            print(f"[corpus] Warning: '{path}' not found  skipping.")
    return "\n".join(segments)


#  Model Initialisation 

_corpus = load_corpus("text.csv")
_model  = MarkovChain(state_size=2).train(_corpus)


def generate_quote() -> str:
    """Request a sentence from the model, retrying until one is produced."""
    result: Optional[str] = None
    while result is None:
        result = _model.generate()
    return result


#  Discord Bot 

client = discord.Client()


@client.event
async def on_ready() -> None:
    print("bot online".format(client))


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return

    if message.content.startswith("!piss"):
        await message.channel.send(generate_quote())


client.run(os.getenv("DISCORD_TOKEN"))
