from discord.ext.commands import DefaultHelpCommand

import discord


class TaalbotHelpCommand(DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        content = discord.Embed(title = 'Taalbot')

        if bot.description:
            content.description = bot.description

        await self.get_destination().send(embed=content)
