from __future__ import annotations

import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "app.log"

DEFAULT_FORMATTER = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def ensure_log_dir() -> None:
    """Ensure that the log directory exists."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_file_handler(level: int = logging.INFO, log_file: Path | str | None = None) -> logging.Handler:
    """Return a file handler writing to the configured log file."""
    ensure_log_dir()
    target_file = Path(log_file) if log_file is not None else LOG_FILE
    handler = logging.FileHandler(target_file, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(DEFAULT_FORMATTER)
    return handler


def configure_logger(
    name: str = "ai_financial_research_platform",
    level: int = logging.INFO,
    log_file: Path | str | None = None,
) -> logging.Logger:
    """Configure and return a logger that writes to a single file."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        logger.addHandler(get_file_handler(level=level, log_file=log_file))
    return logger


def get_logger(name: str = "ai_financial_research_platform") -> logging.Logger:
    """Get the default configured logger."""
    return configure_logger(name=name)
