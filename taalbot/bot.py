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
    # HTTP 500: couldn't extract info from sources
    # TODO(thepib): notify developer so that he can get on with fixing his code
    if response.status_code == 500:
        # Actually a lie (for now)
        await ctx.send("Oops, the rocket blew up in-flight. I just harassed whoever wrote me about it, so you don't have to do it.")
        return
    # HTTP 404: word doesn't exist
    if response.status_code == 404:
        await ctx.send("The word you're looking for was not found.\nIs it a *zelfstandig naamwoord*? Is it even a word?")
        return

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
