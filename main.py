from yaml import safe_load as load
import sys

from src.lib.textcolor import color
from src.backend import browserBootstrap, loginBootstrap

def loadcfg(cfgfilename='user/cfg.yml') -> dict:
	with open(cfgfilename, "r") as cfgfile:
		return load(cfgfile)

def userFacing(cfg: dict):
	"""
	This is the business-logic code.\n
	Asks the user for the program mode and code type(s) they want to generate. 
	Validates the inputted program mode and code mode. 
	Starts the simulated browser and runs it in an infinite loop.
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
	if cfg['programMode'] not in validProgramModes: raise ValueError("Invalid program mode inputted!")

	# Check whether the inputted code mode is valid
	validCodeModes: set = {
		'normal',
		'backup',
		'both'
	}
	if cfg['codeMode'] not in validCodeModes: raise ValueError('Invalid code-generation mode inputted!')

	# Start the simulated browser, and run it in an infinite loop.
	while True:
		driver = browserBootstrap(cfg)
		loginBootstrap(driver, cfg)

if __name__ == '__main__':
	try:
		userFacing(loadcfg())
	except KeyboardInterrupt:
		# Exit procedure taken from: https://stackoverflow.com/a/21144662
		print(f"\n{color('Halting Program on KeyboardInterrupt...!', 'red')}")
		sys.exit(130)