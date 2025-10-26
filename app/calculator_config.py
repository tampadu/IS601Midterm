# app/calculator_config.py
import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()  # loads from .env if present

@dataclass
class Config:
    AUTO_SAVE: bool
    AUTO_SAVE_PATH: str
    HISTORY_PATH: str

def load_config() -> Config:
    auto_save = os.getenv("AUTO_SAVE", "false").lower() in ("1","true","yes")
    auto_save_path = os.getenv("AUTO_SAVE_PATH", "history.csv")
    history_path = os.getenv("HISTORY_PATH", "history.csv")

    # validate
    if not Path(auto_save_path).parent.exists():
        # try creating dir if needed
        try:
            Path(auto_save_path).parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Invalid AUTO_SAVE_PATH: {e}")

    return Config(AUTO_SAVE=auto_save, AUTO_SAVE_PATH=auto_save_path, HISTORY_PATH=history_path)
