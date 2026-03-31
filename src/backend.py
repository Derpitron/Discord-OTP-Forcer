# Import dependencies and libraries
import secrets
import time
import sys
import threading
from pprint import pformat
from pathlib import Path
from typing import assert_never

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
from .auth.code_errors import parse_code_error, get_code_status
from .lib.thorium_binary import find_thorium_binary, register_thorium_browser
from .auth.captcha import captcha_detection
from .lib.types import (
    BinaryPath,
    Browser,
    BrowserSession,
    CodeMode,
    CodeMode_Backup,
    CodeMode_Normal,
    CodeStatusFound,
    CodeStatusNotFound,
    Config,
    ProgramMode,
    SessionStats,
    InvalidCode,
    RateLimited,
    ServiceUnavailable,
    TokenExpired,
    UnknownError,
    NetworkOffline,
)


logger.level(name="SENSITIVE", no=15, color="<m><b>")


def _resolve_and_register_binary_location(browser: Browser) -> BinaryPath | None:
    """
    Returns the binary path for browsers not natively recognized by SeleniumBase, or None if not needed.
    """
    if browser is Browser.Thorium:
        register_thorium_browser()
        return find_thorium_binary()
    return None


def bootstrap_browser(config: Config) -> BrowserSession:
    """
    bootstrap_browser is a function that prepares a puppetable browser.
    """

    match config.program.browser:
        case Browser.Chrome | Browser.Brave | Browser.Chromium | Browser.Thorium:
            _HARDEN_WEB_STORAGE_JS = (Path(__file__).parent / "lib/js_scripts" / "HardenWebStorage.js").read_text(encoding="utf-8")

            driver = Driver(
                browser="chrome" if config.program.browser in (Browser.Chromium, Browser.Thorium) else config.program.browser,
                uc=True,
                binary_location=_resolve_and_register_binary_location(config.program.browser),
                use_chromium=config.program.browser is Browser.Chromium,
                headless=config.program.headless,
                locale_code="en-US",
                chromium_arg="--log-level=1" if config.program.headless else None,
            )

            driver.implicitly_wait(0)

            driver.execute_cdp_cmd("Network.enable", {})

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

            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": _HARDEN_WEB_STORAGE_JS},
            )
            logger.debug("Fixed compatibility polyfill")
        case _ as unreachable:
            assert_never(unreachable)

    logger.debug("Started browser")

    return BrowserSession(driver=driver, config=config)


def _get_landing_url(program_mode: ProgramMode, reset_token: str) -> str:
    match program_mode:
        case ProgramMode.Login:
            return "https://discord.com/login"
        case ProgramMode.Reset:
            return f"https://discord.com/reset#token={reset_token}"
        case _ as unreachable:
            assert_never(unreachable)


def _get_code_field(code_mode: CodeMode) -> tuple[ByType, str]:
    match code_mode:
        case CodeMode_Backup():
            return (By.XPATH, "//*[@label='Enter Discord Backup Code']")
        case CodeMode_Normal():
            return (By.XPATH, "//*[@label='Enter Discord Auth Code']")
        case _:
            raise ValueError(f"Unhandled CodeMode: {code_mode}")


def bootstrap_code_page(session: BrowserSession) -> BrowserSession:
    """
    This sets up the code entry page.
    """
    driver: WebDriver = session.driver
    config: Config = session.config
    wait: WebDriverWait[WebDriver] = WebDriverWait(driver, config.program.elementLoadTolerance)
    wait_longer: WebDriverWait[WebDriver] = WebDriverWait(driver, config.program.elementLoadTolerance * 2)

    # Go to the appropriate starting page for the mode
    landing_url: str = _get_landing_url(config.program.programMode, config.account.resetToken)

    driver.get(landing_url)
    logger.debug(f"Gone to {config.program.programMode.name} page")

    # Log-in with credentials
    password_field: tuple[ByType, str] = (By.NAME, "password")
    email_field: tuple[ByType, str] = (By.NAME, "email")
    try:
        match config.program.programMode:
            case ProgramMode.Login:
                wait.until(EC.presence_of_element_located(email_field)).send_keys(config.account.email)
                wait.until(EC.presence_of_element_located(password_field)).send_keys(config.account.password)
            case ProgramMode.Reset:
                wait.until(EC.presence_of_element_located(password_field)).send_keys(config.account.newPassword)
        wait.until(EC.presence_of_element_located(password_field)).send_keys(Keys.RETURN)
    except TimeoutException:
        logger.critical(
            "Could not locate the email or password field on the page. "
            "This may be caused by a low 'elementLoadTolerance' value in your program.yml. "
            "Try increasing it to 5, 7, or even higher if your internet connection is slow."
        )
        logger.critical("If nothing of this works, go to https://github.com/Derpitron/Discord-OTP-Forcer/discussions/ to ask for help.")
        sys.exit(1)

    wait.until(EC.presence_of_element_located(password_field)).send_keys(Keys.RETURN)
    logger.debug("Found and inputted basic login fields")

    captcha_detection(session)

    wait_for_verify_else: WebDriverWait[WebDriver] = WebDriverWait(driver, 7)

    # Select the method
    try:
        wait_for_verify_else.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Verify with something else')]"))).click()

        match config.program.codeMode:
            case CodeMode_Normal():
                wait_longer.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Use your authenticator app')]"))).click()
            case CodeMode_Backup():
                wait_longer.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Use a backup code')]"))).click()
                time.sleep(11)
                wait_longer.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'use a backup code')]"))).click()
    except TimeoutException:
        match config.program.codeMode:
            case CodeMode_Backup():
                logger.critical(
                    "Cannot use backup mode because you likely have no backup codes left. "
                    "If the 'Verify with something else' button did actually appear, "
                    "please go to https://github.com/Derpitron/Discord-OTP-Forcer/issues and create an issue."
                )
                sys.exit(1)
            case CodeMode_Normal():
                pass

    # Check if the code field exists
    try:
        code_field: tuple[ByType, str] = (By.CLASS_NAME, "input__0f084")
        wait.until(EC.presence_of_element_located(code_field))
    except TimeoutException:
        msg: str
        match config.program.programMode:
            case ProgramMode.Login:
                msg = "Could not log-in to account. Are your email and password correct?  You may have to reset your password. Check the wiki/docs for instructions on this"
                logger.critical(msg)
                raise InvalidCredentialError(msg)
            case ProgramMode.Reset:
                msg = "Your password reset token may be expired. Refresh it and fill it in.  Check https://inbydev.codeberg.page/en/user/setup/#how-to-get-your-reset-token"
                logger.critical(msg)
                raise InvalidCredentialError(msg)

    return session


def _code_taking_long() -> None:
    logger.warning("Code taking longer than 15s, you may be on a slow network or ratelimited. Still waiting for status...")


def try_codes(session: BrowserSession) -> None:
    """Logic to continously enter TOTP/Backup codes"""
    driver: WebDriver = session.driver
    config: Config = session.config

    wait_60s: WebDriverWait[WebDriver] = WebDriverWait(driver, 60)
    wait: WebDriverWait[WebDriver] = WebDriverWait(driver, config.program.elementLoadTolerance * 3)

    # Set up statistics counters
    sessionStats: SessionStats = SessionStats(0, 0, 0, 0, 0, 0)
    start_time: float = time.time()

    sleep_duration_range: list[int]

    submit_button: tuple[ByType, str] = (By.XPATH, "//*[@type='submit']")
    code_field: tuple[ByType, str] = _get_code_field(config.program.codeMode)
    code_status_elt: tuple[ByType, str] = (By.CLASS_NAME, "error__7c901")
    user_homepage: tuple[ByType, str] = (By.CLASS_NAME, "app__160d8")

    make_new_code: bool = False
    rate_limited: bool = False
    random_code: str = generate_random_code(config.program.codeMode)

    logger.info("Starting a Forcer session")
    logger.debug("\n" + pformat(config.program))
    logger.log("SENSITIVE", "\n" + pformat(config.account))

    # Generate a new code.
    try:
        while True:
            if not rate_limited:
                sleep_duration_range = list(config.program.usualAttemptDelayRange)
            else:
                sleep_duration_range = list(config.program.ratelimitedAttemptDelayRange)
                rate_limited = False

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
            else:
                random_code = generate_random_code(config.program.codeMode)

            # Attempt the code
            try:
                code_field_element = wait.until(EC.element_to_be_clickable(code_field))
                code_field_element.clear()
                code_field_element.send_keys(random_code)
                time.sleep(secrets.choice(sleep_duration_range))
                submit_button_element = wait.until(EC.element_to_be_clickable(submit_button))
                submit_button_element.click()
                if isinstance(config.program.codeMode, CodeMode_Backup):
                    sessionStats.attemptedBackupCodeCount += 1
                else:
                    sessionStats.attemptedCodeCount += 1
            except TimeoutException as element_isnt_clickable:
                logger.warning(f"Element isn't clickable yet after {config.program.elementLoadTolerance * 3} sec. You may be on a slow network or ratelimited.")
                sessionStats.slowDownCount += 1
                make_new_code = False
                continue

            # Success check. Break out if it succeeded.
            try:
                # CRITICAL PATH
                # We want to know immediately if the homepage is present or not
                login_test: Element = driver.find_element(*user_homepage)
                if login_test:
                    while True:
                        token = driver.execute_script("return window.localStorage.getItem('token');")
                        if token is not None:
                            logger.info("FOUND YOUR ACCOUNT'S TOKEN SAVE IT AND DO NOT LOG OUT OF DISCORD")
                            logger.success(token)
                            with open("secret/token.txt", "a+") as f:
                                f.write(token + "\n")
                            break
                    break
            except NoSuchElementException as login_didnt_work:
                timer_code_taking_long = threading.Timer(15.0, _code_taking_long)
                timer_code_taking_long.start()

                try:
                    match get_code_status(driver, wait_60s, code_status_elt):
                        case CodeStatusFound(message=code_status_msg, used_fallback=used_fallback):
                            if used_fallback:
                                # fmt:off
                                logger.warning(f"Code Status Element '{code_status_elt[1]}' not found, using fallback selectors. Please report this to the developers.")
                                # fmt:on
                            match parse_code_error(code_status_msg, random_code):
                                case InvalidCode(attempted_code=code, raw_message=msg):
                                    logger.warning(f"{msg}: {code}")
                                    make_new_code = True
                                case RateLimited(raw_message=msg):
                                    logger.warning(msg)
                                    sessionStats.ratelimitCount += 1
                                    make_new_code = False
                                    rate_limited = True
                                case TokenExpired(raw_message=msg):
                                    logger.critical(f"{msg}: The reset token has expired. Please create a new reset token and update it in account.yml")
                                    sys.exit()
                                case ServiceUnavailable(raw_message=msg):
                                    logger.warning(f"{msg}: The service is unavailable, Discord is probably under maintenance.")
                                    sessionStats.serviceUnavailableCount += 1
                                    make_new_code = False
                                case NetworkOffline(raw_message=msg):
                                    logger.error("Network disconnection detected. Trying again in 15 seconds...")
                                    time.sleep(15)
                                    make_new_code = False
                                case UnknownError(raw_message=msg):
                                    logger.error(f"Encountered unimplemented status message. Tell the developers about this: {msg}")
                        case CodeStatusNotFound():
                            logger.warning("Status never arrived after 60 sec. Skipping.")
                            make_new_code = True
                            sessionStats.slowDownCount += 1
                finally:
                    timer_code_taking_long.cancel()

    except KeyboardInterrupt:
        logger.critical("Stopping the program on KeyboardInterrupt!")
        pass

    sessionStats.elapsedTimeSeconds = time.time() - start_time
    logger.critical("Program finished!")
    print_session_statistics(sessionStats)


def print_session_statistics(sessionStats: SessionStats) -> None:
    logger.info("\n" + pformat(sessionStats))
