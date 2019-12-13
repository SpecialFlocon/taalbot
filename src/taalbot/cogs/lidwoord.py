from discord.ext import commands
from io import StringIO

from taalbot import const

import json
import requests


class LidwoordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO(thepib): articles are not expected to change anytime soon, preload them somewhere global scope?
    def get_articles(self):
        response = requests.get("{}/api/{}/lidwoorden".format(self.bot.api_url, self.bot.api_version), timeout=const.API_REQUEST_TIMEOUT)
        response.raise_for_status()
        return json.loads(response.text)

    def get_or_learn_word(self, word):
        response = requests.get("{}/api/{}/woorden/learn/{}".format(self.bot.api_url, self.bot.api_version, word), timeout=const.API_REQUEST_TIMEOUT)
        response.raise_for_status()
        return json.loads(response.text)

    def set_word(self, word, new_article):
        """
        Create a new word with given article,
        or replace the article of an existing word.

        Stalemate resolution algorithm:
        - step 1: the word of the user who ran the command is final.
        """

        response = requests.get("{}/api/{}/woorden/search/{}".format(self.bot.api_url, self.bot.api_version, word), timeout=const.API_REQUEST_TIMEOUT)
        # HTTP 404: word doesn't exist in taalapi's database, we'll create it later.
        word_exists = response.status_code != 404

        articles = self.get_articles()
        if word_exists:
            obj = json.loads(response.text)
            if new_article == _('both'):
                obj['lidwoord'] = [a['id'] for a in articles]
            else:
                obj['lidwoord'] = [a['id'] for a in articles if a['lidwoord'] == new_article]

            # Automatically mark new word/article combination as accurate.
            obj['accurate'] = True

            # Update word/article combination
            response = requests.put("{}/api/{}/woorden/{}/".format(self.bot.api_url, self.bot.api_version, obj['id']), data=obj, timeout=const.API_REQUEST_TIMEOUT)
            response.raise_for_status()
            return json.loads(response.text)
        else:
            new_word = dict()
            new_word['woord'] = word
            if new_article == _('both'):
                new_word['lidwoord'] = [a['id'] for a in articles]
            else:
                new_word['lidwoord'] = [a['id'] for a in articles if a['lidwoord'] == new_article]

            response = requests.post("{}/api/{}/woorden/".format(self.bot.api_url, self.bot.api_version), data=new_word, timeout=const.API_REQUEST_TIMEOUT)
            response.raise_for_status()
            return json.loads(response.text)

    @commands.command(aliases=['hetde'], brief=_("De or het? Use this command to find out!"))
    async def dehet(self, ctx, *args):
        # One argument: the user is asking for the article
        if len(args) == 1:
            obj = self.get_or_learn_word(args[0])
            display_article = '/'.join((lambda x: '**{}**'.format(x))(a) for a in obj['lidwoord_name'])

            if obj['accurate']:
                output = "{} {}".format(display_article, obj['woord'])
            else:
                output = _("""
{0}... {1}? 🤔
Something's off... If I'm wrong, you can correct me: `{2}{3} {1} de/het/{4}`
Don't forget that all plural nouns in Dutch are *de-words*!
""").format(display_article, word, ctx.bot.command_prefix, ctx.invoked_with, _('both'))

            await ctx.send(output)
        # Two arguments: the user is setting the article of a word
        elif len(args) == 2:
            if not args[1] in ['de', 'het', _('both')]:
                return await ctx.send_help('dehet')

            obj = self.set_word(*args)
            display_article = '/'.join((lambda x: '**{}**'.format(x))(a) for a in obj['lidwoord_name'])

            output = _("So, it's {} {}. Noted!").format(display_article, obj['woord'])

            await ctx.send(output)
        else:
            await ctx.send(_("""
To get the article of a noun: `{0}{1} {2}`
To set the article of a noun: `{0}{1} {2} {3}`
More info: `{0}help {1}`
""").format(ctx.bot.command_prefix, ctx.invoked_with, _('word'), _('article')))

def setup(bot):
    bot.add_cog(LidwoordCog(bot))
