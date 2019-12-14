from src import taalbot
from src.taalbot.exceptions import MissingConfigKeyError

import pytest


working_config = """
apiUrl: http://api.url
commandPrefix: "?"
guildId: 1
"""

class TestLaunch:
    def test_exit_on_no_token(self):
        with pytest.raises(SystemExit):
            taalbot.main([], test=True)

    def test_value_error_on_empty_config(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TAALTOOL_BOT_TOKEN", "test")
        f = tmp_path / "empty.yaml"
        f.touch()
        args = ['-c', str(f)]
        with pytest.raises(ValueError):
            taalbot.main(args, test=True)

    def test_exit_on_failed_config_read(self, monkeypatch):
        monkeypatch.setenv("TAALTOOL_BOT_TOKEN", "test")
        args = ['-c', '/invalid/path']
        with pytest.raises(SystemExit):
            taalbot.main(args, test=True)

    def test_missing_one_required_parameter(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TAALTOOL_BOT_TOKEN", "test")
        mock_config = """
commandPrefix: "?"
guildId: 1
"""
        f = tmp_path / "config.yaml"
        f.write_text(mock_config)
        args = ['-c', str(f)]
        with pytest.raises(MissingConfigKeyError):
            taalbot.main(args, test=True)

        f.unlink()
        mock_config = """
apiUrl: http://api.url
guildId: 1
"""

        f.write_text(mock_config)
        with pytest.raises(MissingConfigKeyError):
            taalbot.main(args, test=True)

        f.unlink()
        mock_config = """
apiUrl: http://api.url
commandPrefix: "?"
"""

        f.write_text(mock_config)
        with pytest.raises(MissingConfigKeyError):
            taalbot.main(args, test=True)

    def test_missing_two_required_parameters(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TAALTOOL_BOT_TOKEN", "test")
        mock_config = """
guildId: 1
"""
        f = tmp_path / "config.yaml"
        f.write_text(mock_config)
        args = ['-c', str(f)]
        with pytest.raises(MissingConfigKeyError):
            taalbot.main(args, test=True)

        f.unlink()
        mock_config = """
commandPrefix: "?"
"""

        f.write_text(mock_config)
        with pytest.raises(MissingConfigKeyError):
            taalbot.main(args, test=True)

        f.unlink()
        mock_config = """
apiUrl: http://api.url
"""

        f.write_text(mock_config)
        with pytest.raises(MissingConfigKeyError):
            taalbot.main(args, test=True)

    def test_working_config(self, monkeypatch, tmp_path):
        monkeypatch.setenv("TAALTOOL_BOT_TOKEN", "test")
        mock_config = working_config
        f = tmp_path / "config.yaml"
        f.write_text(mock_config)
        args = ['-c', str(f)]
        assert taalbot.main(args, test=True)
