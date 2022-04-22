from time import sleep
from typing import Union
import secrets

# All the functions in the main file for simplicity's sake
def formatgc(arr: list) -> str:
	"""
	A simple function that turns a array into a string. Made this so i don't repeat myself...

	Args:

		arr: list to be formatted into a string.

	Returns:
		String formating of arr
	"""
	return ''.join(map(str, arr))

def genRndmDigit(num: int = 0, gty: str = "0123456789") -> Union[str, None]:
	"""A function that is used in the generator class to generate random digits. Uses the random module.
	
	Args:

		num: The number of times to generate a random digit. Default value: 0

		gty: String to be used as random characters. Default value: gttypes['genTypeNorm'] =
		"0123456789".

	Returns:
		Formatted version of arr. Or None.
	"""
	arr = []
	if num == 0:
		print("Please enter the number of random digits you want!")
		sleep(5)
		quit()

	for x in range(num):
		arr.append(secrets.choice(gty))
	return formatgc(arr)

def genNormal(num: int): 
	""""""
	ar = []
	for x in range(num):
		ar.append(genRndmDigit(6))
	return formatgc(ar)
