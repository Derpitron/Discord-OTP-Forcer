import sys
import time
from time import strftime

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
    ProgramConfigDict,
    CensoredStr,
)


def load_configuration(account_config_path: str, program_config_path: str) -> Config:
    """
    Parses the config files to our python object.
    """

    accountConfig: AccountConfig
    programConfig: ProgramConfig

    # We first read the program_config_file so we know if sensitiveDebug is active or not
    with open(program_config_path, "r") as program_config_file:
        program_config_dict: ProgramConfigDict = load(program_config_file)

    # And if it is, we convert the strings into the CensoredStr type
    with open(account_config_path, "r") as account_config_file:
        account_dict = load(account_config_file)

        if program_config_dict["sensitiveDebug"]:
            censored_account_dict = {}
            for key, value in account_dict.items():
                if value:
                    value = CensoredStr(value)
                censored_account_dict[key] = value

            accountConfig = AccountConfig(**censored_account_dict)
        else:
            accountConfig = AccountConfig(**account_dict)

        # need a custom parser for this cus of custom types.
        # If the user gives a custom regex here i'll assume it's a backup code.
        # fmt: off
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
        # fmt: on

        formatting = formatter
        if programConfig.sensitiveDebug:
            formatting = formatter_sensitive
        if programConfig.logCreation:
            # fmt: off
            logger.add(
                "log/{0}.log".format(
                    strftime("%d-%m-%Y-%H_%M_%S", time.localtime(time.time()))
                ),
                colorize=False,
                backtrace=True,
                format=formatting,
            )
            # fmt: on

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
        logger.debug("Loaded config/account.yml, config/program.yml config files.")

        return Config(account=accountConfig, program=programConfig)


if __name__ == "__main__":
    logger.remove()

    # innermost runs first.
    # fmt: off
    try_codes(
        *bootstrap_code_page(
            *bootstrap_browser(
                load_configuration("config/account.yml", "config/program.yml")
            )
        )
    )
    # fmt: on
