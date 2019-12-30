from discord.ext import commands

from .. import const

import logging


logger = logging.getLogger('taalbot.cogs.shortcuts')

class Shortcuts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['betekenis'], brief=_("Search for a word in Van Dale free online dictionary"))
    async def vandale(self, ctx, word):
        await ctx.send("<{}/{}>".format(const.VANDALE_SEARCH_BASE_URL, word))

    @commands.command(aliases=['uitspraak'], brief=_("Listen to natives pronouncing a certain word"))
    async def forvo(self, ctx, word):
        await ctx.send("<{}/{}/nl/>".format(const.FORVO_SEARCH_BASE_URL, word))

def setup(bot):
    bot.add_cog(Shortcuts(bot))
