import logging
import os

_log = None  # private singleton


def setup_logger(name="metamark", log_dir="logs", level=logging.INFO):
    global _log
    if _log is not None:
        return _log

    os.makedirs(log_dir, exist_ok=True)
    logfile = os.path.join(log_dir, "metamark.log")

    logger = logging.getLogger(name)
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
        )
    )

    if not logger.handlers:
        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    _log = logger
    return _log


def get_logger():
    if _log is None:
        raise RuntimeError("Logger not initialized. Call setup_logger() first.")
    return _log


def log_action(action, path, status="INFO"):
    """
    Log a standardized action message.
    Example: [COPY] /path/to/image.jpg
    """
    message = f"[{action.upper()}] {path}"
    if status == "INFO":
        _log.info(message)
    elif status == "DEBUG":
        _log.debug(message)
    elif status == "WARNING":
        _log.warning(message)
    elif status == "ERROR":
        _log.error(message)
