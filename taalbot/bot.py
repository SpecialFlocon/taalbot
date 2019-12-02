from discord.ext import commands

import discord
import os
import sys


taalbot = commands.Bot(command_prefix='!')

@taalbot.command()
async def ping(ctx):
    await ctx.send('Pong!')

if __name__ == '__main__':
    try:
        token = os.environ['TAALTOOL_BOT_TOKEN']
    except KeyError:
        print("Bot token is not present, please set it in the TAALTOOL_BOT_TOKEN environment variable.")
        sys.exit(1)

    taalbot.run(token)
