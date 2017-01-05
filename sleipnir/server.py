import asyncio
import json
import requests
import websockets
from typing import Dict, List
import game_classes
import random
import os
import util


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


class PlayerConnection:
	def __init__(self, websocket: websockets):
		self.websocket = websocket

	async def send_dict(self, obj):
		try:
			await self.websocket.send(dumps(obj))
		except Exception as e:
			repr(e)

	async def send_str(self, obj):
		await self.websocket.send(obj)


# Loading settings from json files

def path_to_this_files_directory():
	dir_path = os.path.dirname(os.path.realpath(__file__))
	return dir_path + '/'


with open(path_to_this_files_directory() + 'settings.json') as json_data:
	d = json.load(json_data)

in_production = d.get('inProduction', False)

erebus_address = d.get('productionErebusAddress', '') if in_production else d.get('developmentErebusAddress', '')

public_address = 'localhost'
port = d.get('port', 7100)

with open(path_to_this_files_directory() + 'keys.json') as json_data:
	d = json.load(json_data)

node_key = d.get('node', '')
sleipnir_key = d.get('sleipnir', '')

nodes = dict()  # type: Dict[str, Node]
corporations = dict()  # type: Dict[str, game_classes.Corporation]
players = dict()  # type: Dict[str, game_classes.Player]
connected_players = dict()  # type: Dict[str, PlayerConnection]


class Node:
	def __init__(self, connection):
		self.connection = connection
		self.name = None
		self.public_address = None

	def set_name(self, name: str):
		self.name = name

	def set_public_address(self, address: str):
		self.public_address = address


def get_username(aid):
	req = requests.get(erebus_address + '/get/username', params={'aid': aid}).json()
	return req


def get_random_node_name(skip=None):
	choice = random.choice(list(nodes.keys()))
	while choice == skip:
		choice = random.choice(list(nodes.keys()))
	return choice


async def transfer_player(aid: str, new_node_name: str) -> bool:
	# Checking to see if node is in the pool
	if new_node_name in nodes:
		players[aid].assign_node(new_node_name)

		# Tell new node about player
		await nodes[new_node_name].connection.send(dumps({
			'request': 'player_enter',
			'coq': players[aid].corp.amount_of_ore(),
			'aid': aid,
			'cid': players[aid].corp.corp_id,
			'username': players[aid].username
		}))

		# Tell player to abandon their current node ws and make a new connection
		if aid in connected_players:
			await connected_players[aid].send_dict({
				'request': 'update_node',
				'node_name': new_node_name,
				'node_address': nodes[new_node_name].public_address
			})
			return True
	return False


async def send_number_of_connected_players(send_to_all: bool, target_player_aid=''):
	if send_to_all:
		for connected_player_aid, connected_player in connected_players.items():

			await connected_player.send_dict({
				'request': 'numConnectedPlayers',
				'numConnectedPlayers': len(connected_players)
			})
	else:
		if target_player_aid in connected_players:
			await connected_players[target_player_aid].send_dict({
				'request': 'numConnectedPlayers',
				'numConnectedPlayers': len(connected_players)
			})


async def send_meta_data(client: PlayerConnection):
	await client.send_dict({
		'request': 'git_version',
		'git_version': util.get_git_revision_short_hash()
	})


async def new_connection_handler(websocket, path):
	if path == '/player':
		global players
		global connected_players
		print(f'{websocket.remote_address} Connected')
		aid = None
		username = None
		try:
			authenticated = False
			current_node = None
			while True:
				request = await websocket.recv()
				request = loads(request)
				# print(request)

				if authenticated:
					if request.get('request', None) == 'join':
						# check if loaded in a world
						if aid in players:
							current_node = players[aid].get_current_node()
							if current_node in nodes:
								pass
							else:
								current_node = get_random_node_name()
								players[aid].assign_node(current_node)
							node_obj = nodes[current_node]
							await transfer_player(aid, current_node)
							await websocket.send(dumps({
								'request': 'update_node',
								'node_name': current_node,
								'node_address': node_obj.public_address
							}))
						else:
							new_corp = game_classes.Corporation()
							if in_production is False:
								new_corp.gain_ore(5000)
							else:
								new_corp.gain_ore(205)
							corporations[new_corp.corp_id] = new_corp
							current_player = game_classes.Player()
							current_player.assign_aid(aid)
							current_player.assign_corp(new_corp)
							current_player.assign_username(username)
							current_player.assign_node(get_random_node_name())

							players[aid] = current_player

							current_node = players[aid].get_current_node()
							node_obj = nodes[current_node]

							await nodes[current_node].connection.send(dumps({
								'request': 'player_enter',
								'coq': current_player.corp.amount_of_ore(),
								'aid': aid,
								'cid': new_corp.corp_id
							}))

							await websocket.send(dumps({
								'request': 'update_node',
								'node_name': node_obj.name,
								'node_address': node_obj.public_address
							}))
					elif request.get('request', None) == 'numConnectedPlayers':
						await websocket.send(dumps({
							'request': 'numConnectedPlayers',
							'authenticated': authenticated,
							'numConnectedPlayers': len(connected_players)
						}))
				else:
					if request.get('request', None) == 'register':
						supplied_aid = request.get('aid', None)
						if supplied_aid is not None:
							erebus_response = get_username(supplied_aid)
							if erebus_response.get('valid_aid', False):
								aid = supplied_aid
								username = erebus_response.get('username', 'None')
								authenticated = True
								connected_players[aid] = PlayerConnection(websocket)
								print(f'{websocket.remote_address} authenticated as {username}')
								await websocket.send(dumps({
									'authenticated': authenticated
								}))
								await send_meta_data(connected_players[aid])
								await send_number_of_connected_players(True)
							else:
								await websocket.send(dumps({
									'authenticated': authenticated
								}))
						else:
							await websocket.send(dumps({
								'authenticated': authenticated
							}))
		except:
			pass  # Have to have an except or else we'll get our console spammed with disconnect exceptions
		finally:
			connected_players.pop(aid, None)
			if username is not None:
				print(f'{username} Disconnected')
			else:
				print(f'{websocket.remote_address} Disconnected')
			await send_number_of_connected_players(True)
	elif path == '/node':
		# Register.
		client = Node(websocket)
		try:
			# Implement logic here.
			authenticated = False
			while True:
				request = await websocket.recv()
				request = loads(request)
				# print("Node: {}".format(request))

				request_type = request.get('request', None)

				if authenticated:
					if request_type == 'merge_corporations':
						acquirer_id = request.get('acquirer_id', '')
						acquiree_id = request.get('acquiree_id', '')
						if acquiree_id != '' and acquirer_id != '':
							# Transferring Inventories
							corporations[acquirer_id].apply_inventory_delta_multiple(
								corporations[acquiree_id].assets['inventory'])
							# Changing acquiree's player's corp
							for member in corporations[acquiree_id].members:
								member.assign_corp(corporations[acquirer_id])
							corporations[acquirer_id].gain_ore(corporations[acquiree_id].amount_of_ore())
							corporations[acquiree_id].members = []
							corporations.pop(acquiree_id, None)
							# Server telling all child nodes to transfer corp belongings including players
							# Transferring ownership of buildings is handled by the message
							for node_name in nodes:
								await nodes[node_name].connection.send(dumps({
									'request': 'transfer_assets',
									'key': sleipnir_key,
									'acquirer_id': acquirer_id,
									'acquiree_id': acquiree_id
								}))
					elif request_type == 'update_values':
						# print("Updating values")
						"""
						example_data = {
							'corporations': {
								'2dbb7bed-f20a-4e59-ac71-ab1ed87c89f7': {
									'inventory_deltas': {
										'AttackPowerPotion': 0,
										'HealthPotion': 0,
										'HealthCapPotion': 0,
										'MinerMultiplierPotion': 0
									},
									'ore_delta': 3.0
								}
							}
						}
						"""
						data = request.get('data', None)
						if data is not None:
							for corp_id in data.get('corporations', {}):
								if corp_id in corporations:
									corp_obj = corporations[corp_id]
									corp_obj.apply_child_server_deltas(data['corporations'][corp_id])
						response = {
							'corporations': {}
						}
						for corp_id in corporations:
							corp_obj = corporations[corp_id]
							response['corporations'][corp_id] = {
								'ore_quantity': corp_obj.amount_of_ore(),
								'inventory': corp_obj.assets['inventory']
							}
						# print(response)
						await websocket.send(dumps({
							'data': response,
							'request': 'update_values'
						}))
					elif request_type == 'abort_player':
						player_aid = request.get('player_aid', '')
						if player_aid != '' and len(nodes) > 1:
							current_node = players[player_aid].get_current_node()
							new_node = get_random_node_name(skip=current_node)
							await transfer_player(player_aid, new_node)
					elif request_type == 'transfer_player_to_node':
						target_node = request.get('target_node', '')
						player_aid = request.get('player_aid', '')
						if player_aid != '' and target_node != '':
							await transfer_player(player_aid, target_node)

				else:
					if request_type == 'register':
						if request.get('name', None) is not None and request.get('public_address', None) is not None:
							client.set_name(request.get('name', ''))
							client.set_public_address(request.get('public_address', ''))
							nodes[request.get('name', '')] = client
							authenticated = True
							print("Added {} to pool of nodes".format(client.name))
						await websocket.send(dumps({
							'authenticated': authenticated
						}))
					else:
						await websocket.send(dumps({
							'authenticated': authenticated,
						}))
		except:
			pass  # Have to have this except block here or else we'll get spammed with disconnect exceptions.
		finally:
			# Unregister.
			nodes.pop(client.name, None)
			print(f'Removed {client.name} from pool of nodes')

print(f'Running Sleipnir on port {port}')

start_server = websockets.serve(new_connection_handler, 'localhost', port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
