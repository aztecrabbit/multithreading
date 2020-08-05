import sys

from threading import RLock

from loguru import logger


class Logger:
	def __init__(self, level='DEBUG'):
		self._lock = RLock()

		self.special_chars = {
			'R1': '\033[31;1m',
			'R2': '\033[31;2m',
			'G1': '\033[32;1m',
			'G2': '\033[32;2m',
			'Y1': '\033[33;1m',
			'Y2': '\033[33;2m',
			'B1': '\033[34;1m',
			'B2': '\033[34;2m',
			'P1': '\033[35;1m',
			'P2': '\033[35;2m',
			'C1': '\033[36;1m',
			'C2': '\033[36;2m',
			'CC': '\033[0m',
			'CN': '\033[2K',
			'CR': '\r',
		}

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
		with self._lock:
			sys.stdout.write(f"{self.special_chars['CN']}{message}{self.special_chars['CC']}{self.special_chars['CR']}")
			sys.stdout.flush()

	def log(self, message, level='INFO'):
		self.logger.log(level, message)
