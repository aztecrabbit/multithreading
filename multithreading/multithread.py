import datetime
import os
import sys

from queue import Queue
from threading import Thread, RLock

from .logger import Logger


class MultiThread:
	logger = Logger(level='DEBUG')

	def __init__(self, task_list, threads=8):
		self._lock = RLock()
		self._queue_task_list = Queue()

		self._task_list = task_list
		self._task_list_total = 0
		self._task_list_scanned_total = 0
		self._task_list_success = []
		self._task_list_failed = []

		self._threads = threads or 8

	"""
	Core
	"""

	def filter_list(self, task_list):
		filtered_task_list = []

		for item in task_list:
			if isinstance(item, str):
				item = item.strip()
				if item.startswith('#'):
					continue

			filtered_task_list.append(item)

		return list(set(filtered_task_list))

	def add_task(self, data):
		self._queue_task_list.put(data)
		self._task_list_total += 1

	def get_task_list(self):
		return self.filter_list(self._task_list)

	def start(self):
		try:
			for item in self.get_task_list():
				self._queue_task_list.put(item)

			self._task_list_total = self._queue_task_list.qsize()
			self.start_threads()
			self.join()
		except KeyboardInterrupt:
			with self._queue_task_list.mutex:
				self.keyboard_interrupt()
				self._queue_task_list.queue.clear()
		finally:
			self.complete()

	def join(self):
		self._queue_task_list.join()

	def start_threads(self):
		for _ in range(min(self._threads, self._queue_task_list.qsize()) or self._threads):
			Thread(target=self.start_thread, daemon=True).start()

	def start_thread(self):
		while True:
			task = self._queue_task_list.get()
			data = self.task(task)
			self.task_done(task, data)
			self._queue_task_list.task_done()

	def task(self, *_):
		pass

	def task_done(self, *_):
		self._task_list_scanned_total += 1

	def keyboard_interrupt(self):
		self.log('Keyboard Interrupt')

	def complete(self):
		self.save_list_to_file('data.lst', self.success_list())
		self.save_list_to_file('data-failed.lst', self.failed_list())

	"""
	Extra
	"""

	def success_list(self):
		return self._task_list_success

	def failed_list(self):
		return self._task_list_failed

	def task_success(self, data):
		self._task_list_success.append(data)

	def task_failed(self, data):
		self._task_list_failed.append(data)

	"""
	Utility
	"""

	def real_path(self, name):
		return os.path.dirname(os.path.abspath(sys.argv[0])) + '/' + name

	def log_replace(self, *messages):
		default_messages = [
			f'{self.percentage_scanned():.3f}%',
		]

		self.logger.replace(' - '.join(default_messages + list(messages)))

	def log(self, *args, **kwargs):
		self.logger.log(*args, **kwargs)

	def percentage(self, data_count):
		return (data_count / max(self._task_list_total, 1)) * 100

	def percentage_scanned(self):
		return self.percentage(self._task_list_scanned_total)

	def percentage_success(self):
		return self.percentage(len(self._task_list_success))

	def percentage_failed(self):
		return self.percentage(len(self._task_list_failed))

	def save_list_to_file(self, file_name, data_list):
		data_list = self.filter_list(data_list)
		data_list = [str(x) for x in data_list]
		data_list.sort()

		if not data_list:
			return

		with open(self.real_path(file_name), 'a') as file:
			data_list = [f"# {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"] + data_list
			file.write('\n'.join(data_list) + '\n\n')
