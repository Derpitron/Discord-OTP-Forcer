def toColor(string, color):
	color_code = {
		'blue': '\033[34m',
		'cyan': '\033[96m',
		'yellow': '\033[33m',
		'green': '\033[32m',
		'red': '\033[31m',
		'black': '\033[30m',
		'magenta': '\033[35m',
		'white': '\033[37m',
		'custom': '\033[0;34;47m'
	}
	return color_code[color] + str(string) + '\033[0m'