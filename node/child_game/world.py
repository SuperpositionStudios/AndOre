import uuid, random, datetime
from child_game.cell import Cell
from child_game.player import Player
from child_game.corporation import Corporation
import warnings
from child_game import helper_functions
from child_game.exceptions import CellCoordinatesOutOfBoundsError
from typing import Dict, List, Tuple
import json
from child_game.logger import Logger


def dumps(obj: dict) -> str:
	try:
		return json.dumps(obj)
	except:
		return "{}"


def loads(obj: str) -> dict:
	try:
		return json.loads(obj)
	except:
		return {}


class World:  # World is not really world, it's more Level

	def __init__(self, master_node_address, message_master_node, logger: Logger):
		self.logger = logger

		print("Initializing World...")
		self.master_node_address = master_node_address
		self.message_master_node = message_master_node
		self.rows = 20  # (9 * 3 - 2) - 5
		self.cols = 55  # (16 * 3) + 7
		self.logger.log('Initializing world with {num_rows} rows and {num_columns} columns'
						' and Sleipnir at {sleipnir_address}'.format(
			num_rows=self.rows,
			num_columns=self.cols,
			sleipnir_address=self.master_node_address
		), 10)

		self.world = []  # type: List[List[Cell]]
		self.world_age = 1
		self.last_tick = datetime.datetime.now()
		self.microseconds_per_tick = 250000  # type: int
		self.seconds_per_tick = float(self.microseconds_per_tick) / float(1000000)

		self.logger.log('Running at {spt} seconds per tick'.format(spt=self.seconds_per_tick), 10)

		self.players = dict()  # type: Dict[str, Player]
		self.corporations = dict()  # type: Dict[str, Corporation]
		self.buildings = dict()

		for row in range(self.rows):
			current_row = []  # type: List[Cell]
			for col in range(self.cols):
				current_cell = Cell(self, row, col)
				current_row.append(current_cell)
			self.world.append(current_row)

		self.respawn_cell = self.get_cell(0, 0)

		assert (len(self.world) == self.rows)
		assert (len(self.world[0]) == self.cols)

		print("Created world with dimensions {}x{}".format(self.cols, self.rows))

	def tick(self):
		self.last_tick = datetime.datetime.now()
		self.world_age += 1
		self.logger.update_tick(self.world_age)
		self.tick_corp_buildings()
		self.send_pending_requests()

	def send_pending_requests(self):
		data = {
			'corporations': dict(),
		}
		for corp_id in self.corporations:
			corp_obj = self.corporations[corp_id]
			data['corporations'][corp_id] = {
				'ore_delta': corp_obj.pending_requests['ore_delta'],
				'inventory_deltas': corp_obj.pending_requests['inventory_deltas']
			}
		self.message_master_node({'data': data, 'request': 'update_values'})

	def update_values(self, response):
		for corp_id in response['corporations']:
			if corp_id in self.corporations:
				corp_obj = self.corporations[corp_id]
				corp_obj.reset_pending_requests()
				corp_obj.set_ore_quantity(response['corporations'][corp_id]['ore_quantity'])
				corp_obj.update_inventory_quantities(response['corporations'][corp_id]['inventory'])

	def tick_corp_buildings(self):
		for corp_id, corp in self.corporations.items():
			corp.tick_buildings()

	def corp_exists(self, corp_id) -> bool:
		return corp_id in self.corporations

	def active_aid(self, aid: str):
		return aid in self.players

	def new_player(self, player_id: str, username: str, corp_id: str, corp_ore_quantity: float) -> None:
		spawn_location = self.random_can_enter_cell()  #

		# Corporation
		# If the corp does not exist in our node we create it here
		if self.corp_exists(corp_id) is False:
			self.new_corporation(corp_id=corp_id)

		# at this point, we know there is a corp in our node with the corp_id that was either passed in or generated.
		_corp = self.corporations[corp_id]
		# We update our ore quantity for the corp here
		_corp.ore_quantity = corp_ore_quantity

		new_player = Player(player_id, username, self, spawn_location, _corp)
		_corp.add_member(new_player)
		spawn_location.add_game_object(new_player)
		self.players[player_id] = new_player
		self.logger.log(f'{username} joined the region', 8, verbose=True)

	def despawn_player(self, player_id):
		if self.valid_player_id(player_id):
			# Removing player from world
			player_obj = self.players[player_id]
			player_obj.despawn()
			# Removing player object from player list
			self.players.pop(player_id)

	def random_can_enter_cell(self):
		random_cell = self.get_random_cell()
		max_tries = self.rows * self.cols
		attempt = 1
		while random_cell.can_enter() is False:
			random_cell = self.get_random_cell()
			attempt += 1
			if attempt == max_tries:
				return self.get_cell(0, 0)
		return random_cell

	def new_corporation(self, corp_id=None) -> Corporation:
		new_corp = Corporation(self, corp_id=corp_id)
		self.corporations[new_corp.corp_id] = new_corp
		print(self.corporations)
		return new_corp

	def spawn_ore_deposits(self, num=1):
		assert (num <= self.rows * self.cols)

		for i in range(num):
			random_cell = self.get_random_cell()
			max_tries = self.rows * self.cols
			attempt = 1
			while random_cell.can_enter() is False:
				random_cell = self.get_random_cell()
				attempt += 1
				if attempt == max_tries:
					return
			random_cell.add_ore_deposit()

	def transfer_corp_assets(self, acquirer_id, acquiree_id):
		print("Transferring assets of {} to {}".format(acquiree_id, acquirer_id))
		acquirer = self.corporations[acquirer_id]
		acquiree = self.corporations[acquiree_id]
		acquiree_member_count = len(acquiree.members)
		for player in acquiree.members:
			player.corp = acquirer
			acquirer.add_member(player)
		acquiree.members = []
		print("Acquiree going from {} to {} members".format(acquiree_member_count, len(acquiree.members)))
		for building in acquiree.buildings:
			building.owner_corp = acquirer
		acquiree.buildings = []
		self.corporations.pop(acquiree_id, None)

	def transfer_player_to_random_node(self, player_aid: str):
		self.message_master_node({
			'request': 'abort_player',
			'player_aid': player_aid
		})

	def transfer_player_to_node(self, player_aid: str, target_node: str):
		self.message_master_node({
			'request': 'transfer_player_to_node',
			'player_aid': player_aid,
			'target_node': target_node
		})

	def valid_player_id(self, _id: str) -> bool:
		return _id in self.players

	def get_cell(self, row: int, col: int) -> Cell:
		if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
			raise CellCoordinatesOutOfBoundsError(row, col)
		return self.world[row][col]

	def get_random_cell(self) -> Cell:
		row = random.randint(0, self.rows - 1)  # randint is inclusive
		col = random.randint(0, self.cols - 1)  # randint is inclusive
		return self.get_cell(row, col)

	def client_side_render(self):

		rendered_world = []
		for row in range(self.rows):
			current_row = []
			for col in range(self.cols):
				rendered = self.world[row][col].client_side_render()
				current_row.append(rendered)
			rendered_world.append(current_row)

		standings = {}
		for corp_id, corporation in self.corporations.items():
			standings[corp_id] = corporation.standings

		response = {
			'world': rendered_world,
			'standings': standings
		}
		return response
