import gettext
import pytest
import requests

t = gettext.NullTranslations()
t.install()

from src.taalbot import bot
from src.taalbot.cogs.lidwoord import LidwoordCog


class TestLidwoord:
    """
    This class contains tests for HTTP requests to taalapi.
    """

    def test_get_article_success(self, monkeypatch):
        class MockResponse:
            @staticmethod
            def json():
                return {'id': 1, 'key': "value"}

            @staticmethod
            def raise_for_status():
                pass

        def mock_get(self, *args, **kwargs):
            return MockResponse()

        cfg = {'apiUrl': "http://api.url", 'commandPrefix': "?", 'guildId': 1}
        t = bot.Taalbot(cfg)

        monkeypatch.setattr(requests, "get", mock_get)
        result = LidwoordCog(t).get_articles()
        assert result['id'] == 1 and result['key'] == "value"

    def test_get_article_failure(self, monkeypatch):
        class MockResponse:
            @staticmethod
            def json():
                return None

            @staticmethod
            def raise_for_status():
                raise requests.HTTPError

        def mock_get(self, *args, **kwargs):
            return MockResponse()

        cfg = {'apiUrl': "http://api.url", 'commandPrefix': "?", 'guildId': 1}
        t = bot.Taalbot(cfg)

        monkeypatch.setattr(requests, "get", mock_get)
        with pytest.raises(requests.HTTPError):
            LidwoordCog(t).get_articles()

    def test_get_word_success(self, monkeypatch):
        class MockResponse:
            @staticmethod
            def json():
                return {'id': 1, 'word': "word", 'article': "article"}

            @staticmethod
            def raise_for_status():
                pass

        def mock_get(self, *args, **kwargs):
            return MockResponse()

        cfg = {'apiUrl': "http://api.url", 'commandPrefix': "?", 'guildId': 1}
        t = bot.Taalbot(cfg)

        monkeypatch.setattr(requests, "get", mock_get)
        result = LidwoordCog(t).get_or_learn_word('word')
        assert result['id'] == 1 and result['word'] == "word"

    def test_get_word_failure(self, monkeypatch):
        class MockResponse:
            @staticmethod
            def json():
                return None

            @staticmethod
            def raise_for_status():
                raise requests.HTTPError

        def mock_get(self, *args, **kwargs):
            return MockResponse()

        cfg = {'apiUrl': "http://api.url", 'commandPrefix': "?", 'guildId': 1}
        t = bot.Taalbot(cfg)

        monkeypatch.setattr(requests, "get", mock_get)
        with pytest.raises(requests.HTTPError):
            LidwoordCog(t).get_or_learn_word('word')
