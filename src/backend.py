# Import dependencies and libraries
import json
import secrets
import time
from pprint import pformat
from typing import Any, Tuple

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
from .lib.types import (
    Browser,
    CodeError,
    CodeMode_Backup,
    CodeMode_Normal,
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
    # TODO: implement proper detach mode so the browser can run without crashing, if the program closes
    match config.program.browser:
        case Browser.Chrome:
            HARDEN_WEB_STORAGE_JS = r"""
                (function hardenWebStorage() {
                  if (typeof window === 'undefined') return;
                
                  function lockProperty(obj, prop) {
                    if (!obj) return;
                
                    var desc;
                    try {
                      desc = Object.getOwnPropertyDescriptor(obj, prop);
                    } catch (e) {
                      return;
                    }
                
                    if (!desc || !desc.get) return;
                
                    if (desc.configurable === false) return;
                
                    try {
                      Object.defineProperty(obj, prop, {
                        get: desc.get,
                        set: desc.set,
                        enumerable: desc.enumerable,
                        configurable: false
                      });
                    } catch (e) {
                      // ignore
                    }
                  }
                
                  try {
                    lockProperty(window, 'localStorage');
                    lockProperty(window, 'sessionStorage');
                  } catch (e) {}
                
                  try {
                    if (typeof Window !== 'undefined' && Window.prototype) {
                      lockProperty(Window.prototype, 'localStorage');
                      lockProperty(Window.prototype, 'sessionStorage');
                    }
                  } catch (e) {}
                })();
                """

            opts = ChromeOptions()
            opts.add_argument("--lang=en-US")
            if config.program.headless:
                opts.add_argument("--log-level=1")
            # fmt: off
            driver = uc.Chrome(headless=config.program.headless, options=opts)
            # fmt: on
            driver.execute_cdp_cmd(
                "Network.setBlockedURLs",
                {
                    "urls": [
                        "a.nel.cloudflare.com/report",
                        "https://discord.com/api/v10/science",
                        "https://discord.com/api/v9/science",
                        "sentry.io",
                    ]
                },
            )
            driver.execute_cdp_cmd("Network.enable", {})
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": HARDEN_WEB_STORAGE_JS},
            )
            logger.debug("Fixed compatibility polyfill")
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

    captcha_box: tuple[ByType, str] = (By.CLASS_NAME, "container__8a031")
    # infinitely loop until captcha box is detected
    while True:
        try:
            while True:
                # if captcha box is detected, loop infinitely until the user solves it (captcha box disappears)
                captcha_box_test: Element = driver.find_element(*captcha_box)
        except NoSuchElementException:
            # if captcha box disappears, exit the loop
            break
    del captcha_box

    # Check if the code field exists
    try:
        #fmt: off
        code_field: tuple[ByType, str] = (By.CLASS_NAME, "_49fc18ba07c5025f-header")
        code_field_test: Element = driver.find_element(*code_field)
        #fmt: on
    except NoSuchElementException:
        match config.program.programMode:
            case ProgramMode.Login:
                #fmt: off
                msg: str = "Could not log-in to account. Are your email and password correct? Or, you may have to reset your password. Check the wiki/docs for instructions on this"
                #fmt: on
                logger.critical(msg)
                raise InvalidCredentialError(msg)
            case ProgramMode.Reset:
                #fmt: off
                msg: str = "Could not enter old password. Is your old password correct? Or, more likely, Your password reset token is expired. Refresh it and fill it in (check the instructions)"
                #fmt: on
                logger.critical(msg)
                raise InvalidCredentialError(msg)
    # fmt: off
    match config.program.codeMode:
        case CodeMode_Normal():
            driver.find_element(By.XPATH, value="//*[contains(text(), 'Verify with something else')]").click()
            driver.find_element(By.XPATH, value="//*[contains(text(), 'Use your authenticator app')]").click()
        case CodeMode_Backup():
            driver.find_element(By.XPATH, value="//*[contains(text(), 'Verify with something else')]").click()
            driver.find_element(By.XPATH, value="//*[contains(text(), 'Use a backup code')]").click()
            time.sleep(11)
            driver.find_element(By.XPATH, value="//*[contains(text(), 'use a backup code')]").click()
    # fmt: on

    return driver, config


def try_codes(driver: Driver, config: Config) -> None:
    """Logic to continously enter TOTP/Backup codes"""

    # Set up statistics counters
    sessionStats: SessionStats = SessionStats(0, 0, 0, 0, 0)
    start_time: float = time.time()
    # fmt: off
    sleep_duration_range: list[int] = list(config.program.usualAttemptDelayRange)
    # fmt:on
    secrets

    submit_button: tuple[ByType, str] = (By.XPATH, "//*[@type='submit']")
    code_field: tuple[ByType, str] | None = None
    match config.program.codeMode:
        # fmt: off
        case CodeMode_Backup(): code_field = (By.XPATH, "//*[@label='Enter Discord Backup Code']")
        case CodeMode_Normal(): code_field = (By.XPATH, "//*[@label='Enter Discord Auth Code']")
        # fmt: on
    code_status_elt: tuple[ByType, str] = (By.CLASS_NAME, "_7c9014d93f58a515-error")
    user_homepage: tuple[ByType, str] = (By.CLASS_NAME, "_160d8e55254637e5-app")

    make_new_code: bool = False
    random_code: str = generate_random_code(config.program.codeMode)

    logger.info("Starting a Forcer session")
    logger.debug("\n" + pformat(config.program))
    logger.log("SENSITIVE", "\n" + pformat(config.account))

    # Generate a new code.
    try:
        while True:
            sleep_duration_range = list(config.program.usualAttemptDelayRange)
            # only if I got ratelimited last time.
            if make_new_code:
                random_code = generate_random_code(config.program.codeMode)
                sleep_duration_range = list(config.program.ratelimitedAttemptDelayRange)

            # Use the gen'd backup code only if it's not in the used_backup_codes.txt list. Add the code to the list if I use it.
            # the thing that really sucks here is even if a backup code is valid, by trying it here and logging in, I invalidate it. (backup codes expire on use)
            if isinstance(config.program.codeMode, CodeMode_Backup):
                with open("secret/used_backup_codes.txt", "a+") as f:
                    f.seek(0)
                    used_backup_codes: list[str] = f.readlines()
                    if random_code in used_backup_codes:
                        # fmt: off
                        logger.warning(f"Backup code {random_code} is invalid. Possibly I previously used it, but now it's expired anyway.")
                        # fmt: on
                        continue
                    else:
                        f.write(f"{random_code}\n")

            # Attempt the code

            # backspace the previous code. the max length of a code can be 11 characters (from the backup code)
            driver.find_element(*unwrap(code_field)).send_keys(11 * Keys.BACKSPACE)
            driver.find_element(*unwrap(code_field)).send_keys(random_code)
            time.sleep(secrets.choice(sleep_duration_range))
            driver.find_element(*submit_button).click()
            sessionStats.attemptedCodeCount += 1
            if isinstance(config.program.codeMode, CodeMode_Backup):
                sessionStats.attemptedBackupCodeCount += 1

            # Success check. Break out if I succeed.
            try:
                # CRITICAL PATH
                login_test: Element = driver.find_element(*user_homepage)
                while True:
                    # fmt: off
                    token = driver.execute_script("return window.localStorage.getItem('token')")
                    # fmt: on
                    if token is not None:
                        # fmt: off
                        logger.info(f"FOUND YOUR ACCOUNT'S TOKEN SAVE IT AND DO NOT LOG OUT OF DISCORD)")
                        # fmt: on
                        logger.success(token)
                        with open("secret/token.txt", "a+") as f:
                            f.write(token + "\n")
                        break
                break
            except NoSuchElementException as login_didnt_work:
                try:
                    code_status_msg: str = (driver.find_element(*code_status_elt)).text
                    match (code_status_msg):
                        case "Invalid two-factor code":
                            codeError = CodeError.Invalid
                            # fmt: off
                            logger.warning(f"{code_status_msg}: {random_code}")
                            # fmt: on
                            make_new_code = True
                        # fmt: off
                        case "The resource is being ratelimited." | "Service resource is being rate limited.":
                        # fmt: on
                            codeError = CodeError.Ratelimited
                            logger.warning(code_status_msg)
                            sessionStats.ratelimitCount += 1
                            make_new_code = False
                        case "POST /auth/reset [400]":
                            logger.critical(f"{code_status_msg}: The reset token has expired. Please create a new reset token and update it in account.yml")
                            quit
                        case _:
                            # fmt:off
                            logger.error(f"Encountered unimplemented status message. Tell the developers about this: {code_status_msg}")
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
    # TODO: hold the webdriver here.


def print_session_statistics(SessionStats):
    logger.info("\n" + pformat(SessionStats))

