from yaml import safe_load as load

from src.config.config_validator import validate_account_config, validate_program_config
from src.lib.types import (
    AccountConfig,
    Browser,
    CensoredStr,
    CodeMode_Backup,
    CodeMode_Normal,
    Config,
    ProgramConfig,
    ProgramConfigDict,
    ProgramMode,
)


def _parse_code_mode(code_mode: str) -> CodeMode_Normal | CodeMode_Backup:
    match code_mode:
        case "Normal":
            return CodeMode_Normal()
        case "Backup":
            return CodeMode_Backup()
        case _:
            return CodeMode_Backup(code_mode)


def load_configuration(account_config_path: str, program_config_path: str) -> Config:
    """
    Parses the config files into our Python objects.
    Validation (syntax + values) is done before any parsing attempt.
    """
    accountConfig: AccountConfig
    programConfig: ProgramConfig

    validate_program_config(program_config_path)
    # account validation needs programMode, so we read program config first
    with open(program_config_path, "r") as _f:
        _mode: ProgramMode = ProgramMode[load(_f).get("programMode", "")]
    validate_account_config(account_config_path, _mode)

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

    check_updates: bool | None = program_config_dict.get("checkUpdates")

    # need a custom parser for this cus of custom types.
    # If the user gives a custom regex here i'll assume it's a backup code.

    programConfig = ProgramConfig(
        programMode=ProgramMode[(program_config_dict["programMode"])],
        codeMode=_parse_code_mode(program_config_dict["codeMode"]),
        checkUpdates=check_updates if check_updates is not None else False,
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

    return Config(account=accountConfig, program=programConfig)
