# app/logger.py
import logging
from pathlib import Path

def setup_logger(
    name: str = "calculator", 
    log_file: str = "calculator.log", 
    level=logging.INFO
) -> logging.Logger:
    """
    Sets up a logger with both console and file handlers.
    Avoids adding duplicate handlers if called multiple times.
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler(log_path, mode="a")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info("Logger initialized.")

    return logger


# Shared logger instance
logger = setup_logger()


def main():
    """
    Example usage of the logger. This is the entry point when running
    this file directly.
    """
    log = setup_logger("test_logger", "logs/test_run.log")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")


if __name__ == "__main__":
    main()
