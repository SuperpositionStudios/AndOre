import config
import subprocess


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
