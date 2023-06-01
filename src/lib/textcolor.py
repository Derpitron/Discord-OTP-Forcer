def color(string: str, color: str) -> str:
	"""
	Given a string and a color, return the string with the specified color code applied using ANSI escape codes.

	:param string: The string to colorize.
	:type string: str or None

	:param color: The color to use for the string. Must be one of 'red', 'yellow', 'green', 'cyan', 'blue', 'magenta', 'black', 'white', or 'custom'.
	:type color: str or None

	:return: The input string with the specified color applied using ANSI escape codes, or None if either the input string or color is None.
	:rtype: str or None

	:raises ValueError: If the input color is not one of the supported colors.
	"""
	colorCodeMap = {
		    'red' : '\033[31m',
		 'yellow' : '\033[33m',
		  'green' : '\033[32m',
		   'cyan' : '\033[96m',
		   'blue' : '\033[34m',
		'magenta' : '\033[35m',
		  'black' : '\033[30m',
		  'white' : '\033[37m',
		 'custom' : '\033[0;34;47m'
	}
	if color not in colorCodeMap: raise ValueError('Invalid ANSI color code choice.')


	return f"{colorCodeMap[color]}{string}\033[0m"