from discord.ext import commands
from io import StringIO

import json
import requests


class LidwoordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def search_word(self, word):
        output_buf = StringIO()

        response = requests.get("{}/api/{}/woorden/search/{}".format(self.bot.api_url, self.bot.api_version, word))
        # HTTP 500: couldn't extract info from sources
        # TODO(thepib): notify developer so that he can get on with fixing his code
        if response.status_code == 500:
            # Actually a lie (for now)
            return "Oops, the rocket blew up in-flight. I just harassed whoever wrote me about it, so you don't have to do it."
        # HTTP 404: word doesn't exist
        if response.status_code == 404:
            return "The word you're looking for was not found.\nIs it a *zelfstandig naamwoord*? Is it even a word?"

        words = json.loads(response.text)

        result_prefix = ""
        if len(words) > 1:
            output_buf.write("I found multiple words! 🔎\nHere are the first few ones:\n")
            result_prefix = "- "

        for obj in words:
            articles = obj['lidwoord_name']
            both_articles = len(articles) == 2
            result_suffix = "🤔" if not obj['accurate'] else ""

            if both_articles:
                article_output = "**{}**/**{}**".format(*articles)
            else:
                article_output = "**{}**".format(*articles)

            word = obj['woord']
            output_buf.write("{}{} {} {}\n".format(result_prefix, article_output, word, result_suffix))

        return output_buf.getvalue()

    @commands.command()
    async def dehet(self, ctx, *args):
        if len(args) == 1:
            await ctx.send(self.search_word(word))
        else:
            await ctx.send_help('LidwoordCog')

def setup(bot):
    bot.add_cog(LidwoordCog(bot))
