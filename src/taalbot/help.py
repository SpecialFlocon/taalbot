from discord.ext.commands import HelpCommand

from .const import TAALBOT_CMD_BLUEPRINT

import discord


class TaalbotHelpCommand(HelpCommand):
    def __init__(self, **options):
        self.embed = options.pop('embed', discord.Embed())

        super().__init__(**options)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        self.embed.title = 'Commands'
        self.embed.description = """
            Here's a list of the commands you can run, and their purpose.
            Type `!help <command>` to get detailed help.
        """
        self.embed.colour = discord.Colour.blue()

        filtered = await self.filter_commands(bot.commands, sort=True)
        for c in filtered:
            self.embed.add_field(
                name='{}{}'.format(bot.command_prefix, c.name),
                value=c.brief or 'No info',
                inline=False,
            )

        await self.get_destination().send(embed=self.embed)

    async def send_command_help(self, command):
        try:
            self.embed = discord.Embed.from_dict(TAALBOT_CMD_BLUEPRINT[command.name])
        except KeyError:
            return await self.send_error_message("I don't have a command called {}!".format(command.name))

        await self.get_destination().send(embed=self.embed)

    async def prepare_help_command(self, ctx, command=None):
        self.embed = discord.Embed()
        await super().prepare_help_command(ctx, command)
