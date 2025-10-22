import os
import logging
import structlog
from logging.handlers import RotatingFileHandler

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def setup_logging():
    env = os.getenv("APP_ENV", "dev").lower()
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    log_file = os.getenv("LOG_FILE", "app.log")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", "1048576"))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    log_to_file = os.getenv("LOG_TO_FILE", "1") == "1"

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(log_level)
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(console)
        if log_to_file:
            fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
            fh.setFormatter(logging.Formatter("%(message)s"))
            root.addHandler(fh)

    shared = [
        structlog.contextvars.merge_contextvars,        # if contextvars used
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if env == "prod":
        processors = shared + [
            structlog.processors.JSONRenderer()
        ]
    else:
        from structlog.dev import ConsoleRenderer
        processors = shared + [
            ConsoleRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

def get_logger():
    return structlog.get_logger()