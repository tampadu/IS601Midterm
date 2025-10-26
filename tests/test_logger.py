# tests/test_logger_full.py
import logging
from unittest.mock import patch
import pytest
from app.logger import setup_logger, logger, main

def test_setup_logger_returns_logger(tmp_path):
    log_file = tmp_path / "calc.log"
    log = setup_logger("test_logger", str(log_file))
    assert isinstance(log, logging.Logger)
    assert log.name == "test_logger"
    # Two handlers: StreamHandler + FileHandler
    handler_types = [type(h) for h in log.handlers]
    assert logging.StreamHandler in handler_types
    assert logging.FileHandler in handler_types

def test_setup_logger_no_duplicate_handlers(tmp_path):
    log_file = tmp_path / "dup.log"
    logging.getLogger("dup_logger").handlers = []  # reset
    log1 = setup_logger("dup_logger", str(log_file))
    log2 = setup_logger("dup_logger", str(log_file))
    assert log1 is log2
    assert len(log1.handlers) == 2  # still only two

def test_logger_emits_messages(tmp_path):
    log_file = tmp_path / "emit.log"
    emitted = []

    class DummyHandler(logging.Handler):
        def emit(self, record):
            emitted.append(record)

    logging.getLogger("emit_logger").handlers = []  # reset
    with patch("app.logger.logging.FileHandler", return_value=DummyHandler()), \
         patch("app.logger.logging.StreamHandler", return_value=DummyHandler()):
        log = setup_logger("emit_logger", str(log_file))
        log.info("Info message")
        log.warning("Warning message")
        log.error("Error message")

    messages = [r.getMessage() for r in emitted]
    levels = [r.levelname for r in emitted]
    assert "Info message" in messages
    assert "Warning message" in messages
    assert "Error message" in messages
    assert "INFO" in levels
    assert "WARNING" in levels
    assert "ERROR" in levels

def test_logger_main_block_runs(tmp_path):
    log_file = tmp_path / "main_run.log"
    # Patch setup_logger to redirect file to tmp_path
    with patch("app.logger.setup_logger") as mock_setup:
        mock_log = logging.getLogger("mock_main")
        mock_log.handlers = []  # ensure no duplicate handlers
        mock_setup.return_value = mock_log
        main()
        mock_setup.assert_called()  # ensures main called setup_logger

def test_shared_logger_instance(tmp_path):
    log_file = tmp_path / "shared.log"
    log1 = setup_logger("shared_logger", str(log_file))
    log2 = setup_logger("shared_logger", str(log_file))
    assert log1 is log2
