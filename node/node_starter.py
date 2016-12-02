from ws_node import Node
import websockets
import asyncio
import os
import json


class NodeStarter:
	def __init__(self, node_name: str, node_port: int, production_public_address: str, development_public_address: str,
				 star_gates=['Panagoul']):
		with open(self.path_to_this_files_directory() + 'keys.json') as json_data:
			d = json.load(json_data)

		node_key = d.get('node', '')
		sleipnir_key = d.get('sleipnir', '')

		with open(self.path_to_this_files_directory() + 'settings.json') as json_data:
			d = json.load(json_data)

		in_production = d.get('inProduction', False)

		# Config

		node_name = node_name
		node_port = node_port
		production_public_address = production_public_address
		development_public_address = development_public_address

		#

		node_public_address = production_public_address if in_production else development_public_address

		erebus_address = d.get('productionErebusAddress', '') if in_production else d.get('developmentErebusAddress',
																						  '')
		sleipnir_address = d.get('productionSleipnirAddress', '') if in_production else d.get(
			'developmentSleipnirAddress', '')

		node_public_semi_address = 'localhost'

		n = Node(node_name, node_port, node_public_address, erebus_address, sleipnir_address, star_gates=star_gates)

		start_server = websockets.serve(n.game_client, node_public_semi_address, node_port)

		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_until_complete(n.sleipnir_client())
		asyncio.get_event_loop().run_forever()

	def path_to_this_files_directory(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		return dir_path + '/'
