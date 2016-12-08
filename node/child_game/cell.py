import uuid
from child_game import gameObject, world, corporation
from typing import Tuple, List
from child_game.exceptions import CellCoordinatesOutOfBoundsError
from child_game import exceptions


class Cell:
	def __init__(self, _world: 'world.World', _row: int, _col: int):
		self.world = _world
		self.obj_id = str(uuid.uuid4())
		self.row = _row  # type: int
		self.col = _col  # type: int
		self.contents = []

	def get_cell_by_offset(self, row_offset: int, col_offset: int) -> 'Cell':
		try:
			fetched_cell = self.world.get_cell(self.row + row_offset, self.col + col_offset)
			return fetched_cell
		except CellCoordinatesOutOfBoundsError:
			raise CellCoordinatesOutOfBoundsError(self.row + row_offset, self.col + col_offset)

	def is_next_to_ore_deposit(self) -> bool:
		directions = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]]
		for tup in directions:
			try:
				_cell = self.get_cell_by_offset(tup[0], tup[1])
				struct = _cell.contains_object_type('OreDeposit')
				if struct[0]:
					od = _cell.get_game_object_by_obj_id(struct[1])
					if od[0]:
						od_obj = od[1]
						assert (od_obj.__class__.__name__ == 'OreDeposit')
						return True
			except CellCoordinatesOutOfBoundsError:
				pass
		return False

	def is_adjacent_to_sentry_turret(self, check_horizontally=True, check_vertically=True, check_diagonally=False,
									 check_self=False):

		directions_checked = []  # type: List[Tuple[int, int]]
		if check_self:
			directions_checked.append((0, 0))
		if check_horizontally:
			directions_checked.append((0, -1))
			directions_checked.append((0, 1))
		if check_vertically:
			directions_checked.append((-1, 0))
			directions_checked.append((1, 0))
		if check_diagonally:
			directions_checked.append((-1, -1))
			directions_checked.append((-1, 1))
			directions_checked.append((1, 1))
			directions_checked.append((1, -1))

		for offset_tuple in directions_checked:
			try:
				_cell = self.get_cell_by_offset(offset_tuple[0], offset_tuple[1])
				try:
					turret_id = _cell.get_object_id_of_first_game_object_found('SentryTurret')
					return True
				except exceptions.NoGameObjectOfThatClassFoundException:
					pass

			except CellCoordinatesOutOfBoundsError:
				pass

		return False

	def damage_first_player(self, attacking_corp: 'corporation.Corporation', damage):
		struct = self.contains_object_type('Player')
		if struct[0]:
			player = self.get_game_object_by_obj_id(struct[1])
			if player[0]:
				player_obj = player[1]
				standing = attacking_corp.fetch_standing(player_obj.corp.corp_id)
				if standing == 'N' or standing == 'E':
					player_obj.take_damage(damage)
					return True
		return False

	def deconstruct_first_possible_building_owned_by_corp(self, corp_id):
		for building in self.contents:
			building_owner_id = None
			try:
				building_owner_id = building.owner_corp.corp_id
			except:
				pass
			if corp_id == building_owner_id:
				building.died()
				return True
		return False

	def add_game_object(self, x):
		self.contents.append(x)

	def add_fence(self):
		a = gameObject.Fence(self)
		self.add_game_object(a)
		return a.ore_cost_to_deploy

	def add_ore_deposit(self):
		a = gameObject.OreDeposit(self)
		self.contents.append(a)

	def add_corp_owned_building(self, owner_corp: 'corporation.Corporation', building_type: str):
		assert (owner_corp.__class__.__name__ == 'Corporation')
		a = None
		if building_type == 'SentryTurret':
			a = gameObject.SentryTurret(self, owner_corp)
		elif building_type == 'SpikeTrap':
			a = gameObject.SpikeTrap(self, owner_corp)
		elif building_type == 'RespawnBeacon':
			a = gameObject.RespawnBeacon(self, owner_corp)
		elif building_type == 'Door':
			a = gameObject.Door(self, owner_corp)
		elif building_type == 'Pharmacy':
			a = gameObject.Pharmacy(self, owner_corp)
		elif building_type == 'Hospital':
			a = gameObject.Hospital(self, owner_corp)
		elif building_type == 'OreGenerator':
			a = gameObject.OreGenerator(self, owner_corp)
		elif building_type == 'Fence':
			a = gameObject.Fence(self, owner_corp)
		self.add_game_object(a)

	def add_structure(self, building_type: str, star_gate_target=''):
		obj = None
		if building_type == 'StarGate':
			obj = gameObject.StarGate(self, star_gate_target)
		self.add_game_object(obj)

	def remove_object(self, object_id: str):
		for i in range(0, len(self.contents)):
			if self.contents[i].obj_id == object_id:
				del self.contents[i]
				return

	def contains_object_type(self, obj_type_name: str) -> Tuple[bool, any]:
		"""

		:param obj_type_name: The class name, example: 'Cell'
		:return: A tuple, [0] = a bool, true if cell contains obj_type_name. [1] = obj_id to first obj found of that class in the cell.
		"""
		# obj_type_name is the class name, example: 'Cell'
		# Returns a tuple, a boolean answering if the cell contains an object with the same class name as the input
		# and a string, if the boolean is true then it will return the object's obj_id
		# Returns as soon as one of the objects is found, so this may be unreliable in some use cases
		for obj in self.contents:
			if obj.__class__.__name__ == obj_type_name:
				return True, obj.obj_id
		return False, ''

	def get_object_id_of_first_game_object_found(self, obj_type_name: str) -> str:
		"""

		:param obj_type_name: The class name, if you want to find a Hospital in the cell, then input is 'Hospital'
		:return: The game object's id.
		"""
		for obj in self.contents:
			if obj.__class__.__name__ == obj_type_name:
				return obj.obj_id
		raise exceptions.NoGameObjectOfThatClassFoundException(obj_type_name)

	def get_game_object_by_obj_id(self, obj_id: str):
		for obj in self.contents:
			if obj.obj_id == obj_id:
				return True, obj
		return False, None

	def new_get_game_object_by_obj_id(self, obj_id: str) -> any:
		for obj in self.contents:
			if obj.obj_id == obj_id:
				return obj
		raise exceptions.NoGameObjectByThatObjectIDFoundException()

	def can_enter(self, player_obj=None):
		if player_obj is not None:
			assert (player_obj.__class__.__name__ == 'Player')
			for obj in self.contents:

				class_types = {
					'OreDeposit': 0,
					'StarGate': 0,
					'Fence': 0,
					'Loot': 0,
					'Player': 1
				}
				class_type = class_types.get(obj.__class__.__name__, 2)

				if class_type == 0:
					obj_standing = 'N'
				elif class_type == 1:
					obj_standing = obj.corp.fetch_standing_for_player(player_obj.obj_id)
				elif class_type == 2:
					obj_standing = obj.owner_corp.fetch_standing_for_player(player_obj.obj_id)

				if obj.passable[obj_standing] is False:
					return False
			return True
		else:
			for obj in self.contents:
				obj_standing = 'N'
				if obj.passable[obj_standing] is False:
					return False
			return True

	def client_side_render(self):
		prepared_list = {
			"contents": []
		}
		for obj in self.contents:

			object_ints = {
				'Fence': 1,
				'Hospital': 2,
				'OreGenerator': 3,
				'Pharmacy': 4,
				'RespawnBeacon': 5,
				'Door': 6,
				'Player': 7,
				'Loot': 8,
				'SpikeTrap': 9,
				'SentryTurret': 10,
				'OreDeposit': 11,
				'StarGate': 12
			}

			render_types = {
				1: 1,
				2: 1,
				3: 1,
				4: 1,
				5: 1,
				6: 1,
				7: 2,
				8: 3,
				9: 1,
				10: 1,
				11: 3,
				12: 4
			}

			object_int = object_ints.get(obj.__class__.__name__, None)
			render_type = render_types.get(object_int, None)

			if object_int is not None and render_type is not None:
				rendered_obj = [object_int]
				if render_type == 1:
					rendered_obj.append(obj.owner_corp.corp_id)
				elif render_type == 2:
					rendered_obj.append(obj.aid)
					rendered_obj.append(obj.corp.corp_id)
				elif render_type == 4:
					rendered_obj.append(obj.target_node)
				prepared_list["contents"].append(rendered_obj)
		return prepared_list
