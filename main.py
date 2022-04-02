import discord
import os
import random


#  Text Loading 

def load_text_files(*file_paths):
    """Read and concatenate multiple text/CSV files into one string."""
    combined = ""
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                combined += f.read() + "\n"
        except FileNotFoundError:
            print(f"Warning: {path} not found, skipping.")
    return combined


#  Markov Chain 

def build_markov_chain(text, state_size=2):
    """
    Build a Markov chain transition table from the given text.
    Returns a dict mapping each word-tuple state to a list of possible next words.
    """
    words = text.split()
    chain = {}
    for i in range(len(words) - state_size):
        state = tuple(words[i : i + state_size])
        next_word = words[i + state_size]
        if state not in chain:
            chain[state] = []
        chain[state].append(next_word)
    return chain


def make_sentence(chain, state_size=2, max_words=60):
    """
    Walk the Markov chain to produce one sentence.
    Prefers states that begin with a capitalised word so output reads naturally.
    Returns None if the chain is empty.
    """
    if not chain:
        return None

    # Prefer states whose first word starts with a capital letter
    start_states = [s for s in chain if s[0][0].isupper()]
    if not start_states:
        start_states = list(chain.keys())

    state = random.choice(start_states)
    words = list(state)

    for _ in range(max_words - state_size):
        if state not in chain:
            break
        next_word = random.choice(chain[state])
        words.append(next_word)
        state = tuple(words[-state_size:])

    sentence = " ".join(words)
    # Ensure the sentence ends with punctuation
    if sentence and sentence[-1] not in ".!?":
        sentence += "."
    return sentence


def generate_quote(chain, state_size=2):
    """Keep generating until we get a non-empty sentence."""
    result = None
    while not result:
        result = make_sentence(chain, state_size=state_size)
    return result


#  Startup: build the model once 

raw_text = load_text_files("general.csv", "how_1.csv", "how_2.csv", "how_3.csv")
CHAIN = build_markov_chain(raw_text, state_size=2)


#  Discord Bot 

client = discord.Client()


@client.event
async def on_ready():
    print("bot online".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!piss"):
        quote = generate_quote(CHAIN)
        await message.channel.send(quote)


client.run(os.getenv("DISCORD_TOKEN"))
