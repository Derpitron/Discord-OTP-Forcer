import sys
import time
from time import strftime
from typing import Any

import stackprinter
from loguru import logger
from yaml import safe_load as load

from src.backend import bootstrap_browser, bootstrap_code_page, try_codes
from src.lib.logcreation import formatter, formatter_sensitive
from src.lib.types import (
    AccountConfig,
    Browser,
    CodeMode_Backup,
    CodeMode_Normal,
    Config,
    ProgramConfig,
    ProgramMode,
)


def load_configuration(account_config_path: str, program_config_path: str) -> Config:
    """
    Parses the config files to our python object.
    """

    accountConfig: AccountConfig
    programConfig: ProgramConfig

    with open(account_config_path, "r") as account_config_file:
        accountConfig = AccountConfig(**(load(account_config_file)))

    # need a custom parser for this cus of custom types.
    with open(program_config_path, "r") as program_config_file:
        program_config_dict: dict[str, str | bool | float | int] = load(
            program_config_file
        )
        # If the user gives a custom regex here i'll assume it's a backup code.
        programConfig = ProgramConfig(
            programMode=ProgramMode[(program_config_dict["programMode"])],
            codeMode=(
                CodeMode_Normal()
                if program_config_dict["codeMode"] == "Normal"
                else (
                    CodeMode_Backup()
                    if program_config_dict["codeMode"] == "Backup"
                    else CodeMode_Backup(program_config_dict["codeMode"])
                )
            ),
            browser=Browser[(program_config_dict["browser"])],
            headless=program_config_dict["headless"],
            logCreation=program_config_dict["logCreation"],
            sensitiveDebug=program_config_dict["sensitiveDebug"],
            logLevel=program_config_dict["logLevel"],
            elementLoadTolerance=program_config_dict["elementLoadTolerance"],
            usualAttemptDelayRange=(
                program_config_dict["usualAttemptDelayMin"],
                program_config_dict["usualAttemptDelayMax"],
            ),
            ratelimitedAttemptDelayRange=(
                program_config_dict["ratelimitedAttemptDelayMin"],
                program_config_dict["ratelimitedAttemptDelayMax"],
            ),
        )

        formatting = formatter
        if programConfig.sensitiveDebug == True:
            formatting = formatter_sensitive
        if programConfig.logCreation == True:
            logger.add(
                "log/{0}.log".format(
                    strftime("%d-%m-%Y-%H_%M_%S", time.localtime(time.time()))
                ),
                colorize=False,
                backtrace=True,
                format=formatting,
            )

        logger.add(
            sys.stderr,
            format=formatting,
            colorize=True,
            backtrace=True,
            level=programConfig.logLevel,
        )
        if programConfig.logLevel in ("SENSITIVE", "DEBUG"):
            import stackprinter

            stackprinter.set_excepthook(style="darkbg2")
        logger.debug(f"Loaded config/account.yml, config/program.yml config files.")

        return Config(account=accountConfig, program=programConfig)


def main(config: Config) -> None:
    try_codes(*bootstrap_code_page(*bootstrap_browser(config)))


if __name__ == "__main__":
    logger.remove()
    main(load_configuration("config/account.yml", "config/program.yml"))
