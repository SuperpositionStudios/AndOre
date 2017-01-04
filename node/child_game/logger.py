import child_game.helper_functions
import subprocess
import os


class Logger:
	def __init__(self, region_name, log_level):
		self.log_level = log_level
		self.tick = '0,000,000'
		self.log_directory = child_game.helper_functions.path_to_this_files_directory().replace('/child_game', '') + 'logs/'
		self.filename = f'{self.log_directory}{region_name}-logs.txt'
		self.touch_file()

		self.log(f'Starting logger at priority {self.log_level}', 11)

	def touch_file(self):
		if not os.path.exists(self.log_directory):
			os.makedirs(self.log_directory)
		subprocess.call(['touch', self.filename])

	def update_tick(self, new_tick: int):
		self.tick = child_game.helper_functions.commafy(new_tick, 7)

	def log(self, message, priority=0):
		"""
		Write the message into the log.
		:param message: A string to log
		:param priority: An integer with the message priority. The default value is 0, and the default log level is 1 so the message wouldn't be written, as it only writes messages higher or equal to the log level.
		:return:
		"""
		if priority >= self.log_level:
			with open(self.filename, 'a') as file:
				file.write(f'{child_game.helper_functions.get_date_and_time()} | Tick: {self.tick} | Priority: {priority} | {message}\n')
