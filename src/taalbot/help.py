from discord.ext.commands import HelpCommand

from .const import TAALBOT_CMD_BLUEPRINT

import discord


class TaalbotHelpCommand(HelpCommand):
    def __init__(self, **options):
        self.embed = options.pop('embed', discord.Embed())

        super().__init__(**options)

    def command_not_found(self, string):
        return "I don't have a command called `{}`, but I have a `help` command!".format(string)

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
            cmd_names = [c.name] + c.aliases
            field_title = ', '.join((lambda x: '{}{}'.format(bot.command_prefix, x))(a) for a in cmd_names).strip()

            self.embed.add_field(
                name=field_title,
                value=c.brief or 'No description',
                inline=False,
            )

        await self.get_destination().send(embed=self.embed)

    async def send_command_help(self, command):
        self.embed = discord.Embed.from_dict(TAALBOT_CMD_BLUEPRINT[command.name])
        await self.get_destination().send(embed=self.embed)

    async def prepare_help_command(self, ctx, command=None):
        self.embed = discord.Embed()
        await super().prepare_help_command(ctx, command)
