import sys
import time
from time import strftime

from loguru import logger

from src.lib.types import ProgramConfig
from src.logger.logcreation import formatter, formatter_sensitive


def initialize_check_logger() -> None:
    """
    Removes the default loguru sink and adds a custom one for the logs
    of the config validator.
    """
    logger.remove()

    logger.add(
        sys.stderr,
        format=formatter,
        colorize=True,
        backtrace=True,
        level="INFO",
    )


def initialize_logger(config: ProgramConfig) -> None:
    """
    Removes the default loguru sink and adds a custom one for the logs
    of the rest of the program.
    """
    logger.remove()

    formatting = formatter_sensitive if config.sensitiveDebug else formatter

    if config.logCreation:
        logger.add(
            "log/{}.log".format(strftime("%d-%m-%Y-%H_%M_%S", time.localtime(time.time()))),
            colorize=False,
            backtrace=True,
            format=formatting,
        )

    logger.add(
        sys.stderr,
        format=formatting,
        colorize=True,
        backtrace=True,
        level=config.logLevel,
    )

    logger.debug("Loaded config/account.yml and config/program.yml config files.")
