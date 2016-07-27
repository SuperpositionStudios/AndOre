import uuid, random
from cell import Cell
import gameObject


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
        self.ore_quantity = 0
        self.delta_ore = self.ore_quantity  # The ore lost/gained in the last tick
        self.inner_icon = '@'
        self.icon = '!'
        self.row = self.cell.row
        self.col = self.cell.col
        self.next_action = ''
        self.passable = False
        self.last_action_at_world_age = 0

    def action(self, _dir):
        self.next_action = _dir
        if self.world.world_age > self.last_action_at_world_age:
            self.tick()

    def line_of_stats(self):
        return '[hp {health} ore {ore}] [{row} {col}] [{next_action}][{world_age}] '.format(health=int(self.health),
                                                                                       ore=self.ore_quantity,
                                                                                       row=self.row,
                                                                                       col=self.col,
                                                                                       next_action=self.next_action,
                                                                                       world_age=self.world.world_age)

    def tick(self):
        self.last_action_at_world_age = self.world.world_age
        ore_before_tick = int(self.ore_quantity)
        # Movement
        if self.next_action == 'w':
            self.affect(-1, 0)
        elif self.next_action == 's':
            self.affect(1, 0)
        elif self.next_action == 'a':
            self.affect(0, -1)
        elif self.next_action == 'd':
            self.affect(0, 1)
        self.delta_ore = int(self.ore_quantity - ore_before_tick)
        self.next_action = ''
        self.health_decay()

    def health_decay(self):
        self.health -= self.health_loss_per_turn
        self.check_if_dead()

    def affect(self, row_offset, col_offset):  # Horrible function name but I'll let Hal rename it
        affected_cell = self.try_get_cell_by_offset(row_offset, col_offset)
        if affected_cell is not None and affected_cell is not False:
            # Movement
            if self.try_move(affected_cell):
                return True
            # Cannot move, something interactive must be in the way.
            elif self.try_mining(affected_cell):
                return True
            elif self.try_going_to_hospital(affected_cell):
                return True
            # Since there's nothing to mine, the player must be trying to attack another player
            elif self.try_attacking(affected_cell):
                return True
            else:
                return False
        else:
            return False

    def try_attacking(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Player')
            if struct[0]:
                other_player = _cell.get_game_object_by_obj_id(struct[1])
                if other_player[0]:
                    struct = other_player[1].take_damage(self.attack_power)
                    if struct[0]:  # Means we killed the other player
                        self.add_ore(struct[1])
                        return True
        return False

    def add_ore(self, amount):
        self.ore_quantity += amount
        return True

    def reset_ore(self):
        old_ore = int(self.ore_quantity)
        self.ore_quantity = 0
        return old_ore

    def take_damage(self, damage):
        self.health -= damage
        if self.check_if_dead():
            return True, self.reset_ore()
        else:
            return False, 0

    def try_mining(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('OreDeposit')
            if struct[0]:
                ore_deposit = _cell.get_game_object_by_obj_id(struct[1])
                if ore_deposit[0]:
                    self.ore_quantity += ore_deposit[1].ore_per_turn
                    return True
        return False

    def try_going_to_hospital(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('Hospital')
            if struct[0]:
                hospital = _cell.get_game_object_by_obj_id(struct[1])
                if hospital[0]:
                    assert(hospital[1].__class__.__name__ == 'Hospital')
                    if self.ore_quantity >= 10:
                        self.health = min(self.health + hospital[1].health_regen_per_turn, self.health_cap)
                        self.ore_quantity -= hospital[1].ore_usage_cost
                        return True
                    return False
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
            'ore_quantity': self.ore_quantity,
            'delta_ore': self.delta_ore,
            'health': self.health,
            'world_age': self.world.world_age
        }
        return response

    def check_if_dead(self):
        if self.health <= 0:
            self.change_cell(self.world.respawn_cell)
            self.health += self.starting_health
            return True
        else:
            return False
