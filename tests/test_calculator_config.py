import pytest
from app.calculator_config import load_config, Config
from pathlib import Path
import os
import shutil


@pytest.fixture
def clean_env(monkeypatch):
    """Clear relevant environment variables for testing defaults."""
    keys = [
        "CALCULATOR_LOG_DIR",
        "CALCULATOR_HISTORY_DIR",
        "CALCULATOR_HISTORY_FILE",
        "CALCULATOR_AUTO_SAVE",
        "CALCULATOR_AUTO_SAVE_PATH",
        "CALCULATOR_MAX_HISTORY_SIZE",
        "CALCULATOR_PRECISION",
        "CALCULATOR_MAX_INPUT_VALUE",
        "CALCULATOR_DEFAULT_ENCODING",
        "HISTORY_PATH",
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)


def test_load_config_defaults(clean_env):
    """Test that default values are loaded correctly."""
    config = load_config()

    assert isinstance(config, Config)
    assert config.CALCULATOR_AUTO_SAVE in (True, False)
    assert config.CALCULATOR_AUTO_SAVE_PATH.endswith("history.csv")
    assert Path(config.CALCULATOR_AUTO_SAVE_PATH).parent.exists()
    assert config.HISTORY_PATH.endswith("history.csv")


@pytest.mark.parametrize(
    "value,expected",
    [("true", True), ("1", True), ("yes", True), ("false", False), ("0", False), ("no", False)]
)
def test_load_config_auto_save_variants(clean_env, monkeypatch, value, expected):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", value)
    config = load_config()
    assert config.CALCULATOR_AUTO_SAVE == expected


def test_load_config_custom_paths(clean_env, tmp_path, monkeypatch):
    """Test that custom paths from env are respected."""
    log_dir = tmp_path / "logs"
    history_dir = tmp_path / "history_dir"
    history_file = tmp_path / "my_history.csv"

    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(log_dir))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(history_dir))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(history_file))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE_PATH", str(history_file))
    monkeypatch.setenv("HISTORY_PATH", str(history_file))

    config = load_config()

    assert config.CALCULATOR_LOG_DIR == str(log_dir)
    assert config.CALCULATOR_HISTORY_DIR == str(history_dir)
    assert config.CALCULATOR_HISTORY_FILE == str(history_file)
    assert config.CALCULATOR_AUTO_SAVE_PATH == str(history_file)
    assert config.HISTORY_PATH == str(history_file)
    # Directories should exist
    assert Path(config.CALCULATOR_LOG_DIR).exists()
    assert Path(config.CALCULATOR_HISTORY_DIR).exists()


def test_load_config_creates_missing_directory(clean_env, tmp_path, monkeypatch):
    """Test that missing directories are auto-created."""
    missing_dir = tmp_path / "missing_dir"
    history_file = tmp_path / "history.csv"

    monkeypatch.setenv("CALCULATOR_LOG_DIR", str(missing_dir))
    monkeypatch.setenv("CALCULATOR_HISTORY_DIR", str(tmp_path / "history"))
    monkeypatch.setenv("CALCULATOR_HISTORY_FILE", str(history_file))
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE_PATH", str(history_file))
    monkeypatch.setenv("HISTORY_PATH", str(history_file))

    config = load_config()
    assert Path(config.CALCULATOR_LOG_DIR).exists()
    assert Path(config.CALCULATOR_HISTORY_DIR).exists()
    assert Path(config.CALCULATOR_AUTO_SAVE_PATH).parent.exists()
