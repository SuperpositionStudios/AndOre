from child_game import world as world_py
from child_game import helper_functions
from child_game.logger import Logger
import asyncio
import json
import requests
import websockets
import datetime
from typing import Dict
import signal
import sys
from child_game import helper_functions


class ConnectedClient:
	def __init__(self, connection):
		self.aid = None
		self.connection = connection
		self.authenticated = True

	async def send_dict(self, obj: dict):
		await self.connection.send(helper_functions.dumps(obj))

	def is_authenticated(self):
		return self.authenticated


class Node:
	def __init__(self, node_name: str, node_port: int, node_public_address, erebus_address, sleipnir_address,
				 star_gates=['Panagoul']):
		self.name = node_name
		self.port = node_port
		self.public_address = node_public_address
		self.erebus_address = erebus_address
		self.sleipnir_address = sleipnir_address

		self.logger = Logger(node_name, 3)
		signal.signal(signal.SIGINT, self.signal_handler)

		self.sleipnir_connection = None

		self.connected_clients = dict()  # type: Dict[str, ConnectedClient]

		self.world = world_py.World(sleipnir_address, self.new_message_sleipnir, self.logger)
		self.world.spawn_ore_deposits(5)
		for target_node in star_gates:
			self.world.get_random_cell().add_structure('StarGate', target_node)

		self.tick_server_if_needed()

		print("Running {} on port {}".format(self.name, self.port))

	def signal_handler(self, signal, frame):
		print('Shutting down ungracefully (graceful exits will be eventually implemented, I hope...)')
		self.logger.log("Shutting down...", 10)
		sys.exit(0)

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
		asyncio.get_event_loop().create_task(self.sleipnir_connection.send(helper_functions.dumps(data)))

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

	async def send_meta_data(self, client: ConnectedClient):
		await client.send_dict({
			'request': 'git_version',
			'git_version': helper_functions.get_git_revision_short_hash()
		})

	async def game_client(self, websocket, path):
		print(f'{websocket.remote_address} Connected')
		aid = None
		username = None
		authenticated = False
		try:
			# Implement logic here.
			while True:
				request = await websocket.recv()
				request = helper_functions.loads(request)

				if authenticated:
					if request.get('request', None) == 'ping':
						await websocket.send(helper_functions.dumps({
							'request': 'pong',
							'time': datetime.datetime.utcnow().isoformat()
						}))
					elif request.get('request', None) == 'action':
						action = request.get('action', '')
						shift_key_down = request.get('shift_key_down', False)
						try:
							self.world.players[aid].action(action, shift_key_down)
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
							print(f'{websocket.remote_address} authenticated as {username}')
							self.connected_clients[aid] = ConnectedClient(websocket)

							await websocket.send(helper_functions.dumps({
								'request': 'auth',
								'authenticated': authenticated,
								'nodeName': self.name
							}))

							await self.send_meta_data(self.connected_clients[aid])
						else:
							await websocket.send(helper_functions.dumps({
								'authenticated': authenticated,
								'message': "Invalid aid"
							}))
					else:
						await websocket.send(helper_functions.dumps({
							'authenticated': authenticated,
							'message': "You must register your connection!"
						}))
		except:
			pass  # if we don't have this, then our console will be spammed by connections closing
		finally:
			# Unregister.
			self.connected_clients.pop(aid, None)
			if username is not None:
				print(f'{username} Disconnected')
			else:
				print(f'{websocket.remote_address} Disconnected')

	async def sleipnir_client(self):
		timer = 0
		while True:
			await asyncio.sleep(timer)
			try:
				async with websockets.connect(self.sleipnir_address) as websocket:
					self.sleipnir_connection = websocket

					print(f'Connected to Sleipnir at {self.sleipnir_address}')
					timer = 0

					await websocket.send(helper_functions.dumps({
						'request': 'register',
						'type': 'node',
						'name': self.name,
						'public_address': self.public_address
					}))
					try:
						while True:
							request = await websocket.recv()
							request = helper_functions.loads(request)
							# print('Sleipnir: {}'.format(request))
							request_type = request.get('request', None)
							if request_type == 'player_enter':
								# Checking to see if the player is not in the world.
								# We check this because if the node (we) don't know about a player and they try to join
								# bad stuff happens.
								if self.world.active_aid(request.get('aid', '')) is False:
									player_corp_id = request.get('cid')
									player_aid = request.get('aid')
									player_username = request.get('username', '')
									corp_ore_quantity = request.get('coq', 0)
									self.world.new_player(player_aid, player_username, player_corp_id, corp_ore_quantity)
							elif request_type == 'update_values':
								response = request.get('data', {})
								self.world.update_values(response)
							elif request_type == 'transfer_assets':
								acquiree_id = request.get('acquiree_id', '')
								acquirer_id = request.get('acquirer_id', '')
								if acquiree_id != '' and acquirer_id != '':
									self.world.transfer_corp_assets(acquirer_id, acquiree_id)
					except:
						print("Connection to Sleipnir Lost...")
						raise ValueError()
			except Exception as e:
				#print(repr(e))
				timer = round(timer + 0.1337, 4)
				print(f'Sleipnir at {self.sleipnir_address} still down. Will try again in {timer}s')
				pass
