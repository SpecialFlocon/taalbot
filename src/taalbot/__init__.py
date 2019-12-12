from .bot import Taalbot

import argparse
import gettext
import logging
import os
import sys
import yaml


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

# Initialize localization
try:
    t = gettext.translation('taalbot', 'locales')
except FileNotFoundError as e:
    # Capture exceptions to report the error the way we want to.
    # TODO(thepib): using print() is a transient solution. Implement proper logging.
    print("Failed to load translations: {}".format(e))
    t = gettext.NullTranslations()
finally:
    t.install()

# TaalbotHelpCommand depends on _() (gettext()) being present in __builtins__
from .help import TaalbotHelpCommand

taalbot = Taalbot(
    config,
    help_command=TaalbotHelpCommand(),
    description=_("A sensible bot that helps you practicing languages")
)

# Register extensions
taalbot.load_extension('taalbot.cogs.lidwoord')

taalbot.run(token)
