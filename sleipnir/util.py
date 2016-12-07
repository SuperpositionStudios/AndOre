import subprocess


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
