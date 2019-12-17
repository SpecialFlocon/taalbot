import gettext
import logging
import pytest


t = gettext.NullTranslations()
t.install()

from src.taalbot import bot


class TestBot:
    """
    This class contains tests for parts of Taalbot (a subclass of discord.ext.commands.Bot)
    that do not rely on Discord APIs.
    """

    def test_new_bot_instance_init_method(self):
        cfg = {'apiUrl': "http://api.url", 'commandPrefix': "?", 'guildId': 1}
        t = bot.Taalbot(cfg)
        assert cfg.get('apiUrl') == t.api_url and \
            cfg.get('commandPrefix') == t.config.get('commandPrefix') and \
            cfg.get('guildId') == t.config.get('guildId')

    def test_no_log_channel(self, caplog):
        caplog.set_level(logging.INFO)
        cfg = {'apiUrl': "http://api.url", 'commandPrefix': "?", 'guildId': 1}
        t = bot.Taalbot(cfg)
        t.log_channel = t.get_log_channel()
        assert not t.log_channel and "No channel name was given" in caplog.text
