import os
import pytest
from pathlib import Path
from app.calculator_config import load_config, Config


# --- Unit Tests for load_config() ---

def test_load_config_defaults(monkeypatch):
    """Test that default values are loaded when no environment variables are set."""
    monkeypatch.delenv("CALCULATOR_AUTO_SAVE", raising=False)
    monkeypatch.delenv("CALCULATOR_AUTO_SAVE_PATH", raising=False)
    monkeypatch.delenv("CALCULATOR_HISTORY_FILE", raising=False)

    config = load_config()
    assert isinstance(config, Config)
    assert config.CALCULATOR_AUTO_SAVE is False
    assert config.CALCULATOR_AUTO_SAVE_PATH == config.CALCULATOR_HISTORY_FILE
    assert config.CALCULATOR_HISTORY_FILE == "data/history.csv"


@pytest.mark.parametrize(
    "env_value,expected",
    [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ],
)
def test_load_config_auto_save_variants(monkeypatch, env_value, expected):
    """Test CALCULATOR_AUTO_SAVE parsing for different truthy/falsey environment values."""
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", env_value)
    config = load_config()
    assert config.CALCULATOR_AUTO_SAVE == expected


def test_load_config_custom_paths(monkeypatch, tmp_path):
    """Test that custom paths are used when provided."""
    auto_save_path = tmp_path / "autosave" / "data.csv"
    history_file = tmp_path / "history" / "log.csv"
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE_PATH", str(auto_save_path))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(history_file))

    config = load_config()
    assert config.CALCULATOR_AUTO_SAVE_PATH == str(auto_save_path)
    assert config.CALCULATOR_HISTORY_FILE == str(history_file)


def test_load_config_creates_missing_directory(monkeypatch, tmp_path):
    """Test that a missing directory for CALCULATOR_AUTO_SAVE_PATH is created if necessary."""
    missing_dir = tmp_path / "nonexistent_dir"
    file_path = missing_dir / "file.csv"
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE_PATH", str(file_path))

    config = load_config()
    # The directory should now exist
    assert missing_dir.exists()
    assert config.CALCULATOR_AUTO_SAVE_PATH == str(file_path)


def test_load_config_raises_on_invalid_path(monkeypatch):
    """Test that load_config raises ValueError when directory creation fails."""
    # Patch Path.mkdir to raise an exception
    def mock_mkdir(*args, **kwargs):
        raise PermissionError("cannot create directory")

    monkeypatch.setenv("CALCULATOR_AUTO_SAVE_PATH", "/invalid_dir/test.csv")
    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    with pytest.raises(ValueError, match="Unable to create directory"):
        load_config()
