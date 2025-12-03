import os
import sys
import time
from time import strftime

import stackprinter
from loguru import logger
from yaml import safe_load as load

from src.backend import bootstrap_browser, bootstrap_code_page
from src.lib.exceptions import UserCausedHalt
from src.lib.logcreation import formatter, formatter_sensitive


def load_configuration(config_file_path="user/cfg.yml") -> dict:
    """

    We're defining a function f: yaml -> Config
    """

    with open(config_file_path, "r") as configuration_file:

        config = load(configuration_file)

        formatting = formatter

        if config["sensitiveDebug"] == "True":

            formatting = formatter_sensitive

        if config["logCreation"] == "True":
            logger.add(
                "log/{0}.log".format(
                    strftime("%d-%m-%Y-%H_%M_%S", time.localtime(time.time()))
                ),
                colorize=False,
                backtrace=True,
                format=formatting,
            )

        logger.add(sys.stderr, format=formatting, colorize=True, backtrace=True)

        logger.debug(
            f"Loaded configuration file located at {os.path.realpath(configuration_file.name)}"
        )
        return config


def userFacing(configuration: dict):

    validProgramModes: set = {"login", "reset"}

    if configuration["programMode"].lower() not in validProgramModes:

        raise ValueError("Invalid program mode inputted!")

    validCodeModes: set = {"normal", "backup", "backup_let", "both"}

    if configuration["codeMode"].lower() not in validCodeModes:

        raise ValueError("Invalid code-generation mode inputted!")

    while True:

        driver = bootstrap_browser(configuration)

        bootstrap_code_page(driver, configuration)


if __name__ == "__main__":

    try:

        logger.remove()

        userFacing(load_configuration())

    except UserCausedHalt:

        logger.info("User halted the program!")

        sys.exit(130)
