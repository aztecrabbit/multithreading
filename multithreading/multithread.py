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
			item = self._queue_task_list.get()
			data = self.task(item) or item
			self.task_done(data)
			self._queue_task_list.task_done()

	def task(self, task):
		pass

	def task_done(self, *_):
		self._task_list_scanned_total += 1

	def complete(self):
		pass

	def keyboard_interrupt(self):
		self.logger.log('Keyboard Interrupt')

	"""
	Extra
	"""

	def task_success(self, data):
		self._task_list_success.append(data)

	def task_failed(self, data):
		self._task_list_failed.append(data)

	"""
	Utility
	"""

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
