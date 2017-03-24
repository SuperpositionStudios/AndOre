from ws_node import Node
import websockets
import asyncio
import os
import json
from typing import List


def path_to_this_files_directory():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	return dir_path + '/'


class NodeStarter:
	def __init__(self, node_name: str, node_port: int, public_address: str, star_gates: List[str], sleipnir_address,
				 erebus_address, node_key):

		n = Node(node_name, node_port, public_address, erebus_address, sleipnir_address, star_gates=star_gates)

		start_server = websockets.serve(n.game_client, '0.0.0.0', node_port)

		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_until_complete(n.sleipnir_client())
		asyncio.get_event_loop().run_forever()
