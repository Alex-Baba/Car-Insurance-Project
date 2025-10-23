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
    # In container we default to console logging unless explicitly enabled AND not in docker env.
    log_to_file_env = os.getenv("LOG_TO_FILE", "0") == "1"
    log_to_file = log_to_file_env and env not in {"docker"}

    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(log_level)
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(console)
        if log_to_file:
            # Ensure writable path (create directory if specified like logs/app.log)
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                except Exception:
                    # Fallback to console only if we cannot create directory
                    return
            try:
                fh = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
                fh.setFormatter(logging.Formatter("%(message)s"))
                root.addHandler(fh)
            except PermissionError:
                # Ignore file handler if path unwritable in container
                pass

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