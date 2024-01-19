import re
import os
import sys

from loguru import logger

def obfuscate_message(message: str):
	"""Obfuscate sensitive information."""
	obfuscation_patterns = [
		(r"email: .*", "email: ******"),
		(r"password: .*", "password: ******"),
		(r"newPassword: .*", "newPassword: ******"),
		(r"resetToken: .*", "resetToken: ******"),
		(r"authToken: .*", "authToken: ******"),
		(r"located at .*", "located at ******"),
		(r"#token=.*", "#token=******"),
		# Add more obfuscation patterns as needed
	]
	for pattern, replacement in obfuscation_patterns:
		message = re.sub(pattern, replacement, message)

	return message

def formatter(record):
	record["extra"]["obfuscated_message"] = record["message"]
	return "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>[{level}]</level> - <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{extra[obfuscated_message]}</level>\n{exception}"

def formatter_sensitive(record):
	record["extra"]["obfuscated_message"] = obfuscate_message(record["message"])
	return "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green> <level>[{level}]</level> - <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{extra[obfuscated_message]}</level>\n{exception}"