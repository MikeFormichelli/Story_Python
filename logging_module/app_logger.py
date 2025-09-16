import logging
from logging.handlers import RotatingFileHandler


def logging_setup(
    name: str = "character_writing_app",
    log_file: str = "app.log",
    level: int = logging.DEBUG,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # prevent repeat handler set up:
    if logger.hasHandlers():
        return logger

    logger.propagate = True

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # handler:

    handler = RotatingFileHandler(
        f"logs/{log_file}", maxBytes=max_bytes, backupCount=backup_count
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)

    logger.addHandler(handler)

    return logger
