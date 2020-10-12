import datetime
import os
import sys
import time

from queue import Queue
from threading import Thread, RLock

from .logger import Logger


class MultiThread:
	logger = Logger(level='DEBUG')

	file_name_success_list = ''
	file_name_failed_list = ''

	def __init__(self, task_list=None, threads=None):
		self._lock = RLock()
		self._loop = True
		self._queue_task_list = Queue()

		self._task_list = task_list or []
		self._task_list_total = 0
		self._task_list_scanned_total = 0
		self._task_list_success = []
		self._task_list_failed = []

		self._threads = threads or 16

	"""
	Core
	"""

	def set_threads(self, threads):
		self._threads = threads or self._threads

	def add_task(self, data):
		self._queue_task_list.put(data)
		self._task_list_total += 1

	def get_task_list(self):
		return self._task_list

	def start(self):
		try:
			for task in self.get_task_list():
				self.add_task(task)
			self.init()
			self.start_threads()
			self.join()
		except KeyboardInterrupt:
			self.task_complete()
			self.keyboard_interrupt()
		finally:
			self.complete()

	def start_threads(self):
		for _ in range(min(self._threads, self._queue_task_list.qsize()) or self._threads):
			Thread(target=self.thread, daemon=True).start()

	def thread(self):
		while self.loop():
			task = self._queue_task_list.get()
			if not self.loop():
				break
			self.task(task)
			self._task_list_scanned_total += 1
			self._queue_task_list.task_done()

	def init(self):
		pass

	def task(self, *_):
		pass

	def join(self):
		self._queue_task_list.join()
		self.task_complete()

	def complete(self):
		data_time = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

		if not self.file_name_success_list:
			self.file_name_success_list = 'success'

		if not self.file_name_failed_list:
			self.file_name_failed_list = 'failed'

		self.save_list_to_file(f'storage/{self.file_name_success_list}_{data_time}.lst', self.success_list())
		self.save_list_to_file(f'storage/{self.file_name_failed_list}_{data_time}.lst', self.failed_list())

	"""
	Extra
	"""

	def lock(self):
		return self._lock

	def lock_queue(self):
		return self._queue_task_list.mutex

	def loop(self):
		return self._loop

	def success_list(self):
		return self._task_list_success

	def failed_list(self):
		return self._task_list_failed

	def task_success(self, data):
		self._task_list_success.append(data)

	def task_failed(self, data):
		self._task_list_failed.append(data)

	def task_complete(self):
		self._loop = False

		with self.lock_queue():
			self._queue_task_list.unfinished_tasks -= len(self._queue_task_list.queue)
			self._queue_task_list.queue.clear()

	def keyboard_interrupt(self):
		CC = self.logger.special_chars['CC']
		R1 = self.logger.special_chars['R1']

		with self.lock_queue():
			self.log(
				'\n'.join([
					f'{R1}Keyboard Interrupt{CC}',
					'  Clearing all threads and queue',
					'  Please wait...',
					'',
				])
			)

	"""
	Utility
	"""

	def log(self, *args, **kwargs):
		self.logger.log(*args, **kwargs)

	def log_replace(self, *messages):
		default_messages = [
			' ',
			f'{self.percentage_scanned():.3f}%',
			f'{self._task_list_scanned_total} of {self._task_list_total}',
			f'{len(self.success_list())}',
		]

		messages = [str(x) for x in messages if x is not None and str(x)]

		self.logger.replace(' - '.join(default_messages + messages))

	def real_path(self, name=''):
		return os.path.dirname(os.path.abspath(sys.argv[0])) + (f'/{name}' if name else '')

	def filter_list(self, data):
		filtered_data = []

		for item in data:
			item = str(item).strip()
			if item.startswith('#'):
				continue
			filtered_data.append(item)

		return list(set(filtered_data))

	def dict_merge(self, default_data, data):
		if not isinstance(default_data, dict):
			default_data = {}

		if not isinstance(data, dict):
			data = {}

		return {**default_data, **data}

	def sleep(self, seconds):
		while seconds > 0:
			yield seconds
			time.sleep(1)
			seconds -= 1

	def percentage(self, data_count):
		return (data_count / max(self._task_list_total, 1)) * 100

	def percentage_scanned(self):
		return self.percentage(self._task_list_scanned_total)

	def save_list_to_file(self, filepath, data_list):
		data_list = self.filter_list(data_list)
		data_list = [str(x) for x in data_list]
		data_list.sort()

		if not data_list:
			return

		if dirname := os.path.dirname(filepath):
			if not os.path.exists(dirname):
				os.makedirs(dirname)

		with open(self.real_path(filepath), 'w') as file:
			file.write('\n'.join(data_list) + '\n')
