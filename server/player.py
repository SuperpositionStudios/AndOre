import uuid, random
from cell import Cell
import gameObject
import corporation


class Player(gameObject.GameObject):
    def __init__(self, _id, _world, _cell):
        super().__init__(_cell)
        assert (_world is not None)

        self.id = _id
        self.obj_id = _id
        self.world = _world
        self.cell = _cell
        self.starting_health = 100
        self.health_cap = 100
        self.health_loss_per_turn = 0.1
        self.health = 100
        self.attack_power = 10
        self.delta_ore = 0  # The ore lost/gained in the last tick
        self.inner_icon = '@'
        self.neutral_icon = 'N'
        self.enemy_icon = 'E'
        self.ally_icon = 'A'
        self.corp_member_icon = 'M'
        self.icon = '!'
        self.row = self.cell.row
        self.col = self.cell.col
        self.dir_key = ''
        self.modifier_key = 'm'
        self.passable = False
        self.last_action_at_world_age = 0
        self.corp = self.world.new_corporation(self)

    def action(self, key_pressed):
        direction_keys = ['w', 'a', 's', 'd']
        modifier_keys = {
            'k': "for attacking/killing",
            'm': "for moving",
            'l': "for looting",
            'i': "for inviting corp to merge into current corp",
            '-': "for setting a corp to a lower standing (A -> N -> E)",
            '+': "for setting a corp to a higher standing (E -> N -> A)",
            'f': "for building a fence"
        }
        if key_pressed in direction_keys:
            self.dir_key = key_pressed
        else:
            self.dir_key = ''
            self.modifier_key = key_pressed
        if self.world.world_age > self.last_action_at_world_age:
            self.tick()

    def line_of_stats(self):
        return '[hp {health} ore {ore}] [{row} {col}] [{mod_key}][{world_age}] '.format(health=int(self.health),
                                                                                       ore=self.corp.ore_quantity,
                                                                                       row=self.row,
                                                                                       col=self.col,
                                                                                       mod_key=self.modifier_key,
                                                                                       world_age=self.world.world_age)

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
        affected_cell = self.try_get_cell_by_offset(row_offset, col_offset)
        if affected_cell is not None and affected_cell is not False:
            if self.modifier_key == 'm':  # Player is trying to move
                return self.try_move(affected_cell)
            elif self.modifier_key == 'k':  # Player is trying to attack something
                return self.try_attacking(affected_cell)
            elif self.modifier_key == 'l':  # Player is trying to collect/loot something
                if self.try_mining(affected_cell):
                    return True
                elif self.try_going_to_hospital(affected_cell):
                    return True
                elif self.try_looting(affected_cell):
                    return True
                else:
                    return False
            elif self.modifier_key == 'i':  # Player/Corp is trying to merge corps with another player
                if self.try_merge_corp(affected_cell):
                    return True
                else:
                    return False
            elif self.modifier_key == 'f':  # Player is trying to build a fence
                if self.try_building_fence(affected_cell):
                    return True
                else:
                    return False
            elif self.modifier_key == '-':  # Player is trying to worsen their standings towards the target player's corp
                if self.try_worsening_standing(affected_cell):
                    return True
                else:
                    return False
            elif self.modifier_key == '+':  # Player is trying to improve their standings towards the target player's corp
                if self.try_improving_standing(affected_cell):
                    return True
                else:
                    return False
            elif self.modifier_key == 'h':  # Player is trying to construct a hospital
                if self.try_building_hospital(affected_cell):
                    return True
                else:
                    return False
            elif self.modifier_key == 'g':  # Player is trying to construct an ore generator
                if self.try_building_ore_generator(affected_cell):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def try_building_ore_generator(self, _cell):
        if _cell is not None and _cell.can_enter():
            ore_cost = _cell.add_ore_generator(self.corp)
            if self.corp.amount_of_ore() > ore_cost:
                self.lose_ore(ore_cost)
                return True
            else:
                struct = _cell.contains_object_type('OreGenerator')
                if struct[0]:
                    ore_generator = _cell.get_game_object_by_obj_id(struct[1])
                    if ore_generator[0]:
                        ore_generator[1].delete()
                        return False

    def try_building_hospital(self, _cell):
        if _cell is not None and _cell.can_enter():
            ore_cost = _cell.add_hospital(self.corp)
            if self.corp.amount_of_ore() > ore_cost:
                self.lose_ore(ore_cost)
                return True
            else:
                struct = _cell.contains_object_type('Hospital')
                if struct[0]:
                    hospital = _cell.get_game_object_by_obj_id(struct[1])
                    if hospital[0]:
                        hospital[1].delete()
                        return False

    def try_building_fence(self, _cell):
        if _cell is not None and _cell.can_enter():
            ore_cost = _cell.add_fence()
            if self.corp.amount_of_ore() > ore_cost:
                self.lose_ore(ore_cost)
                return True
            else:
                struct = _cell.contains_object_type('Fence')
                if struct[0]:
                    fence = _cell.get_game_object_by_obj_id(struct[1])
                    if fence[0]:
                        fence[1].delete()
                        return False
        return False

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

    def try_looting(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Loot')
            if struct[0]:
                loot_object = _cell.get_game_object_by_obj_id(struct[1])
                if loot_object[0]:
                    self.gain_ore(loot_object[1].ore_quantity)
                    loot_object[1].delete()
                    return True
        return False

    def try_mining(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('OreDeposit')
            if struct[0]:
                ore_deposit = _cell.get_game_object_by_obj_id(struct[1])
                if ore_deposit[0]:
                    self.gain_ore(ore_deposit[1].ore_per_turn)
                    return True
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

    def try_attacking(self, _cell):
        if _cell is not None:
            if _cell.contains_object_type('Fence')[0]:
                struct = _cell.contains_object_type('Fence')
                fence = _cell.get_game_object_by_obj_id(struct[1])
                if fence[0]:
                    fence[1].take_damage(self.attack_power)
                    return True
            elif _cell.contains_object_type('Hospital')[0]:
                struct = _cell.contains_object_type('Hospital')
                hospital = _cell.get_game_object_by_obj_id(struct[1])
                if hospital[0]:
                    hospital_obj = hospital[1]
                    corp_standing_to_hospital_owner_corp = self.corp.fetch_standing(hospital_obj.owner_corp.corp_id)
                    if corp_standing_to_hospital_owner_corp == 'M' or corp_standing_to_hospital_owner_corp == 'A':
                        return False  # You cannot attack a hospital that is owned by a corp that we are friendly to
                    else:
                        hospital_obj.take_damage(self.attack_power, self.corp)
                        return True
            elif _cell.contains_object_type('OreGenerator'):
                struct = _cell.contains_object_type('OreGenerator')
                ore_generator = _cell.get_game_object_by_obj_id(struct[1])
                if ore_generator[0]:
                    ore_generator_obj = ore_generator[1]
                    corp_standing_to_ore_generator_owner_corp = self.corp.fetch_standing(ore_generator_obj.owner_corp.corp_id)
                    if corp_standing_to_ore_generator_owner_corp == 'M' or corp_standing_to_ore_generator_owner_corp == 'A':
                        return False  # You cannot attack an ore generator that is owned by a corp that we are friendly to
                    else:
                        ore_generator_obj.take_damage(self.attack_power, self.corp)
                        return True
            elif _cell.contains_object_type('Player')[0]:
                struct = _cell.contains_object_type('Player')
                other_player = _cell.get_game_object_by_obj_id(struct[1])
                if other_player[0]:
                    corp_standing_to_other_players_corp = self.corp.fetch_standing(other_player[1].corp.corp_id)
                    if self.corp.check_if_in_corp(struct[1]):
                        return False  # You cannot attack another player in your corp
                    elif corp_standing_to_other_players_corp == 'A':
                        return False  # You cannot attack members of corporations that your corporation considers allies
                    else:
                        # Attacking someone not in your corp
                        other_player[1].take_damage(self.attack_power)
                        # Worsening their corp's standings towards your corp
                        other_player[1].corp.worsen_standing(self.corp.corp_id)
                        # Worsening your corp's standings towards their corp
                        self.corp.worsen_standing(other_player[1].corp.corp_id)
                        return True
        return False

    def gain_ore(self, amount):
        self.corp.gain_ore(amount)

    def lose_ore(self, amount):
        self.corp.lose_ore(amount)

    def drop_ore(self):
        loot_object = gameObject.Loot(self.cell)

        ore_loss = self.corp.calculate_ore_loss_on_death()

        loot_object.ore_quantity = ore_loss
        self.lose_ore(ore_loss)

        self.cell.add_game_object(loot_object)

    def take_damage(self, damage):
        self.health -= damage
        if self.check_if_dead():
            self.died()

    def try_going_to_hospital(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Hospital')
            if struct[0]:
                hospital = _cell.get_game_object_by_obj_id(struct[1])
                if hospital[0]:
                    hospital_obj = hospital[1]
                    assert(hospital_obj.__class__.__name__ == 'Hospital')
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

    def try_move(self, _cell):
        if _cell is not None:
            if _cell.can_enter():
                self.change_cell(_cell)
                return True
            else:
                return False
        return False

    def try_get_cell_by_offset(self, row_offset, col_offset):
        fetched_cell = self.world.get_cell(self.row + row_offset, self.col + col_offset)
        if fetched_cell is False or fetched_cell is None:
            return False
        else:
            return fetched_cell

    def world_state(self):
        los = self.line_of_stats().ljust(self.world.rows)
        los = list(los)
        worldmap = self.world.get_world(player_id=self.id)
        worldmap.append(los)
        return worldmap

    def get_vitals(self):
        response = {
            'ore_quantity': self.corp.amount_of_ore(),
            'delta_ore': self.delta_ore,
            'health': self.health,
            'world_age': self.world.world_age
        }
        return response

    def check_if_dead(self):
        if self.health <= 0:
            return True
        else:
            return False

    def died(self):
        if self.health <= 0:
            self.drop_ore()
            self.health += self.starting_health
            self.go_to_respawn_location()

    def go_to_respawn_location(self):
        self.change_cell(self.world.random_can_enter_cell())
