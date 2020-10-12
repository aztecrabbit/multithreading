from .multithread_request import MultiThreadRequest


class MultiThreadRequestAria2(MultiThreadRequest):
	aria2_rpc = 'http://127.0.0.1:6800/jsonrpc'
	aria2_rpc_secret = ''

	def download(self, url, dirname='', filename=''):
		options = {}

		if dirname:
			options['dir'] = dirname

		if filename:
			options['out'] = filename

		content = {
			'jsonrpc': '2.0',
			'id': 'aztecrabbit:multithreading',
			'method': 'aria2.addUri',
			'params': [f'token:{self.aria2_rpc_secret}', [url], options],
		}

		response = self.request('post', self.aria2_rpc, json=content)

		R1 = self.logger.special_chars['R1']
		CC = self.logger.special_chars['CC']

		data = response.json()

		if data.get('error'):
			self.log('\n'.join([
				f"{R1}Response Error{CC}",
				f"  {data.get('message')}",
				f"",
			]))

			return

		self.download_added(response, url, dirname, filename)

	def download_added(self, response, url, dirname, filename):
		data = response.json()

		G1 = self.logger.special_chars['G1']
		CC = self.logger.special_chars['CC']

		self.log(f"{G1}{data.get('result')}{CC} - {url}")
