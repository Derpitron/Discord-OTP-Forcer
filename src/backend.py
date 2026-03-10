# Import dependencies and libraries
import secrets
import time
import sys
from pprint import pformat
from typing import Tuple

from loguru import logger

from seleniumbase import Driver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement as Element
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

# TODO: Refactor this into an Enum class in the future for type safety
RATE_LIMIT_ERRORS: tuple[str, ...] = (
    "The resource is being ratelimited.",
    "Service resource is being rate-limited.",
    "Service resource is being rate limited.",
    "You are being rate limited.",
    "The resource is being rate limited.",
)

logger.level(name="SENSITIVE", no=15, color="<m><b>")


def bootstrap_browser(config: Config) -> Tuple[WebDriver, Config]:
    """
    bootstrap_browser is a function that prepares a puppetable browser.
    """

    driver: WebDriver | None = None

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

            arguments = None
            if config.program.headless:
                arguments = "--log-level=1"

            # fmt: off
            driver = Driver(
                browser="chrome",
                # undetected-chromedriver maintained from SeleniumBase.
                uc=True,
                headless=config.program.headless,
                # Sets the Language Locale Code for the web browser.
                locale_code="en-US",
                chromium_arg=arguments,
            )

            uc_driver = unwrap(driver)

            uc_driver.execute_cdp_cmd("Network.enable", {})

            # fmt: on
            uc_driver.execute_cdp_cmd(
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

            uc_driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": HARDEN_WEB_STORAGE_JS},
            )
            logger.debug("Fixed compatibility polyfill")
    logger.debug("Started browser")

    return uc_driver, config


def bootstrap_code_page(
    driver: WebDriver,
    config: Config,
) -> Tuple[WebDriver, Config]:
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

    # fmt: off
    while driver.find_elements(*captcha_box): # Check if the captcha exists
        logger.info("A captcha detected. Please complete the captcha for the program to continue.")
        driver.implicitly_wait(config.program.elementLoadTolerance) #Waits for the program to detect that the captcha isn't there.
    # fmt: on

    logger.debug("No captcha detected or has been completed. Moving on to the rest of the script.")

    wait: WebDriverWait[WebDriver] = WebDriverWait(driver, 15)
    # fmt: off
    wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Verify with something else')]"))).click()

    # Select the method
    match config.program.codeMode:
        case CodeMode_Normal():
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Use your authenticator app')]"))).click()
        case CodeMode_Backup():
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Use a backup code')]"))).click()
            time.sleep(11)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'use a backup code')]"))).click()
    # fmt: on

    # Check if the code filed exists
    try:
        # fmt: off
        code_field: tuple[ByType, str] = (By.CLASS_NAME, "input__0f084")
        code_field_test: Element = driver.find_element(*code_field)
        # fmt: on
    except NoSuchElementException:
        msg: str
        match config.program.programMode:
            case ProgramMode.Login:
                # fmt: off
                msg = "Could not log-in to account. Are your email and password correct? Or, you may have to reset your password. Check the wiki/docs for instructions on this"
                # fmt: on
                logger.critical(msg)
                raise InvalidCredentialError(msg)
            case ProgramMode.Reset:
                # fmt: off
                msg = "Could not enter old password. Is your old password correct? Or, more likely, Your password reset token is expired. Refresh it and fill it in (check the instructions)"
                # fmt: on
                logger.critical(msg)
                raise InvalidCredentialError(msg)

    return driver, config


def try_codes(driver: WebDriver, config: Config) -> None:
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
    # fmt: off
    match config.program.codeMode:
        case CodeMode_Backup(): code_field = (By.XPATH, "//*[@label='Enter Discord Backup Code']")
        case CodeMode_Normal(): code_field = (By.XPATH, "//*[@label='Enter Discord Auth Code']")
    # fmt: on
    code_status_elt: tuple[ByType, str] = (By.CLASS_NAME, "error__7c901")
    user_homepage: tuple[ByType, str] = (By.CLASS_NAME, "app__160d8")

    make_new_code: bool = False
    random_code: str = generate_random_code(config.program.codeMode)

    logger.info("Starting a Forcer session")
    logger.debug("\n" + pformat(config.program))
    logger.log("SENSITIVE", "\n" + pformat(config.account))

    wait: WebDriverWait[WebDriver] = WebDriverWait(driver, 15)

    # Generate a new code.
    try:
        while True:
            sleep_duration_range = list(config.program.usualAttemptDelayRange)
            # only if I didn't get ratelimited last time.
            if make_new_code:
                random_code = generate_random_code(config.program.codeMode)
                sleep_duration_range = list(config.program.ratelimitedAttemptDelayRange)

            # Use the gen'd backup code only if it's not in the used_backup_codes.txt list. Add the code to the list if I use it.
            # the thing that really sucks here is even if a backup code is valid, by trying it here and logging in, I invalidate it. (backup codes expire on use)
            if isinstance(config.program.codeMode, CodeMode_Backup):
                with open("secret/used_backup_codes.txt", "a+") as f:
                    f.seek(0)
                    used_backup_codes: list[str] = f.read().splitlines()
                    if random_code in used_backup_codes:
                        if make_new_code:
                            logger.warning(f"Backup code {random_code} is invalid. Possibly I previously used it, but now it's expired anyway.")
                            random_code = generate_random_code(config.program.codeMode)
                        else:  # If rate limiting occurs, do not generate a new code
                            logger.warning(f"Backup code {random_code} wasn't tested. Will test once the ratelimiting is over.")
                    else:
                        f.write(f"{random_code}\n")

            # Attempt the code
            try:
                code_field_element = wait.until(EC.element_to_be_clickable(unwrap(code_field)))
                code_field_element.clear()
                code_field_element.send_keys(random_code)
                time.sleep(secrets.choice(sleep_duration_range))
                submit_button_element = wait.until(EC.element_to_be_clickable(unwrap(submit_button)))
                submit_button_element.click()
                sessionStats.attemptedCodeCount += 1
                if isinstance(config.program.codeMode, CodeMode_Backup):
                    sessionStats.attemptedBackupCodeCount += 1
            except TimeoutException as element_isnt_clickable:
                logger.warning("Element isn't clickable yet after 15 sec. You may be on a slow network or ratelimited.")
                sessionStats.slowDownCount += 1
                make_new_code = False
                continue

            # Success check. Break out if I succeed.
            try:
                # CRITICAL PATH
                login_test: Element = driver.find_element(*user_homepage)
                if login_test:
                    while True:
                        # fmt: off
                        token = driver.execute_script("return window.localStorage.getItem('token');")
                        # fmt: on
                        if token is not None:
                            # fmt: off
                            logger.info("FOUND YOUR ACCOUNT'S TOKEN SAVE IT AND DO NOT LOG OUT OF DISCORD")
                            # fmt: on
                            logger.success(token)
                            with open("secret/token.txt", "a+") as f:
                                f.write(token + "\n")
                            break
                    break
            except NoSuchElementException as login_didnt_work:
                try:
                    # fmt:off
                    code_status_fallback_selectors = [
                        (By.XPATH, "//form//div[text()='Invalid two-factor code']"),
                        (By.XPATH, "//form//div[text()='The resource is being ratelimited.']"),
                        (By.XPATH, "//form//div[text()='Service resource is being rate-limited.']"),
                        (By.XPATH, "//form//div[text()='Service resource is being rate limited.']"),
                        (By.XPATH, "//form//div[text()='The resource is being rate limited.']"),
                    ]
                    # fmt:on

                    code_status_msg: str | None = None

                    # Try first with the Code Status Element Class, if not, fallback to the text.
                    try:
                        code_status_msg = driver.find_element(*code_status_elt).text
                    except NoSuchElementException:
                        driver.implicitly_wait(0)

                        for selector in code_status_fallback_selectors:
                            try:
                                code_status_msg = driver.find_element(*selector).text
                                # fmt:off
                                logger.warning(f"Code Status Element '{code_status_elt[1]}' not found, using fallback selectors. Please report this to the developers.")
                                # fmt:on
                                break
                            except NoSuchElementException:
                                continue

                        driver.implicitly_wait(config.program.elementLoadTolerance)

                    if code_status_msg is None:
                        raise NoSuchElementException()

                    match code_status_msg:
                        case "Invalid two-factor code":
                            codeError = CodeError.Invalid
                            # fmt: off
                            logger.warning(f"{code_status_msg}: {random_code}")
                            # fmt: on
                            make_new_code = True
                        case msg if msg in RATE_LIMIT_ERRORS:
                            codeError = CodeError.Ratelimited
                            logger.warning(code_status_msg)
                            sessionStats.ratelimitCount += 1
                            make_new_code = False
                        case "POST /auth/reset [400]":
                            logger.critical(f"{code_status_msg}: The reset token has expired. Please create a new reset token and update it in account.yml")
                            sys.exit()
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


def print_session_statistics(SessionStats):
    logger.info("\n" + pformat(SessionStats))
