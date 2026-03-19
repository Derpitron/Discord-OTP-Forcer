import time

from loguru import logger

from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.remote.webdriver import WebDriver


def captcha_detection(
    driver: WebDriver,
) -> None:
    captcha_box: tuple[ByType, str] = (By.CLASS_NAME, "container__8a031")
    captcha_detected: bool = bool(driver.find_elements(*captcha_box))

    if not captcha_detected:
        logger.debug("No captcha detected. Moving on to the rest of the script.")
        return

    while True:  # Check if the captcha_box still exists
        logger.info("A captcha detected. Please complete the captcha for the program to continue.")
        time.sleep(1)
        if not driver.find_elements(*captcha_box):  # Waits for the program to detect that the captcha isn't there.
            break

    logger.debug("Captcha has been completed. Moving on to the rest of the script.")
