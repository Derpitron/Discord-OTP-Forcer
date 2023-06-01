from string import digits, ascii_lowercase as letters
from secrets import choice as randchoice

# All the functions in the main file for simplicity's sake
def list2str(list: list) -> str:
	"""
	A simple function that turns a list into a string. Made this so i don't repeat myself...

	Args:

		list: list to be formatted into a string.

	Returns:
		All list elements concatenated to one string
	"""
	return ''.join(map(str, list))

def genRandomChar(charSet: str) -> str:
	"""
	Generate a random character from the given character set.

	:param charSet: a string containing the characters to choose from
	:type charSet: str
	:return: a single randomly selected character from the character set
	:rtype: str
	"""
	yield randchoice(charSet)

def genRandomCode(mode: str) -> str:
	"""
	Generate a code based on the given mode parameter.

	:param mode: A string representing the mode of code generation. It can be either 'normal' or 'backup'.
	:type mode: str or None

	:return: A string representing the generated code.
	:rtype: str or None

	"""
	# The nitty-gritty settings for code generation based on mode.
	match mode:
		case 'normal':
			# Generates a 6-digit numeric 'normal' code
			return list2str( list( next(genRandomChar(           digits )) for _ in range(6)))
		case 'backup':
			# Generates an 8-digit alphanumeric 'backup' code
			return list2str( list( next(genRandomChar( letters + digits )) for _ in range(8)))
		case 'both':
			# Generates a code with a random possibility of being 'normal' or 'backup' type
			# We pack the two genRandomCode options into a list, pass as a single parameter to randchoice
			# Source: https://stackoverflow.com/a/70510607/19195633
			return randchoice( [genRandomCode('normal'), genRandomCode('backup')] )
