from src import taalbot

import pytest


class TestLaunch:
    def test_exit_on_no_token(self):
        with pytest.raises(SystemExit):
            taalbot.main([])

    def test_value_error_on_empty_config(self, monkeypatch):
        monkeypatch.setenv("TAALTOOL_BOT_TOKEN", "test")
        args = ['-c', '/tmp/test']
        with pytest.raises(ValueError):
            taalbot.main(args)

    def test_exit_on_failed_config_read(self, monkeypatch):
        monkeypatch.setenv("TAALTOOL_BOT_TOKEN", "test")
        args = ['-c', '/invalid/path']
        with pytest.raises(SystemExit):
            taalbot.main(args)
