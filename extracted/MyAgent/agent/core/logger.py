"""Central logging for ParsAgent — rich console output + rotating file handler."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.logging import RichHandler

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_configured = set()


def get_logger(name: str = "parsagent") -> logging.Logger:
    """Return a logger that prints nicely to the console and persists to logs/agent.log."""
    logger = logging.getLogger(name)
    if name in _configured:
        return logger

    logger.setLevel(logging.INFO)

    console = RichHandler(rich_tracebacks=True, markup=True, show_path=False)
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    file_handler = RotatingFileHandler(
        LOG_DIR / "agent.log",
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
    )
    logger.addHandler(file_handler)

    logger.propagate = False
    _configured.add(name)
    return logger
