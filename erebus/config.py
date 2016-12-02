# Modifying this while deploying? Well good news you don't have to anymore. Just modify settings.json

import os
import json


def path_to_this_files_directory():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	return dir_path + '/'


def path_to_db(database_name='database.db'):
	return 'sqlite:///' + str(path_to_this_files_directory()) + database_name


def game_server_url():
	with open(path_to_this_files_directory() + 'settings.json') as json_data:
		d = json.load(json_data)
	address = d.get('master_server_address', 'http://localhost:7100')
	return address
