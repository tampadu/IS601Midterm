import logging
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "calculator", log_file: str = "calculator.log", level=logging.INFO) -> logging.Logger:
    # Ensure the directory for the log file exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        # Log format
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


# Example: get a shared logger instance
logger = setup_logger()

if __name__ == "__main__":
    # Quick test
    log = setup_logger("test_logger", "logs/test_run.log")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
