from discord.ext import commands

from .. import const

import json
import requests


class LidwoordCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO(thepib): articles are not expected to change anytime soon, preload them somewhere global scope?
    def get_articles(self):
        response = requests.get("{}/api/{}/lidwoorden".format(self.bot.api_url, self.bot.api_version), timeout=const.API_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def get_or_learn_word(self, word):
        response = requests.get("{}/api/{}/woorden/learn/{}".format(self.bot.api_url, self.bot.api_version, word), timeout=const.API_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def set_word(self, word, new_article):
        """
        Create a new word with given article,
        or replace the article of an existing word.

        Stalemate resolution algorithm:
        - step 1: the word of the user who ran the command is final.
        """

        response = requests.get("{}/api/{}/woorden/search/{}".format(self.bot.api_url, self.bot.api_version, word), timeout=const.API_REQUEST_TIMEOUT)
        # HTTP 200: word exists in taalapi's database
        word_exists = response.status_code == requests.codes.ok

        articles = self.get_articles()
        if word_exists:
            obj = response.json()
            if new_article == _('both'):
                obj['lidwoord'] = [a['id'] for a in articles]
            else:
                obj['lidwoord'] = [a['id'] for a in articles if a['lidwoord'] == new_article]

            # Automatically mark new word/article combination as accurate.
            obj['accurate'] = True

            # Update word/article combination
            response = requests.put("{}/api/{}/woorden/{}/".format(self.bot.api_url, self.bot.api_version, obj['id']), data=obj, timeout=const.API_REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        else:
            new_word = dict()
            new_word['woord'] = word
            if new_article == _('both'):
                new_word['lidwoord'] = [a['id'] for a in articles]
            else:
                new_word['lidwoord'] = [a['id'] for a in articles if a['lidwoord'] == new_article]

            response = requests.post("{}/api/{}/woorden/".format(self.bot.api_url, self.bot.api_version), data=new_word, timeout=const.API_REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()

    @commands.command(aliases=['hetde'], brief=_("De or het? Use this command to find out!"))
    async def dehet(self, ctx, *args):
        # One argument: the user is asking for the article
        if len(args) == 1:
            try:
                obj = self.get_or_learn_word(args[0])
            except requests.HTTPError as e:
                if e.response.status_code == requests.codes.not_found:
                    return await ctx.send(_("""
I couldn't find this word... 🙁
You can set the article yourself, though! (cf. `{}help {}`)
""").format(ctx.bot.command_prefix, ctx.invoked_with))
                else:
                    raise e

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
