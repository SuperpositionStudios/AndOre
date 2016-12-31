import json
import bcrypt
import os
from typing import Dict


def encrypt_new_password(password):
	one_time_use_salt = bcrypt.gensalt()
	encrypted_password = bcrypt.hashpw(str.encode(password), one_time_use_salt)
	return encrypted_password


def encrypt_password(stored_password, entered_password):
	return bcrypt.hashpw(bytes(entered_password, 'utf-8'), stored_password)


def path_to_this_files_directory():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	return dir_path + '/'


class Permissions:
	def __init__(self):
		json_data = open(path_to_this_files_directory() + 'settings.json')
		settings = json.load(json_data)

		self.permissions = settings.get('permissions', {})

	def privilege(self, level: str) -> Dict:
		return self.permissions.get(level, {})
