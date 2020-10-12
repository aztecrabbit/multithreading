from .multithread_request import MultiThreadRequest


class MultiThreadRequestAria2(MultiThreadRequest):
	aria2_rpc = 'http://127.0.0.1:6800/jsonrpc'
	aria2_rpc_secret = ''

	def request_rpc(self, data):
		default_data = {
			'jsonrpc': '2.0',
			'id': 'aztecrabbit:multithreading',
		}

		response = super().request('post', self.aria2_rpc, json=self.dict_merge(default_data, data))

		R1 = self.logger.special_chars['R1']
		CC = self.logger.special_chars['CC']

		data = response.json()

		if data.get('error'):
			self.log('\n'.join([
				f"{R1}Response Error{CC}",
				f"  {data['error'].get('message')}",
				f"",
			]))

			self.task_complete()

			raise ValueError

		return response

	def aria2_get_stopped_list(self):
		response = self.request_rpc({
			'method': 'aria2.tellStopped',
			'params': [f'token:{self.aria2_rpc_secret}', 0, 10000],
		})

		data = response.json()

		return data['result']

	def aria2_remove_download_result(self, gid):
		response = self.request_rpc({
			'method': 'aria2.removeDownloadResult',
			'params': [f'token:{self.aria2_rpc_secret}', gid],
		})

		R1 = self.logger.special_chars['R1']

		data = response.json()

		if data['result'] == 'OK':
			self.log(f'{R1}{gid} - Removed')

		else:
			self.log(f'{data}')

	def aria2_clear_completed_list(self):
		for data in self.aria2_get_stopped_list():
			if data['status'] == 'complete':
				self.aria2_remove_download_result(data['gid'])

	def download(self, url, dirname='', filename=''):
		options = {}

		if dirname:
			options['dir'] = dirname

		if filename:
			options['out'] = filename

		response = self.request_rpc({
			'method': 'aria2.addUri',
			'params': [f'token:{self.aria2_rpc_secret}', [url], options],
		})

		self.download_added(response, url, dirname, filename)

	def download_added(self, response, url, dirname, filename):
		data = response.json()

		G1 = self.logger.special_chars['G1']
		CC = self.logger.special_chars['CC']

		self.log(f"{G1}{data.get('result')}{CC} - {url}")
