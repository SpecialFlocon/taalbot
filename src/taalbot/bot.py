from discord.ext import commands

from . import const

import discord
import logging
import traceback


class Taalbot(commands.Bot):
    def __init__(self, config, **kwargs):
        self.api_url = config.get('apiUrl') # For convenience
        self.api_version = const.API_VERSION
        self.config = config
        self.log_channel = None

        super().__init__(command_prefix=self.config.get('commandPrefix'), **kwargs)

    def get_log_channel(self):
        log_channel_name = self.config.get('logChannel')
        if not log_channel_name:
            logging.info("No channel name was given in the configuration, disabling in-channel logs.")
            return None

        for c in self.get_all_channels():
            # Skip guilds that are not the current one
            if c.guild.id != self.config.get('guildId'):
                continue

            # Skip non-text channels, and text channels whose name don't match
            if c.type != discord.ChannelType.text or c.name != log_channel_name:
                continue

            # Log then bail out if bot doesn't have enough permissions to send messages
            if not c.permissions_for(c.guild.me).send_messages:
                logging.warning("Bot does not have the permission to send messages to #{}. Logs will only be available on stderr.".format(log_channel_name))
                return None

            return c

        logging.warning("Channel #{} was not found anywhere. Logs will only be available on stderr.".format(log_channel_name))
        return None

    async def on_ready(self):
        self.log_channel = self.get_log_channel()
        logging.info("taalbot has joined the chat!")

    async def on_command_error(self, context, exception):
        if self.extra_events.get('on_command_error', None):
            return

        if hasattr(context.command, 'on_error'):
            return

        cog = context.cog
        if cog:
            if commands.Cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        if isinstance(exception, commands.errors.CommandNotFound):
            return

        if self.log_channel:
            await self.log_channel.send(const.LOG_CHANNEL_MSG.format(exception))

        logging.error(traceback.format_exception(type(exception), exception, exception.__traceback__))
