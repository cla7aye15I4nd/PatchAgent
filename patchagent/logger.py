import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from colorama import Fore, Style, init

from patchagent.utils import debug_mode

init(autoreset=True)
LEVEL_COLORS = {
    logging.DEBUG: Fore.GREEN,
    logging.INFO: Fore.BLUE,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA,
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt, style="%"):
        super().__init__(fmt, datefmt, style)  # type: ignore

    def format(self, record):
        level_color = LEVEL_COLORS.get(record.levelno, Style.RESET_ALL)
        message = super().format(record)
        message = f"{level_color}{message}{Style.RESET_ALL}"
        return message


class CustomLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)


def setup_logger(
    log_file=None,
    level=logging.DEBUG if debug_mode() else logging.INFO,
    max_size=10000000,
    backups=5,
):
    """
    Creates a logger instance with colored and bold console output for certain levels.
    Automatically names log files based on the current date and time if not specified.
    """
    logger = CustomLogger(__name__)
    logger.setLevel(level)

    if not log_file:
        log_path = Path(__file__).parent / "logs"
        log_path.mkdir(exist_ok=True)
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = (log_path / f"{current_time}.log").resolve()

    file_handler = RotatingFileHandler(log_file, maxBytes=max_size, backupCount=backups)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    colored_formatter = ColoredFormatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler.setFormatter(colored_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logging.setLoggerClass(CustomLogger)
log = setup_logger()

if __name__ == "__main__":
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
