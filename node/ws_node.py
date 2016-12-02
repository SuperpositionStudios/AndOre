from child_game import world as world_py
import asyncio
import json
import requests
import websockets
import datetime
from typing import Dict


class ConnectedClient:
	def __init__(self, connection):
		self.aid = None
		self.connection = connection
		self.authenticated = True

	async def send_dict(self, obj: dict):
		await self.connection.send(dumps(obj))

	def is_authenticated(self):
		return self.authenticated


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


class Node:
	def __init__(self, node_name: str, node_port: int, node_public_address, erebus_address, sleipnir_address,
				 star_gates=['Panagoul']):
		self.name = node_name
		self.port = node_port
		self.public_address = node_public_address
		self.erebus_address = erebus_address
		self.sleipnir_address = sleipnir_address

		self.sleipnir_connection = None

		self.connected_clients = dict()  # type: Dict[str, ConnectedClient]

		self.world = world_py.World(sleipnir_address, self.new_message_sleipnir)
		self.world.spawn_ore_deposits(5)
		for target_node in star_gates:
			self.world.get_random_cell().add_structure('StarGate', target_node)

		self.tick_server_if_needed()

		print("Running {} on port {}".format(self.name, self.port))

	async def send_state_to_all(self):
		world_state = self.world.client_side_render()
		aids = self.connected_clients.keys()
		for aid in aids:
			try:
				await self.send_state(aid, world_state=world_state, send_ping=True)
			except:
				pass

	async def send_state(self, aid: str, world_state=None, send_ping=False) -> bool:
		try:
			connected_client = self.connected_clients.get(aid, None)

			if connected_client is not None:

				inventory = self.world.players[aid].corp.render_inventory()
				vitals = self.world.players[aid].get_vitals()
				corp_id = self.world.players[aid].corp.corp_id

				if world_state is None:
					world_state = self.world.client_side_render()

				dict_being_sent = {
					'authenticated': connected_client.is_authenticated(),
					'request': 'send_state_client_render',
					'world': world_state['world'],
					'standings': world_state['standings'],
					'inventory': inventory,
					'vitals': vitals,
					'corp_id': corp_id
				}

				if send_ping:
					dict_being_sent['time'] = datetime.datetime.utcnow().isoformat()

				await connected_client.send_dict(dict_being_sent)

				return True
		except:
			return False

	def new_message_sleipnir(self, data: dict):
		asyncio.get_event_loop().create_task(self.sleipnir_connection.send(dumps(data)))

	def get_username(self, aid: str):
		req = requests.get(self.erebus_address + '/get/username', params={'aid': aid}).json()
		return req

	# @profile
	def tick_server_if_needed(self):
		now = datetime.datetime.now()
		if (now - self.world.last_tick).microseconds >= self.world.microseconds_per_tick:
			self.world.tick()
			asyncio.get_event_loop().create_task(self.send_state_to_all())
		asyncio.get_event_loop().call_later(self.world.seconds_per_tick, self.tick_server_if_needed)

	async def game_client(self, websocket, path):
		# Register.
		try:
			# Implement logic here.
			aid = None
			username = None
			authenticated = False
			while True:
				request = await websocket.recv()
				request = loads(request)

				if authenticated:
					if request.get('request', None) == 'ping':
						await websocket.send(dumps({
							'request': 'pong',
							'time': datetime.datetime.utcnow().isoformat()
						}))
					elif request.get('request', None) == 'action':
						action = request.get('action', '')
						try:
							self.world.players[aid].action(action)
						except Exception as e:
							repr(e)

						await self.send_state(aid, send_ping=True)
				else:
					if request.get('request', None) == 'register':
						aid = request.get('aid', '')
						erebus_response = self.get_username(aid)
						if erebus_response.get('valid_aid', False):
							username = erebus_response.get('username', '')
							authenticated = True
							self.connected_clients[aid] = ConnectedClient(websocket)
							await websocket.send(dumps({
								'request': 'auth',
								'authenticated': authenticated,
								'nodeName': self.name
							}))
						else:
							await websocket.send(dumps({
								'authenticated': authenticated,
								'message': "Invalid aid"
							}))
					else:
						await websocket.send(dumps({
							'authenticated': authenticated,
							'message': "You must register your connection!"
						}))
		finally:
			# Unregister.
			self.connected_clients.pop(aid, None)
			print("Bye bye user")

	async def sleipnir_client(self):
		async with websockets.connect(self.sleipnir_address) as websocket:
			try:
				self.sleipnir_connection = websocket

				await websocket.send(dumps({
					'request': 'register',
					'type': 'node',
					'name': self.name,
					'public_address': self.public_address
				}))

				while True:
					request = await websocket.recv()
					request = loads(request)
					# print('Sleipnir: {}'.format(request))
					request_type = request.get('request', None)
					if request_type == 'player_enter':
						# Checking to see if the player is not in the world.
						# We check this because if the node (we) don't know about a player and they try to join
						# bad stuff happens.
						if self.world.active_aid(request.get('aid', '')) is False:
							player_corp_id = request.get('cid')
							player_aid = request.get('aid')
							corp_ore_quantity = request.get('coq', 0)
							new_player_obj = self.world.new_player(player_id=player_aid, corp_id=player_corp_id,
																   corp_ore_quantity=corp_ore_quantity)
					elif request_type == 'update_values':
						response = request.get('data', {})
						self.world.update_values(response)
					elif request_type == 'transfer_assets':
						acquiree_id = request.get('acquiree_id', '')
						acquirer_id = request.get('acquirer_id', '')
						if acquiree_id != '' and acquirer_id != '':
							self.world.transfer_corp_assets(acquirer_id, acquiree_id)
			finally:
				print("Connection to sleipnir closed")
				asyncio.get_event_loop().create_task(self.sleipnir_client)
