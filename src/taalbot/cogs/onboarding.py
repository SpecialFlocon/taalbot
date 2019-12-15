from discord.ext import commands

from .. import const

import discord
import logging


class Onboarding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dm_instructions(self, member):
        await member.send("Onboarding process start! And done.")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.dm_instructions(member)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def onboard(self, ctx, *, member: discord.Member=None):
        member = member or ctx.author
        logging.info("Onboarding for user {} has been requested by {}.".format(member, ctx.author))
        await self.dm_instructions(member)

    @onboard.error
    async def onboard_error(self, ctx, error):
        author = ctx.message.author
        if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.MissingAnyRole):
            await ctx.send(_("{}, you are not allowed to run this command. If you'd like to go through on-boarding process again, ask someone with enough permissions to initiate it for you.").format(author.mention))
            if ctx.bot.log_channel:
                await ctx.bot.log_channel.send("""
User {} without sufficient permissions tried to start the on-boarding process by running:
```
{}
```
""".format(author.mention, ctx.message.content))

            logging.info("Onboarding command invoked by user {} with insufficient permissions".format(author.name))
            logging.debug("Permissions for user {}: {}".format(author.name, ctx.channel.permissions_for(author)))
        else:
            if ctx.bot.log_channel:
                await self.log_channel.send(const.LOG_CHANNEL_MSG.format(error))
            logging.error(traceback.format_exception(type(error), error, error.__traceback__))

def setup(bot):
    bot.add_cog(Onboarding(bot))
