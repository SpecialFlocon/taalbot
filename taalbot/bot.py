from discord.ext import commands
from io import StringIO

import discord
import json
import os
import requests
import sys


taalbot = commands.Bot(command_prefix='!')

@taalbot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@taalbot.command(name='dehet')
async def search_word(ctx, word):
    output_buf = StringIO()

    response = requests.get("http://localhost:8000/api/v1/woorden/search/{}".format(word))
    words = json.loads(response.text)

    result_prefix = ""
    if len(words) > 1:
        output_buf.write("I found multiple words! 🔎\nHere are the first few ones:\n")
        result_prefix = "- "

    for obj in words:
        articles = obj['lidwoord_name']
        both_articles = len(articles) == 2
        result_suffix = ""

        if both_articles:
            article_output = "**{}**/**{}**".format(*articles)
            result_suffix = "⚠"
        else:
            article_output = "**{}**".format(*articles)

        word = obj['woord']
        output_buf.write("{}{} {} {}\n".format(result_prefix, article_output, word, result_suffix))

    await ctx.send(output_buf.getvalue())

if __name__ == '__main__':
    try:
        token = os.environ['TAALTOOL_BOT_TOKEN']
    except KeyError:
        print("Bot token is not present, please set it in the TAALTOOL_BOT_TOKEN environment variable.")
        sys.exit(1)

    taalbot.run(token)
