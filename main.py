import discord
import os
import csv
import json
import markovify

client = discord.Client()
c = 0
data = []

file_name = "general.csv"
file_name2 = "how_1.csv"
file_name3 = "how_2.csv"
file_name4 = "how_3.csv"

def markov():
    with open(file_name) as f:
        with open(file_name2) as f2:
            with open(file_name3) as f3:
                with open(file_name4) as f4:
                    text = f.read()
                    text2 = f2.read()
                    text3 = f3.read()
                    text4 = f4.read()
                    text = text + text2 + text3 + text4
                    model = markovify.NewlineText(text, state_size=2, well_formed = True)
                    curr = model.make_sentence()
                    while not curr:
                        curr = model.make_sentence()
                    return curr

@client.event
async def on_ready():
    print('bot online'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!piss'):
        quote = markov()
        await message.channel.send(quote)

client.run(os.getenv('DISCORD_TOKEN'))
