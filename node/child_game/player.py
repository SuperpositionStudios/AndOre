import uuid, random
from child_game import gameObject, corporation, cell
import child_game
from child_game import exceptions
import math


class Player(gameObject.GameObject):
    def __init__(self, _id: str, _world: 'child_game.world.World', _cell: 'cell.Cell', _corp: 'corporation.Corporation'):
        super().__init__(_cell)
        assert (_world is not None)
        assert (_corp is not None)

        self.id = _id
        self.aid = self.id
        self.obj_id = _id
        self.world = _world
        self.cell = _cell

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

    def action(self, key_pressed):
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

        if key_pressed == 'shiftDown':
            self.shiftKeyActive = True
        elif key_pressed == 'shiftUp':
            self.shiftKeyActive = False
        elif key_pressed in direction_keys:
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
            'ore_quantity': int(self.corp.amount_of_ore()),
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
        ore_before_tick = int(self.corp.amount_of_ore())  # Used for calculating delta-ore
        # Interaction with cells
        if self.dir_key == 'w':
            self.interact_with_cell(-1, 0)
        elif self.dir_key == 's':
            self.interact_with_cell(1, 0)
        elif self.dir_key == 'a':
            self.interact_with_cell(0, -1)
        elif self.dir_key == 'd':
            self.interact_with_cell(0, 1)
        self.delta_ore = int(self.corp.amount_of_ore() - ore_before_tick)
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
                if self.mine(affected_cell):
                    return True
                elif self.try_going_to_hospital(affected_cell):
                    return True
                elif self.loot(affected_cell):
                    return True
                elif self.try_buying_from_pharmacy(affected_cell):
                    return True
                elif self.try_activating_star_gate(affected_cell):
                    return True
                else:
                    return False
            elif self.primary_modifier_key == 'i':  # Player/Corp is trying to merge corps with another player
                if self.try_merge_corp(affected_cell):
                    return True
                else:
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
                        self.construct_spike_trap(affected_cell)
                        return True
                    except (exceptions.CellCannotBeEnteredException,
                            exceptions.CorporationHasInsufficientFundsException) as e:
                        repr(e)
                        return False
                else:
                    return False
            elif self.primary_modifier_key == '-':  # Player is trying to worsen their standings towards the target player's corp
                return self.try_worsening_standing(affected_cell)
            elif self.primary_modifier_key == '+':  # Player is trying to improve their standings towards the target player's corp
                return self.try_improving_standing(affected_cell)
            elif self.primary_modifier_key == 'u':  # Player is trying to use something in their corp inventory
                return self.try_using_inventory()
            elif self.primary_modifier_key == 'c':  # Player is trying to cancel a building's existence
                return self.try_deconstructing(affected_cell)
            else:
                return False
        except exceptions.CellCoordinatesOutOfBoundsError:
            return False

    def try_activating_star_gate(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('StarGate')
            if struct[0]:
                obj = _cell.get_game_object_by_obj_id(struct[1])
                if obj[0]:
                    obj[1].use(self)
                    return True
        return False

    def try_deconstructing(self, _cell):
        if _cell is not None:
            _cell.deconstruct_first_possible_building_owned_by_corp(self.corp.corp_id)

    def try_using_inventory(self):
        #  Consumables
        chosen_potion = self.corp.return_obj_selected_in_rendered_inventory(int(self.secondary_modifier_key))
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
        if _cell.can_enter(player_obj=self):
            ore_cost = gameObject.SentryTurret.construction_cost
            if self.corp.amount_of_ore() >= ore_cost:
                _cell.add_corp_owned_building(self.corp, 'SentryTurret')
                self.lose_ore(ore_cost)
            else:
                raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def construct_spike_trap(self, _cell: 'Cell') -> None:
        if _cell.can_enter(player_obj=self):
            ore_cost = gameObject.SpikeTrap.construction_cost
            if self.corp.amount_of_ore() >= ore_cost:
                _cell.add_corp_owned_building(self.corp, 'SpikeTrap')
                self.lose_ore(ore_cost)
            else:
                raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def construct_pharmacy(self, _cell: 'Cell') -> None:
        if _cell.can_enter(player_obj=self):
            ore_cost = gameObject.Pharmacy.construction_cost
            if self.corp.amount_of_ore() >= ore_cost:
                _cell.add_corp_owned_building(self.corp, 'Pharmacy')
                self.lose_ore(ore_cost)
            else:
                raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def construct_respawn_beacon(self, _cell: 'Cell') -> None:
        if _cell.can_enter(player_obj=self):
            ore_cost = gameObject.RespawnBeacon.construction_cost
            if self.corp.amount_of_ore() >= ore_cost:
                _cell.add_corp_owned_building(self.corp, 'RespawnBeacon')
                self.lose_ore(ore_cost)
            else:
                raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def construct_door(self, _cell: 'Cell') -> None:
        if _cell.can_enter(player_obj=self):
            ore_cost = gameObject.Door.construction_cost
            if self.corp.amount_of_ore() >= ore_cost:
                _cell.add_corp_owned_building(self.corp, 'Door')
                self.lose_ore(ore_cost)
            else:
                raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def construct_ore_generator(self, _cell: 'Cell') -> None:
        if _cell.can_enter(player_obj=self):
            if _cell.next_to_ore_deposit():
                ore_cost = gameObject.OreGenerator.construction_cost
                if self.corp.amount_of_ore() >= ore_cost:
                    _cell.add_corp_owned_building(self.corp, 'OreGenerator')
                    self.lose_ore(ore_cost)
                else:
                    raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
            else:
                raise exceptions.CellIsNotAdjacentToOreDepositException()
        else:
            raise exceptions.CellCannotBeEnteredException()

    def construct_hospital(self, _cell: 'Cell') -> None:
        if _cell.can_enter(player_obj=self):
            ore_cost = gameObject.Hospital.construction_cost
            if self.corp.amount_of_ore() >= ore_cost:
                _cell.add_corp_owned_building(self.corp, 'Hospital')
                self.lose_ore(ore_cost)
            else:
                raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def construct_fence(self, _cell: 'Cell') -> None:
        if _cell.can_enter(player_obj=self):
            ore_cost = gameObject.Fence.construction_cost
            if self.corp.amount_of_ore() >= ore_cost:
                _cell.add_corp_owned_building(self.corp, 'Fence')
                self.lose_ore(ore_cost)
            else:
                raise exceptions.CorporationHasInsufficientFundsException(self.corp.corp_id)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def try_merge_corp(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Player')
            if struct[0]:
                other_player = _cell.get_game_object_by_obj_id(struct[1])
                if other_player[0]:
                    other_player_corp_id = other_player[1].get_corp_id()
                    self.send_merge_invite(other_player_corp_id)
                    return True
        return False

    def get_corp_id(self):
        return self.corp.corp_id

    def send_merge_invite(self, corp_id):
        self.corp.send_merge_invite(corp_id)

    def receive_merge_invite(self, corp_id):
        self.corp.receive_merge_invite(corp_id)

    def loot(self, _cell):
        try:
            target_id = _cell.get_object_id_of_first_game_object_found('Loot')
            target = _cell.new_get_game_object_by_obj_id(target_id)
            self.gain_ore(target.ore_quantity)
            target.delete()
            return True
        except (exceptions.NoGameObjectOfThatClassFoundException,
                exceptions.NoGameObjectByThatObjectIDFoundException):
            return False

    def mine(self, _cell):
        try:
            target_id = _cell.get_object_id_of_first_game_object_found('OreDeposit')
            target = _cell.new_get_game_object_by_obj_id(target_id)
            self.gain_ore(target.ore_per_turn * self.ore_multiplier)
            return True
        except (exceptions.NoGameObjectOfThatClassFoundException,
                exceptions.NoGameObjectByThatObjectIDFoundException):
            return False

    def try_worsening_standing(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Player')
            if struct[0]:
                other_player = _cell.get_game_object_by_obj_id(struct[1])
                if other_player[0]:
                    self.corp.worsen_standing(other_player[1].corp.corp_id)
                    return True
        else:
            return False

    def try_improving_standing(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Player')
            if struct[0]:
                other_player = _cell.get_game_object_by_obj_id(struct[1])
                if other_player[0]:
                    self.corp.improve_standing(other_player[1].corp.corp_id)
                    return True
        else:
            return False

    def attack(self, _cell):
        try:
            target_player_id = _cell.get_object_id_of_first_game_object_found('Player')
            target_player = _cell.new_get_game_object_by_obj_id(target_player_id)
            standing_to_target_player = self.corp.fetch_standing(target_player.corp.corp_id)
            if standing_to_target_player in ['N', 'E']:
                # You can attack a Neutral or Enemy
                target_player.take_damage(self.attack_power)
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
                target_id = _cell.get_object_id_of_first_game_object_found(game_object_class_name)
                target = _cell.new_get_game_object_by_obj_id(target_id)
                standing_towards_target = self.corp.fetch_standing(target.owner_corp.corp_id)
                if standing_towards_target in ['N', 'E']:
                    target.take_damage(self.attack_power, self.corp)
                    return True
                else:
                    return False
            except (exceptions.NoGameObjectOfThatClassFoundException,
                    exceptions.NoGameObjectByThatObjectIDFoundException):
                pass

        return False

    def gain_ore(self, amount: float) -> None:
        self.corp.gain_ore(amount)

    def lose_ore(self, amount: float) -> None:
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

    def try_buying_from_pharmacy(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Pharmacy')
            if struct[0]:
                pharmacy = _cell.get_game_object_by_obj_id(struct[1])
                if pharmacy[0]:
                    pharmacy_obj = pharmacy[1]
                    assert(pharmacy_obj.__class__.__name__ == 'Pharmacy')
                    if int(self.secondary_modifier_key) == 0:
                        item_num = 9
                    else:
                        item_num = int(self.secondary_modifier_key) - 1
                    return pharmacy_obj.buy_item(self.corp, item_num)

    def try_going_to_hospital(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Hospital')
            if struct[0]:
                hospital = _cell.get_game_object_by_obj_id(struct[1])
                if hospital[0]:
                    hospital_obj = hospital[1]
                    assert (hospital_obj.__class__.__name__ == 'Hospital')
                    hospital_owners = hospital_obj.owner_corp
                    owner_standings_towards_us = hospital_owners.fetch_standing_for_player(self.obj_id)
                    price_to_use_hospital = hospital_obj.prices_to_use[owner_standings_towards_us]
                    owners_profit = hospital_obj.profits_per_use[owner_standings_towards_us]

                    if self.corp.amount_of_ore() >= price_to_use_hospital:
                        self.health = min(self.health + hospital_obj.health_regen_per_turn, self.health_cap)
                        # Pay for using hospital
                        self.lose_ore(price_to_use_hospital)
                        # Hospital owners profit
                        hospital_obj.give_profit_to_owners(owner_standings_towards_us)
                        return True
        return False

    def move(self, _cell: 'cell.Cell') -> None:
        if _cell.can_enter(player_obj=self):
            self.change_cell(_cell)
        else:
            raise exceptions.CellCannotBeEnteredException()

    def check_if_dead(self):
        return self.health <= 0

    def died(self):
        if self.health <= 0:
            self.drop_ore()
            self.health = int(self.starting_health)
            self.ore_multiplier = float(self.starting_ore_multiplier)
            self.attack_power = int(self.starting_attack_power)
            self.health_cap = int(self.starting_health_cap)
            self.go_to_respawn_location()
            self.primary_modifier_key = 'm'

    def go_to_respawn_location(self):
        self.change_cell(self.corp.get_respawn_cell())
