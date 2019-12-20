from .exceptions import MissingConfigKeyError

import argparse
import gettext
import logging
import os
import sys
import yaml


def main(argv=None, test=False):
    try:
        token = os.environ['TAALTOOL_BOT_TOKEN']
    except KeyError:
        print("Bot token is not present, please set it in the TAALTOOL_BOT_TOKEN environment variable.")
        sys.exit(1)

    a = argparse.ArgumentParser(description='taalbot')
    a.add_argument('-c', '--config', help='taalbot configuration file', default='/etc/taalbot/config.yaml')
    a.add_argument('-v', '--verbose', help='Control verbosity level', action='count', default=0)
    args = a.parse_args(argv)

    try:
        config_file = open(args.config)
    except OSError as e:
        print("Error opening configuration file: {}".format(e))
        sys.exit(1)

    config = yaml.safe_load(config_file)
    if not config:
        raise ValueError("Configuration file is empty.")

    REQUIRED_CONFIG_PARAMS = ['apiUrl', 'commandPrefix', 'guildId']
    for p in REQUIRED_CONFIG_PARAMS:
        if not config.get(p):
            raise MissingConfigKeyError(p)

    # Enable logging
    if args.verbose == 0:
        log_level = logging.INFO
    elif args.verbose >= 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.NOTSET
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=log_level)

    # Initialize localization
    try:
        t = gettext.translation('taalbot', 'locales')
    except FileNotFoundError as e:
        logging.warning("Failed to load translations: {}".format(e))
        t = gettext.NullTranslations()
    finally:
        t.install()

    # Bot<->Discord server actions cannot be easily tested.
    # If in test mode, the buck stops here, with a positive result.
    if test:
        return True

    # Taalbot and TaalbotHelpCommand depends on _() (gettext()) being present in __builtins__
    from .bot import Taalbot
    from .help import TaalbotHelpCommand

    taalbot = Taalbot(
        config,
        help_command=TaalbotHelpCommand(),
        description=_("A bot that helps you practicing languages")
    )

    # Register extensions
    taalbot.load_extension('taalbot.cogs.lidwoord')
    taalbot.load_extension('taalbot.cogs.onboarding')

    taalbot.run(token)
