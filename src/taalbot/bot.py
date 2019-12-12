from discord.ext import commands

from . import const

import logging


class Taalbot(commands.Bot):
    def __init__(self, config, **kwargs):
        self.api_url = config['apiUrl']
        self.api_version = const.API_VERSION

        super().__init__(command_prefix='!', **kwargs)

    async def on_command_error(self, context, exception):
        if self.extra_events.get('on_command_error', None):
            return

        if hasattr(context.command, 'on_error'):
            return

        cog = context.cog
        if cog:
            if commands.Cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        logging.error(exception)
        logging.debug(exception.__traceback__)
