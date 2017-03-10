import uuid, random
from child_game import gameObject, corporation, cell
import child_game
from child_game import exceptions
import math


class Player(gameObject.GameObject):
	def __init__(self, _id: str, username: str, _world: 'child_game.world.World', _cell: 'cell.Cell',
				 _corp: 'corporation.Corporation'):
		super().__init__(_cell)
		assert (_world is not None)
		assert (_corp is not None)

		self.id = _id
		self.aid = self.id
		self.obj_id = _id
		self.world = _world
		self.cell = _cell

		self.username = username

		self.starting_health_cap = 100
		self.health_cap = int(100)

		self.starting_ore = 500
		self.starting_health = 100
		self.health_loss_per_turn = 0.1
		self.health = int(self.starting_health)

		self.health_loss_on_sprint = 2

		self.starting_attack_power = 10
		self.attack_power = int(self.starting_attack_power)

		self.starting_ore_multiplier = 1
		self.ore_multiplier = float(self.starting_ore_multiplier)

		self.delta_ore = 0  # The ore lost/gained in the last tick
		self.row = self.cell.row
		self.col = self.cell.col
		self.shiftKeyActive = False
		self.dir_key = ''
		self.primary_modifier_key = 'm'
		self.secondary_modifier_key = '1'
		self.passable = {
			'M': False,
			'A': False,
			'N': False,
			'E': False
		}
		self.last_action_at_world_age = 0
		self.corp = _corp

		self.prevents_building_in_cell = True

		self.potions_taken = {
			'HealthPotion': {
				'taken': 0,
				'applied': 0
			},
			'HealthCapPotion': {
				'taken': 0,
				'applied': 0
			},
			'AttackPowerPotion': {
				'taken': 0,
				'applied': 0
			},
		}

	# Called when being removed from the node
	def despawn(self):
		# Removes self from the node's copy of the corp
		self.corp.remove_member(self)
		self.delete()

	def action(self, key_pressed: str, shift_status: bool):
		direction_keys = ['w', 'a', 's', 'd']
		primary_modifier_keys = {
			'k': "for attacking/killing",
			'm': "for moving",
			'l': "for looting",
			'i': "for inviting corp to merge into current corp",
			'-': "for setting a corp to a lower standing (A -> N -> E)",
			'+': "for setting a corp to a higher standing (E -> N -> A)",
			'b': "Build mode",
			'u': "for using something in your corp inventory",
			'c': "Cancel a corp owned building's existence"
		}
		secondary_modifier_keys = {
			'0': "",
			'1': "",
			'2': "",
			'3': "",
			'4': "",
			'5': "",
			'6': "",
			'7': "",
			'8': "",
			'9': ""
		}

		self.dir_key = ''

		self.shiftKeyActive = shift_status

		if key_pressed in direction_keys:
			self.dir_key = key_pressed
			return self.tick_if_allowed()
		elif key_pressed in primary_modifier_keys:
			self.primary_modifier_key = key_pressed
			return self.tick_if_allowed()
		elif key_pressed in secondary_modifier_keys:
			self.secondary_modifier_key = key_pressed
			return self.tick_if_allowed()

	def tick_if_allowed(self):
		if self.world.world_age > self.last_action_at_world_age:
			self.tick()
			return True
		return False

	def line_of_stats(self):
		los = '[hp {health}/{health_cap} ap {ap}] [ore {ore} om {mm}] [{pri_mod_key} {sec_mod_key}] [{world_age}] '.format(
			health=int(self.health),
			health_cap=int(self.health_cap),
			ap=int(self.attack_power),
			ore=int(self.corp.ore_quantity),
			mm=round(self.ore_multiplier, 1),
			pri_mod_key=self.primary_modifier_key,
			sec_mod_key=self.secondary_modifier_key,
			world_age=self.world.world_age)
		return los.ljust(self.world.cols)

	def get_vitals(self):
		response = {
			'ore_quantity': int(self.corp.ore_quantity),
			'ore_multiplier': round(self.ore_multiplier, 1),
			'delta_ore': self.delta_ore,
			'health': round(self.health, 1),
			'health_cap': round(self.health_cap, 1),
			'attack_power': round(self.attack_power, 1),
			'world_age': self.world.world_age,
			'row': self.row,
			'col': self.col,
			'modifier_key': self.primary_modifier_key,
			'secondary_modifier_key': self.secondary_modifier_key
		}
		return response

	def tick(self):
		self.last_action_at_world_age = self.world.world_age
		ore_before_tick = int(self.corp.ore_quantity)  # Used for calculating delta-ore
		# Interaction with cells
		if self.dir_key == 'w':
			self.interact_with_cell(-1, 0)
		elif self.dir_key == 's':
			self.interact_with_cell(1, 0)
		elif self.dir_key == 'a':
			self.interact_with_cell(0, -1)
		elif self.dir_key == 'd':
			self.interact_with_cell(0, 1)
		self.delta_ore = int(self.corp.ore_quantity - ore_before_tick)
		self.dir_key = ''  # Resets the direction key
		self.health_decay()

	def health_decay(self):
		self.health -= self.health_loss_per_turn
		if self.check_if_dead():
			self.died()

	def interact_with_cell(self, row_offset, col_offset):
		try:
			affected_cell = self.cell.get_cell_by_offset(row_offset, col_offset)
			# TODO: Turn this into a dict
			if self.primary_modifier_key == 'm':  # Player is trying to move
				try:
					self.move(affected_cell)
					if self.shiftKeyActive:
						try:
							new_cell = self.cell.get_cell_by_offset(row_offset, col_offset)
							self.move(new_cell)
							return True
						except (exceptions.CellCoordinatesOutOfBoundsError,
								exceptions.CellCannotBeEnteredException):
							pass
				except exceptions.CellCannotBeEnteredException:
					pass
				return False
			elif self.primary_modifier_key == 'k':  # Player is trying to attack something
				return self.attack(affected_cell)
			elif self.primary_modifier_key == 'l':  # Player is trying to collect/loot something
				try:
					if self.mine(affected_cell):
						return True
				except:
					pass

				try:
					self.utilize_hospital(affected_cell)
					return True
				except (exceptions.NoHospitalFoundException, exceptions.CellIsNoneException,
						exceptions.CorporationHasInsufficientFundsException):
					pass

				try:
					if self.loot(affected_cell):
						return True
				except:
					pass

				try:
					self.buy_from_pharmacy(affected_cell)
					return True
				except (exceptions.CellIsNoneException, exceptions.NoPharmacyFoundException):
					pass

				try:
					self.activate_star_gate(affected_cell)
					return True
				except exceptions.NoStarGatePresentException:
					pass

				return False

			elif self.primary_modifier_key == 'i':  # Player/Corp is trying to merge corps with another player
				try:
					self.action_handler_merge_request(affected_cell)
					return True
				except (exceptions.NoPlayerFoundException, exceptions.CellIsNoneException):
					return False
			elif self.primary_modifier_key == 'b':  # Player is in build mode
				if self.secondary_modifier_key == '1':  # Player is trying to build a fence
					try:
						self.construct_fence(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException) as e:
						repr(e)
						return False
				elif self.secondary_modifier_key == '2':  # Player is trying to build a hospital
					try:
						self.construct_hospital(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException) as e:
						repr(e)
						return False
				elif self.secondary_modifier_key == '3':  # Player is trying to build an Ore Generator
					try:
						self.construct_ore_generator(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException,
							exceptions.CellIsNotAdjacentToOreDepositException) as e:
						repr(e)
						return False
				elif self.secondary_modifier_key == '4':  # Player is trying to build a Pharmacy
					try:
						self.construct_pharmacy(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException,
							exceptions.CellIsNotAdjacentToOreDepositException) as e:
						repr(e)
						return False
				elif self.secondary_modifier_key == '5':  # Player is trying to build a door
					try:
						self.construct_door(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException) as e:
						repr(e)
						return False
				elif self.secondary_modifier_key == '6':
					try:
						self.construct_respawn_beacon(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException) as e:
						repr(e)
						return False
				elif self.secondary_modifier_key == '7':
					try:
						self.construct_sentry_turret(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException) as e:
						repr(e)
						return False
				elif self.secondary_modifier_key == '8':
					try:
						#self.construct_spike_trap(affected_cell)
						return True
					except (exceptions.CellCannotBeEnteredException,
							exceptions.CorporationHasInsufficientFundsException) as e:
						repr(e)
						return False
				else:
					return False
			elif self.primary_modifier_key == '-':  # Player is trying to worsen their standings towards the target player's corp
				try:
					self.worsen_standing_towards_targets_corp(affected_cell)
				except exceptions.CellIsNoneException:
					pass
				except exceptions.NoPlayerFoundException:
					pass
			elif self.primary_modifier_key == '+':
				# Player is trying to improve their standings towards the target player's corp
				try:
					self.improve_standing_towards_targets_corp(affected_cell)
				except exceptions.CellIsNoneException:
					pass
				except exceptions.NoPlayerFoundException:
					pass
			elif self.primary_modifier_key == 'u':  # Player is trying to use something in their corp inventory
				return self.try_using_inventory()
			elif self.primary_modifier_key == 'c':  # Player is trying to cancel a building's existence
				try:
					self.deconstruct(affected_cell)
					return True
				except exceptions.CellIsNoneException as e:
					repr(e)
					return False
			else:
				return False
		except exceptions.CellCoordinatesOutOfBoundsError:
			return False

	def activate_star_gate(self, _cell):
		if _cell is not None:
			try:
				stargate_id = _cell.get_object_id_of_first_object_found('StarGate')  # type: str
				stargate_obj = _cell.get_object_by_obj_id(stargate_id)  # type: gameObject.StarGate
				stargate_obj.use(self)
			except (exceptions.NoGameObjectOfThatClassFoundException,
					exceptions.NoGameObjectByThatObjectIDFoundException):
				raise exceptions.NoStarGatePresentException()
		else:
			raise exceptions.CellIsNoneException()

	def deconstruct(self, _cell: 'cell.Cell') -> None:
		if _cell is not None:
			_cell.deconstruct_first_possible_building_owned_by_corp(self.corp)
		else:
			raise exceptions.CellIsNoneException()

	def try_using_inventory(self):
		chosen_potion = self.corp.return_obj_selected_in_rendered_inventory(int(self.secondary_modifier_key))
		#  Consumables
		if chosen_potion is None:
			return False
		else:
			chosen_potion = chosen_potion()

		if chosen_potion.item_type == 'Consumable':
			potion_name = chosen_potion.__class__.__name__
			self.corp.queue_inventory_delta(potion_name, -1)
			self.potions_taken[potion_name] = {
				'taken': self.potions_taken.get(potion_name, {}).get('taken', 0) + 1,
				'applied': self.potions_taken.get(potion_name, {}).get('applied', 0),
				'effects': chosen_potion.effects
			}
			self.recalculate_potion_effects()
			return True
		else:
			return False  # Not yet supported

	def recalculate_potion_effects(self):
		deltas = {
			'Health Delta': 0,
			'Ore Delta': 0,
			'Ore Multiplier Delta': 0,
			'Health Cap Delta': 0,
			'Attack Power Delta': 0
		}

		for potion_name, values in self.potions_taken.items():
			if values.get('taken', 0) > 0:

				effects = values.get('effects', {})

				# Instant Bonuses
				if values.get('taken', 0) > values.get('applied', 0):
					# Health Delta
					deltas['Health Delta'] = deltas.get('Health Delta', 0) + effects.get('Health Delta', 0)

					# Ore Gain/Lose
					deltas['Ore Delta'] = deltas.get('Ore Delta', 0) + effects.get('Ore Delta', 0)

					# Now that we've applied the instant bonuses, we can increase the applied value.
					values['applied'] = values.get('applied', 0) + 1

				### Now we can apply the multipliers ###

				# Ore Multiplier #
				deltas['Ore Multiplier Delta'] = deltas.get('Ore Multiplier Delta', 0) + (
					effects.get('Ore Multiplier Delta', 0) * (
						1 + math.log(values.get('taken', 0), 2)
					)
				)

				# Health Cap #
				deltas['Health Cap Delta'] = deltas.get('Health Cap Delta', 0) + (
					effects.get('Health Cap Delta', 0) * (
						1 + math.log(values.get('taken', 0), 2)
					)
				)

				# Attack Power #
				deltas['Attack Power Delta'] = deltas.get('Attack Power Delta', 0) + (
					effects.get('Attack Power Delta', 0) * (
						1 + math.log(values.get('taken', 0), 2)
					)
				)
			else:
				continue

		if deltas.get('Health Delta', 0) > 0:
			self.gain_health(deltas.get('Health Delta', 0))
		elif deltas.get('Health Delta', 0) < 0:
			self.take_damage(deltas.get('Health Delta', 0))

		self.gain_ore(deltas.get('Ore Delta', 0))

		self.ore_multiplier = self.starting_ore_multiplier + deltas.get('Ore Multiplier Delta', 0)

		self.health_cap = self.starting_health_cap + deltas.get('Health Cap Delta', 0)

		self.attack_power = self.starting_attack_power + deltas.get('Attack Power Delta', 0)

	def gain_health(self, amount):
		self.health = min(self.health_cap, self.health + amount)

	def construct_sentry_turret(self, _cell: 'Cell') -> None:
		if _cell.can_build() and _cell.is_adjacent_to_game_object('SentryTurret',
																				 check_diagonally=True,
																				 check_horizontally=True,
																				 check_vertically=True,
																				 check_self=True) is False:
			ore_cost = gameObject.SentryTurret.construction_cost
			if self.corp.ore_quantity >= ore_cost:
				_cell.add_corp_owned_building(self.corp, 'SentryTurret')
				self.lose_ore(ore_cost)
				self.world.logger.log("{player} Spent {cost} to build a Sentry Turret".format(player=self.username, cost=ore_cost), 2)
			else:
				raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def construct_spike_trap(self, _cell: 'Cell') -> None:
		if _cell.can_build():
			ore_cost = gameObject.SpikeTrap.construction_cost
			if self.corp.ore_quantity >= ore_cost:
				_cell.add_corp_owned_building(self.corp, 'SpikeTrap')
				self.lose_ore(ore_cost)
				self.world.logger.log("{player} Spent {cost} to build a Spike Trap".format(player=self.username, cost=ore_cost), 2)
			else:
				raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def construct_pharmacy(self, _cell: 'Cell') -> None:
		if _cell.can_build():
			ore_cost = gameObject.Pharmacy.construction_cost
			if self.corp.ore_quantity >= ore_cost:
				_cell.add_corp_owned_building(self.corp, 'Pharmacy')
				self.lose_ore(ore_cost)
				self.world.logger.log("{player} Spent {cost} to build a Pharmacy".format(player=self.username, cost=ore_cost), 2)
			else:
				raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def construct_respawn_beacon(self, _cell: 'Cell') -> None:
		if _cell.can_build():
			ore_cost = gameObject.RespawnBeacon.construction_cost
			if self.corp.ore_quantity >= ore_cost:
				_cell.add_corp_owned_building(self.corp, 'RespawnBeacon')
				self.lose_ore(ore_cost)
				self.world.logger.log("{player} Spent {cost} to build a Respawn Beacon".format(player=self.username, cost=ore_cost), 2)
			else:
				raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def construct_door(self, _cell: 'Cell') -> None:
		if _cell.can_build():
			ore_cost = gameObject.Door.construction_cost
			if self.corp.ore_quantity >= ore_cost:
				_cell.add_corp_owned_building(self.corp, 'Door')
				self.lose_ore(ore_cost)
				self.world.logger.log("{player} Spent {cost} to build a Door".format(player=self.username, cost=ore_cost), 2)
			else:
				raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def construct_ore_generator(self, _cell: 'Cell') -> None:
		if _cell.can_build():
			if _cell.is_adjacent_to_game_object('OreDeposit', check_diagonally=True, check_horizontally=True,
												check_vertically=True):
				ore_cost = gameObject.OreGenerator.construction_cost
				if self.corp.ore_quantity >= ore_cost:
					_cell.add_corp_owned_building(self.corp, 'OreGenerator')
					self.lose_ore(ore_cost)
					self.world.logger.log("{player} Spent {cost} to build an Ore Generator".format(player=self.username, cost=ore_cost), 2)
				else:
					raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
			else:
				raise exceptions.CellIsNotAdjacentToOreDepositException()
		else:
			raise exceptions.CellCannotBeEnteredException()

	def construct_hospital(self, _cell: 'Cell') -> None:
		if _cell.can_build():
			ore_cost = gameObject.Hospital.construction_cost
			if self.corp.ore_quantity >= ore_cost:
				_cell.add_corp_owned_building(self.corp, 'Hospital')
				self.lose_ore(ore_cost)
				self.world.logger.log("{player} Spent {cost} to build a Hospital".format(player=self.username, cost=ore_cost), 2)
			else:
				raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def construct_fence(self, _cell: 'Cell') -> None:
		if _cell.can_build():
			ore_cost = gameObject.Fence.construction_cost
			if self.corp.ore_quantity >= ore_cost:
				_cell.add_corp_owned_building(self.corp, 'Fence')
				self.lose_ore(ore_cost)
				self.world.logger.log("{player} Spent {cost} to build a Fence".format(player=self.username, cost=ore_cost), 2)
			else:
				raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def action_handler_merge_request(self, _cell) -> None:
		# If you have a better name, please do share.
		if _cell is not None:
			try:
				target_player_id = _cell.get_object_id_of_first_object_found('Player')
				target_player = _cell.get_object_by_obj_id(target_player_id)  # type: Player
				target_player_corp_id = target_player.corp.corp_id
				self.corp.send_merge_invite(target_player_corp_id)
			except exceptions.NoPlayerFoundException:
				raise exceptions.NoPlayerFoundException()
			except exceptions.NoGameObjectByThatObjectIDFoundException:
				raise exceptions.NoPlayerFoundException()
		else:
			raise exceptions.CellIsNoneException()

	def receive_merge_invite(self, corp_id):
		self.corp.receive_merge_invite(corp_id)

	def loot(self, _cell):
		try:
			target_id = _cell.get_object_id_of_first_object_found('Loot')
			target = _cell.get_object_by_obj_id(target_id)
			self.gain_ore(target.ore_quantity)
			self.world.logger.log('{player} looted {amount} Ore'.format(player=self.username,
																		amount=target.ore_quantity), 3)
			target.delete()
			return True
		except (exceptions.NoGameObjectOfThatClassFoundException,
				exceptions.NoGameObjectByThatObjectIDFoundException):
			return False

	def mine(self, _cell):
		try:
			target_id = _cell.get_object_id_of_first_object_found('OreDeposit')
			target = _cell.get_object_by_obj_id(target_id)  # type: gameObject.OreDeposit
			ore_quantity = target.ore_per_turn * self.ore_multiplier
			target.extract_ore(ore_quantity)
			self.gain_ore(ore_quantity)
			self.world.logger.log('{} mined {} Ore'.format(self.username, ore_quantity), 3)
			return True
		except (exceptions.NoGameObjectOfThatClassFoundException,
				exceptions.NoGameObjectByThatObjectIDFoundException):
			return False

	def worsen_standing_towards_targets_corp(self, _cell) -> None:
		if _cell is not None:
			try:
				target_player_id = _cell.get_object_id_of_first_object_found('Player')
				target_player = _cell.get_object_by_obj_id(target_player_id)  # type: Player
				target_player_corp_id = target_player.corp.corp_id
				self.corp.worsen_standing(target_player_corp_id)
			except (exceptions.NoPlayerFoundException, exceptions.NoGameObjectByThatObjectIDFoundException):
				raise exceptions.NoPlayerFoundException()
		else:
			raise exceptions.CellIsNoneException()

	def improve_standing_towards_targets_corp(self, _cell) -> None:
		if _cell is not None:
			try:
				target_player_id = _cell.get_object_id_of_first_object_found('Player')
				target_player = _cell.get_object_by_obj_id(target_player_id)  # type: Player
				target_player_corp_id = target_player.corp.corp_id
				self.corp.improve_standing(target_player_corp_id)
			except (exceptions.NoPlayerFoundException, exceptions.NoGameObjectByThatObjectIDFoundException):
				raise exceptions.NoPlayerFoundException()
		else:
			raise exceptions.CellIsNoneException()

	def attack(self, _cell):
		try:
			target_player_id = _cell.get_object_id_of_first_object_found('Player')
			target_player = _cell.get_object_by_obj_id(target_player_id)  # type: Player
			standing_to_target_player = self.corp.fetch_standing(target_player.corp.corp_id)
			if standing_to_target_player in ['N', 'E']:
				# You can attack a Neutral or Enemy
				target_player.take_damage(self.attack_power)
				self.world.logger.log('{attacker} attacked {defender} for {damage_amount} damage'.format(attacker=self.username,
																										 defender=target_player.username,
																										 damage_amount=self.attack_power))
				target_player.corp.worsen_standing(self.corp.corp_id)
				self.corp.worsen_standing(target_player.corp.corp_id)
				return True
			else:
				# You cannot attack a Corporation Member, or an Ally
				return False
		except (exceptions.NoGameObjectOfThatClassFoundException, exceptions.NoGameObjectByThatObjectIDFoundException):
			pass

		game_object_class_names = ['Fence', 'Hospital', 'OreGenerator', 'Pharmacy',
								   'Door', 'SentryTurret', 'SpikeTrap', 'RespawnBeacon']

		for game_object_class_name in game_object_class_names:
			try:
				target_id = _cell.get_object_id_of_first_object_found(game_object_class_name)
				target = _cell.get_object_by_obj_id(target_id)
			except (exceptions.NoGameObjectOfThatClassFoundException,
					exceptions.NoGameObjectByThatObjectIDFoundException):
				pass
			else:
				standing_towards_target = self.corp.fetch_standing(target.owner_corp.corp_id)
				if standing_towards_target in ['N', 'E']:
					target.take_damage(self.attack_power, self.corp)
					return True
				else:
					return False
		return False

	def gain_ore(self, amount: float) -> None:
		self.corp.gain_ore(amount)

	def lose_ore(self, amount: float) -> None:
		self.world.logger.log('{player} spent/lost {amount} Ore'.format(player=self.username, amount=amount), 2)
		self.corp.lose_ore(amount)

	def drop_ore(self):
		loot_object = gameObject.Loot(self.cell)

		ore_loss = self.corp.calculate_ore_loss_on_death()

		loot_object.ore_quantity = ore_loss
		self.lose_ore(ore_loss)

		self.cell.add_game_object(loot_object)
		if self.corp.ore_quantity < 100:
			self.gain_ore(100 - self.corp.ore_quantity)

	def take_damage(self, damage):
		self.health -= damage
		if self.check_if_dead():
			self.died()

	def buy_from_pharmacy(self, _cell):
		if _cell is not None:
			try:
				pharmacy_id = _cell.get_object_id_of_first_object_found('Pharmacy')
				pharmacy = _cell.get_object_by_obj_id(pharmacy_id)  # type: gameObject.Pharmacy

				if int(self.secondary_modifier_key) == 0:
					item_num = 9
				else:
					item_num = int(self.secondary_modifier_key) - 1
				pharmacy.buy_item(self.corp, item_num)
			except (exceptions.NoGameObjectOfThatClassFoundException,
					exceptions.NoGameObjectByThatObjectIDFoundException):
				raise exceptions.NoPharmacyFoundException()
		else:
			raise exceptions.CellIsNoneException()

	def utilize_hospital(self, _cell):
		if _cell is not None:
			try:
				hospital_id = _cell.get_object_id_of_first_object_found('Hospital')
				hospital = _cell.get_object_by_obj_id(hospital_id)  # type: gameObject.Hospital
				hospital_owner_corp = hospital.owner_corp
				owner_standings_towards_us = hospital_owner_corp.fetch_standing(self.corp.corp_id)
				price_to_use_hospital = hospital.prices_to_use.get(owner_standings_towards_us, 0)
				profit_for_owners = hospital.profits_per_use.get(owner_standings_towards_us, 0)

				if self.corp.ore_quantity >= price_to_use_hospital:
					# Healing
					self.health = min(self.health + hospital.health_regen_per_turn, self.health_cap)
					# Pay
					self.lose_ore(price_to_use_hospital)
					# Profit
					hospital.give_profit_to_owners(profit_for_owners)

					self.world.logger.log('{player} used a hospital owned by {owners}'.format(
						player=self.username,
						owners=hospital_owner_corp.corp_id
					), 2)
				else:
					raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
			except (exceptions.NoGameObjectOfThatClassFoundException,
					exceptions.NoGameObjectByThatObjectIDFoundException):
				raise exceptions.NoHospitalFoundException()
		else:
			raise exceptions.CellIsNoneException()

	def move(self, _cell: 'cell.Cell') -> None:
		if _cell.can_enter(player_obj=self):
			self.change_cell(_cell)
		else:
			raise exceptions.CellCannotBeEnteredException()

	def check_if_dead(self):
		return self.health <= 0

	def died(self):
		if self.health <= 0:
			self.world.logger.log('{} died'.format(self.username), 4)
			self.drop_ore()
			self.health = int(self.starting_health)
			self.ore_multiplier = float(self.starting_ore_multiplier)
			self.attack_power = int(self.starting_attack_power)
			self.health_cap = int(self.starting_health_cap)
			self.go_to_respawn_location()
			self.primary_modifier_key = 'm'

	def go_to_respawn_location(self):
		self.change_cell(self.corp.get_respawn_cell())
