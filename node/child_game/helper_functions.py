import config
import subprocess
import os
import datetime
import json


def dumps(obj: dict):
	try:
		return json.dumps(obj)
	except:
		return "{}"


def loads(obj: str):
	try:
		return json.loads(obj)
	except:
		return {}


def drint(text):
	if config.developing:
		print(text)


def flatten_2d_list(x):
	response = []
	for i in x:
		for k in i:
			response.append(k)
	return response


def calculate_standing(standing, modifier):
	if standing == 'E' and modifier == 1:
		return 'N'
	elif standing == 'E' and modifier == -1:
		return 'E'
	elif standing == 'N' and modifier == 1:
		return 'A'
	elif standing == 'N' and modifier == -1:
		return 'E'
	elif standing == 'A' and modifier == 1:
		return 'A'
	elif standing == 'A' and modifier == -1:
		return 'N'
	else:
		return 'N'


def get_git_revision_hash(return_bytes=False):
	if return_bytes:
		return subprocess.check_output(['git', 'rev-parse', 'HEAD'])
	else:
		return str(subprocess.check_output(['git', 'rev-parse', 'HEAD']), 'utf-8')


def get_git_revision_short_hash(return_bytes=False):
	if return_bytes:
		return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
	else:
		return str(subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']), 'utf-8')


def path_to_this_files_directory():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	return dir_path + '/'


def get_date_and_time():
	now = datetime.datetime.now()
	return f"{'%02d' % now.month}/{'%02d' % now.day}/{now.year}-{'%02d' % now.hour}:{'%02d' % now.minute}:{'%02d' % now.second}"


def commafy(x: int, total_digits=0) -> str:
	"""
	Adds leading zeros and commas to an int. 5 >> 5 | 1234 >> 1,234 | 1234, 7 >> 0,001,234
	:param x: The integer to be converted into a string
	:param total_digits: The total length (excluding commas) that the result will have
	:return:
	"""
	number_without_commas = None

	if total_digits == 0:
		number_without_commas = '%0{}d'.format(len(str(x))) % x
	else:
		number_without_commas = '%0{}d'.format(total_digits) % x

	reversed_string_list = list(number_without_commas[::-1])

	reversed_final_list = []

	for i in range(len(reversed_string_list)):
		if i % 3 == 0 and i != 0:
			reversed_final_list.append(',')
		reversed_final_list.append(reversed_string_list[i])

	return ''.join(reversed_final_list)[::-1]

