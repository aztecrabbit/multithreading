from hashlib import sha1
from uuid import uuid4

import requests

from .multithread import MultiThread


class MultiThreadRequest(MultiThread):
	requests = requests

	def request_connection_error(self, request_id, method, url, **_):
		for _ in self.sleep(1):
			self.log_replace(request_id, method, url, 'connection error')
		return 0

	def request_read_timeout(self, request_id, method, url, **_):
		for remains in self.sleep(10):
			self.log_replace(request_id, method, url, 'read timeout', remains)
		return 0

	def request_timeout(self, request_id, method, url, **_):
		for remains in self.sleep(5):
			self.log_replace(request_id, method, url, 'timeout', remains)
		return 0

	def request(self, method, url, **kwargs):
		request_id = sha1(str(uuid4()).encode()).hexdigest()[:8]
		method = method.upper()

		kwargs['timeout'] = kwargs.get('timeout', 5)

		retry = int(kwargs.pop('retry', 5))

		while retry > 0:
			self.log_replace(request_id, method, url)

			try:
				return self.requests.request(method, url, **kwargs)

			except requests.exceptions.ConnectionError:
				retry_decrease = self.request_connection_error(request_id, method, url, **kwargs)
				retry -= retry_decrease or 0

			except requests.exceptions.ReadTimeout:
				retry_decrease = self.request_read_timeout(request_id, method, url, **kwargs)
				retry -= retry_decrease or 0

			except requests.exceptions.Timeout:
				retry_decrease = self.request_timeout(request_id, method, url, **kwargs)
				retry -= retry_decrease or 0

		return None
