import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    CALCULATOR_LOG_DIR: str
    CALCULATOR_HISTORY_DIR: str
    CALCULATOR_HISTORY_FILE: str
    CALCULATOR_AUTO_SAVE: bool
    CALCULATOR_AUTO_SAVE_PATH: str
    CALCULATOR_MAX_HISTORY_SIZE: int
    CALCULATOR_PRECISION: int
    CALCULATOR_MAX_INPUT_VALUE: float
    CALCULATOR_DEFAULT_ENCODING: str
    HISTORY_PATH: str  # some tests expect this


def _bool_from_env(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).lower() in ("1", "true", "yes", "on")


def load_config() -> Config:
    log_dir = os.getenv("CALCULATOR_LOG_DIR", "logs")
    history_dir = os.getenv("CALCULATOR_HISTORY_DIR", "data")
    history_file = os.getenv("CALCULATOR_HISTORY_FILE", "data/history.csv")
    history_path = os.getenv("HISTORY_PATH", history_file)
    auto_save = _bool_from_env("CALCULATOR_AUTO_SAVE", "false")
    auto_save_path = os.getenv("CALCULATOR_AUTO_SAVE_PATH", history_file)

    max_history_size = int(os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000"))
    precision = int(os.getenv("CALCULATOR_PRECISION", "6"))
    max_input = float(os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e12"))
    encoding = os.getenv("CALCULATOR_DEFAULT_ENCODING", "utf-8")

    # Ensure directories exist
    for p in (log_dir, history_dir, Path(auto_save_path).parent):
        try:
            Path(p).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Unable to create directory {p}: {e}")

    return Config(
        CALCULATOR_LOG_DIR=str(log_dir),
        CALCULATOR_HISTORY_DIR=str(history_dir),
        CALCULATOR_HISTORY_FILE=str(history_file),
        CALCULATOR_AUTO_SAVE=auto_save,
        CALCULATOR_AUTO_SAVE_PATH=str(auto_save_path),
        CALCULATOR_MAX_HISTORY_SIZE=max_history_size,
        CALCULATOR_PRECISION=precision,
        CALCULATOR_MAX_INPUT_VALUE=max_input,
        CALCULATOR_DEFAULT_ENCODING=encoding,
        HISTORY_PATH=str(history_path),
    )
