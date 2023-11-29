import os
from yaml import safe_load as load
import sys

import stackprinter
stackprinter.set_excepthook(style='darkbg')

from loguru import logger

from src.lib.textcolor import color
from src.backend import bootstrap_browser, bootstrap_login_page
from src.lib.exceptions import UserCausedHalt

def load_configuration(configuration_file_path='user/cfg.yml') -> dict:
	"""
	Loads a YAML configuration file and returns a dictionary of the configuration.

	:param configuration_file_path: A string representing the path to the YAML configuration file to be loaded. Default is 'user/cfg.yml'.
	:type configuration_file_path: str
	:return: A dictionary representing the loaded YAML configuration file.
	:rtype: dict
	"""
	with open(configuration_file_path, "r") as configuration_file: 
		logger.debug(f'Loaded configuration file located at {os.path.realpath(configuration_file.name)}')
		return load(configuration_file)

def userFacing(configuration: dict):
	"""
	Takes a configuration dictionary `configuration` as input and prompts the user to select a program mode and code type(s) they want to generate. Then, it checks whether the inputted program mode and code mode are valid or not. If the inputted modes are valid, it starts the simulated browser and runs it in an infinite loop.

	:param configuration: A dictionary that contains the configuration for the function.
	:type configuration: dict

	:raises ValueError: If the inputted program mode or code mode is invalid.

	:return: None
	:rtype: None
	"""
	#To-do: move the below stuff to documentation.
	# Ask the user what program mode they want to use
	#programModePromptText = (
	#	f"Enter the program mode which you want to generate codes for."
	#	f"\n[{color('    Login     ', 'green')}] -   login"
	#	f"\n[{color('Password Reset', 'green')}] -   reset\n:"
	#)
	# Ask the user what code type(s) they want to use
	#codeModePromptText = (
	#	f"What kind(s) of codes would you like to generate?"
	#	f"\n[{color('normal','green')}] - {color('6','green')} Digit Normal Code"
	#	f"\n[{color('backup','green')}] - {color('8','green')} Digit Backup Code"
	#	f"\n[{color('  both','cyan') }] - Both {color('6','green')} Digit Normal Codes and {color('8','green')} Digit Backup Codes\n:"
	#)

	# Check whether the inputted program mode is valid
	validProgramModes: set = {
		'login',
		'reset'
	}
	if configuration['programMode'].lower() not in validProgramModes: raise ValueError("Invalid program mode inputted!")

	# Check whether the inputted code mode is valid
	validCodeModes: set = {
		'normal',
		'backup',
		'backup_let',
		'both'
	}
	if configuration['codeMode'].lower() not in validCodeModes: raise ValueError('Invalid code-generation mode inputted!')

	# Start the simulated browser, and run it in an infinite loop.
	while True:
		driver = bootstrap_browser(configuration)
		bootstrap_login_page(driver, configuration)

if __name__ == '__main__':
	try:
		userFacing(load_configuration())
	except UserCausedHalt:
		# Exit procedure taken from: https://stackoverflow.com/a/21144662
		logger.info('User halted the program!')
		sys.exit(130)
