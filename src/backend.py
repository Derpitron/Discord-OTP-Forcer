# Import dependencies and libraries
import time
import secrets
from src.lib.codegen import generate_random_code
from src.lib.textcolor import color

# Import Selenium libraries and dependencies
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

def bootstrap_browser(
	configuration: dict,
) -> webdriver.chrome.webdriver.WebDriver:
	"""
	bootstrap_browser is a function that initializes and returns a WebDriver object of the Chrome browser. 
	:param configuration: a dictionary object which holds the program mode as key-value pairs. 
	:type configuration: dict
	:return: a WebDriver object of the Chrome browser.
	:rtype: webdriver.chrome.webdriver.WebDriver
	"""
	# Set Chromium options.
	options = Options()
	options.add_experimental_option('excludeSwitches', ['enable-logging'])
	options.add_experimental_option(         'detach', True)
	options.add_argument("--lang=en-US") # Force the browser window into English so we can find the code XPATH

	# If you want to run the program without the browser opening then remove the # from the options below 
	#options.add_argument('--headless')
	#options.add_argument('--log-level=1')

	# Get and initialize the most up-to-date Chromium web driver
	driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
	#Blocking various Discord analytics/monitoring URLS so they don't phone home
	driver.execute_cdp_cmd('Network.setBlockedURLs', {
		'urls': [
			'a.nel.cloudflare.com/report', 
			'https://discord.com/api/v10/science',
			'https://discord.com/api/v9/science',
			'sentry.io'
		]
	})
	# Enable the network connectivity of the browser
	driver.execute_cdp_cmd('Network.enable', {})

	# Go to the appropriate starting page for the mode
	match configuration['programMode'].lower():
		case 'login':
			# Go to the discord login page
			driver.get('https://www.discord.com/login')
		case 'reset':
			# Go to the discord page
			driver.get('https://discord.com/reset#token=' + configuration['resetToken'])
	# Wait 1 second before typing the email and password
	driver.implicitly_wait(1)
	return driver

def bootstrap_login_page(
	driver: webdriver.chrome.webdriver.WebDriver,
	configuration: dict,
):
	"""
	Login Bootstrap is a function that takes in two parameters:
	1. driver: A web driver object of Chrome
	2. configuration: A dictionary of configuration keys and values
	The function locates the login input fields based on the `configuration` parameter's `programMode`. If `programMode` is 'login',
	the email and password fields are located, and the values of the fields are filled using `configuration`. If `programMode` is 'reset',
	only the password field is located and filled in with the `newPassword` key from `configuration`. The function then attempts to find
	a TOTP login field, and if found, calls the `codeEntry()` function to enter the authentication code. If a `NoSuchElementException`
	is caught while trying to find the TOTP login field, the function continues to run, assuming that the hCaptcha has been completed.
	"""
	# Find the login input fields
	login_fields = {
		'password': driver.find_element(by=By.NAME, value='password')
	}
	match configuration['programMode'].lower():
		case 'login':
			login_fields['email'] = driver.find_element(by=By.NAME, value='email')
			# Enter the email and password. 
			#Uses jugaad syntax to get and fill in the email and password user details in the appropriate field.
			for i in login_fields:
				login_fields[i].send_keys(configuration[i])
		case 'reset':
			# Enter the new password
			login_fields['password'].send_keys(configuration['newPassword'])
	
	# Click Enter/Return to submit the user details
	login_fields['password'].send_keys(Keys.RETURN)

	# Start code entering
	#loginTOTP = otp input field. TOTP stands for Timed One Time Password
	# Constantly run the script.
	while (True):
		# Attempt to find the TOTP login field
		try:
			
			match configuration['codeMode']:
				case 'normal':
					login_fields['TOTP'] = driver.find_element(by=By.XPATH, value="//input[@placeholder='6-digit authentication code']")

				case 'backup':
					driver.find_element(By.XPATH, "//*[contains(text(), 'Verify with something else')]").click()
					WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Use a backup code')]"))) # Waits until element is clickable
					driver.find_element(By.XPATH, "//*[contains(text(), 'Use a backup code')]").click()
					driver.implicitly_wait(1)
					login_fields['TOTP'] = driver.find_element(by=By.XPATH, value="//input[@placeholder='8-digit backup code']")
					driver.implicitly_wait(1)
					
			# Auto-triggers the password reset flow
			if ('Please reset your password to log in.' in driver.page_source):
				configuration['programMode'] = 'reset'
				code_entry(driver, login_fields, configuration)
			code_entry(driver, login_fields, configuration)
		except NoSuchElementException: # This try-except block constantly checks whether the hCaptcha has been completed, and if so, it will continue to the next phase.
			pass
		except NoSuchWindowException: # If the browser window is closed stop looking for TOTP login field 
			break

def code_entry(
	     driver: webdriver.chrome.webdriver.WebDriver,
	login_fields: dict,
	     configuration: dict
):
	try:
		"""
		Enter OTP codes continuously until successful login, using the provided webdriver, 
		loginFields dictionary, and configuration dictionary. Returns nothing. 

		:param driver: A webdriver object.
		:type driver: webdriver.chrome.webdriver.WebDriver
		:param loginFields: A dictionary of login fields.
		:type loginFields: dict
		:param configuration: A dictionary of configuration values.
		:type configuration: dict
		"""
		# Set up statistics counters
		session_statistics = {
			'attemptedCodeCount':   0,
			    'ratelimitCount':   0,
			       'elapsedTime': 0.0,
			       'programMode':  '',
			          'codeMode':  '',
		}

		#Logic to continuously enter OTP codes
		time.sleep(0.3)
		start_time = time.time()
		sleep_duration_seconds = 0
		while (True):
			# Inform user TOTP field was found
			if session_statistics['attemptedCodeCount'] == 0:
				for i in configuration:
					session_statistics[i] = configuration[i]
					print(f"{color(i, 'green')}: {session_statistics[i]}")
				print(f"TOTP login field: {color('Found','green')}")
				print(f"Forcer: {color('Starting','green')}")
				print(f"Program Mode: {color(configuration['programMode'].lower(), 'green')}")
				print(f"Code Mode: {color(configuration['codeMode'].lower(), 'green')}")

			# Generate a new code and enter it into the TOTP field
			totp_code = generate_random_code(configuration['codeMode'].lower())

			# Use the 8-digit code only if it's not in the used_backup_codes.txt list
			if len(totp_code) == 8:
				with open('user/used_backup_codes.txt', 'a+') as f:
					f.seek(0)
					used_backup_codes = f.read() 
					if totp_code in used_backup_codes:
						continue
					else:
						f.write(f"{totp_code}\n")

			# Send the code
			login_fields['TOTP'].send_keys(totp_code)
			login_fields['TOTP'].send_keys(Keys.RETURN)
			session_statistics['attemptedCodeCount'] += 1
			driver.implicitly_wait(0.3) # Wait for page to update so we can detect changes such as rate limited.   

			while ('ratelimited' in driver.page_source):
				sleep_duration_seconds = secrets.choice(range(5, 7))
				session_statistics['ratelimitCount'] += 1
				print(f"Code: {color(totp_code, 'blue')} was {color('Ratelimited', 'yellow')} will retry in {color(sleep_duration_seconds, 'blue')}")
				time.sleep(sleep_duration_seconds)
				login_fields['TOTP'].send_keys(Keys.RETURN)
				driver.implicitly_wait(0.3)

			if ('Token has expired' in driver.page_source): 
				#Print this out as well as some statistics, and prompt the user to retry.
				session_statistics['elapsedTime'] = time.time() - start_time
				print_session_statistics('invalid_password_reset_token', session_statistics)
				# Close the browser and stop the script.
				driver.close()
				break

			# This means that Discord has expired this login session, we must restart the process.
			elif ('Invalid token' in driver.page_source):
				#  Testing for a new localised message.
				#  Print this out as well as some statistics, and prompt the user to retry.
				session_statistics['elapsedTime'] = time.time() - start_time
				print_session_statistics('invalid_session_ticket', session_statistics)
				# Close the browser and stop the script.
				driver.close()
				break

			# The entered TOTP code is invalid. Wait a few seconds, then try again.
			else:
				sleep_duration_seconds = secrets.choice(range(2, 6))
			#Testing if the main app UI renders.
			try:
				# Wait 1 second, then check if the Discord App's HTML loaded by it's CSS class name. If loaded, then output it to the user.
				loginTest = driver.find_element(by=By.CLASS_NAME, value='app_b1f720') # Will need a better way to find.
				driver.implicitly_wait(1)
				print(color(f"Code {totp_code} worked!", 'green'))
				exit
			except NoSuchElementException:
				# This means that the login was unsuccessful so let's inform the user and wait.
				print(f"Code: {color(totp_code, 'blue')} did not work, delay: {color(sleep_duration_seconds, 'blue')}")
				time.sleep(sleep_duration_seconds)
				# Backspace the previously entered TOTP code.
				for i in range(len(totp_code)):
					login_fields['TOTP'].send_keys(Keys.BACKSPACE)
	except NoSuchWindowException:
		session_statistics['elapsedTime'] = time.time() - start_time
		print_session_statistics('invalid_session_ticket', session_statistics)

def print_session_statistics(
	halt_reason: str,
	session_statistics: dict
):
	"""
	Displays statistics and the reason for program halt.

	:param halt_reason: A string representing the reason why the program halted.
	:type halt_reason: str
	:param session_statistics: A dictionary containing statistical data.
	:type session_statistics: dict
	:return: This function does not return anything.
	"""
	halt_reasons = {
			 'invalid_session_ticket': 'Invalid session ticket',
		'invalid_password_reset_token': 'Invalid password reset token',
			'password_reset_required': 
									f"We need to reset the password!\n"\
									f"Running {color('reset program mode', 'green')}!\n"\
									f"{color('(This feature will only work if the resetToken is filled in the .env file.)', 'yellow')}"
	}
	print(color(f"Halt reason:            {         halt_reasons[halt_reason]}", 'red' ))
	print(color(f"Program mode:           {       session_statistics['programMode']}", 'blue'))
	print(color(f"Code mode:              {          session_statistics['codeMode']}", 'blue'))
	print(color(f"Number of tried codes:  {session_statistics['attemptedCodeCount']}", 'blue'))
	print(color(f"Time elapsed for codes: {       session_statistics['elapsedTime']}", 'blue'))
	print(color(f"Number of ratelimits    {    session_statistics['ratelimitCount']}", 'blue'))
