from discord.ext import commands

from . import const
from .help import TaalbotHelpCommand

import argparse
import logging
import os
import sys
import yaml


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

if __name__ == '__main__':
    try:
        token = os.environ['TAALTOOL_BOT_TOKEN']
    except KeyError:
        print("Bot token is not present, please set it in the TAALTOOL_BOT_TOKEN environment variable.")
        sys.exit(1)

    a = argparse.ArgumentParser(description='taalbot')
    a.add_argument('-c', '--config', help='taalbot configuration file', default='/etc/taalbot/config.yaml')
    args = a.parse_args()

    try:
        config_file = open(args.config)
    except OSError as e:
        print("Error opening configuration file: {}".format(e))
        sys.exit(1)

    config = yaml.safe_load(config_file)
    if not config:
        raise ValueError("Configuration file is empty.")

    # Enable logging
    logging.basicConfig()

    taalbot = Taalbot(
        config,
        help_command=TaalbotHelpCommand(),
        description=_("A sensible bot that helps you practicing languages")
    )

    # Register extensions
    taalbot.load_extension('taalbot.cogs.lidwoord')

    taalbot.run(token)
