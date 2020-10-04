import os
import sys

from threading import RLock

from loguru import logger

special_chars_code = {
	'D': '30',  # Disabled
	'R': '31',  # Red
	'G': '32',  # Green
	'Y': '33',  # Yellow
	'B': '34',  # Blue
	'P': '35',  # Purple
	'C': '36',  # Cyan
	'W': '37',  # White
}

special_chars = {
	'CC': '\033[0m',  # Clear Color
	'CN': '\033[2K',  # Clear Line
	'CR': '\r',  # To First Line
}


def get_special_char(key=None, char_type=1):
	"""
	char_type
	```
	0 = normal
	1 = bold (light)
	2 = dark
	3 = italic
	4 = underline
	5 = blink
	6 = blink again (?)
	7 = reverse
	```
	"""
	if (special_char := special_chars.get(key)) is not None:
		return special_char

	if key is not None and (char_code := special_chars_code.get(key)) is not None:
		return f'\033[{char_code};{char_type}m'

	return f'\033[{char_type}m'


for code in special_chars_code:
	for i in range(1, 9 + 1):
		special_chars[f'{code}{i}'] = get_special_char(code, i)


class Logger:
	def __init__(self, level='DEBUG'):
		self._lock = RLock()

		self.special_chars = special_chars

		self.logger = logger
		self.logger.remove()
		self.logger.configure(
			extra={
				'CC': self.special_chars['CC'],
				'CN': self.special_chars['CN'],
				'CR': self.special_chars['CR'],
			}
		)
		self.logger.add(sys.stderr, colorize=True, format='{extra[CR]}{extra[CN]}{message}{extra[CC]}', level=level)

	def replace(self, message):
		columns, _ = os.get_terminal_size()

		if len(message) > columns:
			message = message[:columns - 3] + '...'

		CN = self.special_chars['CN']
		CC = self.special_chars['CC']
		CR = self.special_chars['CR']

		with self._lock:
			sys.stdout.write(f'{CN}{message}{CC}{CR}')
			sys.stdout.flush()

	def log(self, message, level='INFO'):
		self.logger.log(level, message)
