import time

import requests

from .multithread import MultiThread


class MultiThreadRequest(MultiThread):
	requests = requests

	def request_connection_error(self):
		time.sleep(1)
		return 0

	def request_timeout(self):
		time.sleep(5)
		return 1

	def request(self, method, url, **kwargs):
		method = method.upper()

		self.log_replace(method, url)

		kwargs['timeout'] = kwargs.get('timeout', 5)

		retry = int(kwargs.pop('retry', 5))

		while retry > 0:
			try:
				return self.requests.request(method, url, **kwargs)

			except requests.exceptions.ConnectionError:
				self.log_replace(method, url, 'connection error')
				retry_decrease = self.request_connection_error()
				retry -= retry_decrease or 0

			except (requests.exceptions.ReadTimeout, requests.exceptions.Timeout):
				self.log_replace(method, url, 'timeout')
				retry_decrease = self.request_timeout()
				retry -= retry_decrease or 1

		return None
