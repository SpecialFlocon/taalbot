from discord.ext.commands import HelpCommand
from string import Template

from .utils import TAALBOT_CMD_BLUEPRINT

import copy
import discord
import logging


class TaalbotHelpCommand(HelpCommand):
    def __init__(self, **options):
        self.embed = options.pop('embed', discord.Embed())

        super().__init__(**options)

    def command_not_found(self, string):
        return _("I don't have a command called `{}`, but I have a `help` command!").format(string)

    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot

        self.embed.title = _('Commands')
        self.embed.description = _("""
Here's a list of the commands you can run, and their purpose.
Type `{}help command` to get detailed help for given command.
""".format(bot.command_prefix))
        self.embed.colour = discord.Colour.blue()

        filtered = await self.filter_commands(bot.commands, sort=True)
        for c in filtered:
            cmd_names = [c.name] + c.aliases
            field_title = ', '.join((lambda x: '{}{}'.format(bot.command_prefix, x))(a) for a in cmd_names).strip()

            self.embed.add_field(
                name=field_title,
                value=c.brief or _('No description'),
                inline=False,
            )

        await self.get_destination().send(embed=self.embed)

    async def send_command_help(self, command):
        try:
            d = TAALBOT_CMD_BLUEPRINT[command.name]
        except KeyError:
            logging.warning(_("Failed to load help data for command `{}`".format(command.name)))
            return

        cmd_blueprint = copy.deepcopy(d)
        for f in cmd_blueprint.get('fields', []):
            v = f.get('value', None)
            if v:
                f['value'] = Template(v).safe_substitute(
                    both_articles=_('both'),
                    cmd=command.name,
                    prefix=self.context.bot.command_prefix
                )

        self.embed = discord.Embed.from_dict(cmd_blueprint)
        await self.get_destination().send(embed=self.embed)

    async def prepare_help_command(self, ctx, command=None):
        self.embed = discord.Embed()
        await super().prepare_help_command(ctx, command)
