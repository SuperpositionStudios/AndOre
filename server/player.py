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
        self.health = 100
        self.ore_quantity = 0
        self.inner_icon = '@'
        self.icon = '!'
        self.row = self.cell.row
        self.col = self.cell.col
        self.next_action = ''
        self.passable = False

    def action(self, _dir):
        self.next_action = _dir
        self.tick()

    def line_of_stats(self):
        return 'hp {health} ore {ore} row {row} col {col} m {next_action}'.format(health=self.health,
                                                                                  ore=self.ore_quantity,
                                                                                  row=self.row,
                                                                                  col=self.col,
                                                                                  next_action=self.next_action)

    def tick(self):
        # Movement
        if self.next_action == 'w':
            self.affect(-1, 0)
        elif self.next_action == 's':
            self.affect(1, 0)
        elif self.next_action == 'a':
            self.affect(0, -1)
        elif self.next_action == 'd':
            self.affect(0, 1)

    def affect(self, row_offset, col_offset):  # Horrible function name but I'll let Hal rename it
        affected_cell = self.try_get_cell_by_offset(row_offset, col_offset)
        if affected_cell is not None:
            # Movement
            if self.try_move(affected_cell):
                return True
            # Cannot move, something interactive must be in the way.
            elif self.try_mining(affected_cell):
                return True
            else:
                return False
        else:
            return False

    def try_mining(self, _cell):
        if _cell is not None:
            struct = _cell.contains_object_type('OreDeposit')
            if struct[0]:
                ore_deposit = _cell.get_game_object_by_obj_id(struct[1])
                if ore_deposit[0]:
                    self.ore_quantity += ore_deposit[1].ore_per_turn
                    return True
                else:
                    return False
            else:
                return False
        else:
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
        return self.world.get_cell(self.row + row_offset, self.col + col_offset)

    def world_state(self):
        los = self.line_of_stats().ljust(self.world.rows)
        los = list(los)
        worldmap = self.world.get_world(player_id=self.id)
        worldmap.append(los)
        return worldmap
