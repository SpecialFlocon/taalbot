from discord.ext import commands
from io import StringIO

import json
import requests


class LidwoordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO(thepib): articles are not expected to change anytime soon, preload them somewhere global scope?
    def get_articles(self):
        response = requests.get("{}/api/{}/lidwoorden".format(self.bot.api_url, self.bot.api_version))
        return json.loads(response.text)

    def get_or_learn_word(self, word):
        output_buf = StringIO()

        response = requests.get("{}/api/{}/woorden/learn/{}".format(self.bot.api_url, self.bot.api_version, word))
        # HTTP 500: couldn't extract info from sources
        # TODO(thepib): notify developer so that he can get on with fixing his code
        if response.status_code == 500:
            # Actually a lie (for now)
            return "Oops, the rocket blew up in-flight. I just harassed whoever wrote me about it, so you don't have to do it."
        # HTTP 404: word doesn't exist
        if response.status_code == 404:
            return "The word you're looking for was not found.\nIs it a *zelfstandig naamwoord*? Is it even a word?"

        obj = json.loads(response.text)
        articles = obj['lidwoord_name']
        both_articles = len(articles) == 2
        result_suffix = "🤔" if not obj['accurate'] else ""

        if both_articles:
            article_output = "**{}**/**{}**".format(*articles)
        else:
            article_output = "**{}**".format(*articles)

        word = obj['woord']
        output_buf.write("{} {} {}\n".format(article_output, word, result_suffix))

        return output_buf.getvalue()

    def set_word(self, word, new_article):
        """
        Create a new word with given article,
        or replace the article of an existing word.

        Stalemate resolution algorithm:
        - step 1: the word of the user who ran the command is final.
        """

        response = requests.get("{}/api/{}/woorden/search/{}".format(self.bot.api_url, self.bot.api_version, word))
        # HTTP 404: word doesn't exist in taalapi's database, we'll create it later.
        word_exists = response.status_code != 404

        articles = self.get_articles()
        if word_exists:
            obj = json.loads(response.text)
            if new_article == 'both':
                obj['lidwoord'] = [a['id'] for a in articles]
            else:
                obj['lidwoord'] = [a['id'] for a in articles if a['lidwoord'] == new_article]

            # Automatically mark new word/article combination as accurate.
            obj['accurate'] = True

            # Update word/article combination
            response = requests.put("{}/api/{}/woorden/{}/".format(self.bot.api_url, self.bot.api_version, obj['id']), data=obj)
            if response.status_code != requests.codes.ok:
                return "I couldn't replace the article of this word. Not because I don't believe you, but because of a technical (or human) deficiency."

            return "Article for word {} has been set to **{}**. Thank you for your valuable contribution!".format(word, new_article)
        else:
            new_word = dict()
            new_word['woord'] = word
            if new_article == 'both':
                new_word['lidwoord'] = [a['id'] for a in articles]
            else:
                new_word['lidwoord'] = [a['id'] for a in articles if a['lidwoord'] == new_article]

            response = requests.post("{}/api/{}/woorden/{}/".format(self.bot.api_url, self.bot.api_version), data=new_word)
            if response.status_code != requests.codes.ok:
                return "I couldn't add this word/article combination to my record. Not because I don't believe you, but because of a technical (or human) deficiency."

            return "Word {} with article **{}** has been added to my record. Thank you for your valuable contribution!".format(word, new_article)

    @commands.command()
    async def dehet(self, ctx, *args):
        if len(args) == 1:
            await ctx.send(self.get_or_learn_word(args[0]))
        else:
            await ctx.send_help('LidwoordCog')

def setup(bot):
    bot.add_cog(LidwoordCog(bot))
