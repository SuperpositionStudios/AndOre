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

        if self.next_action == 'w':
            self.try_move(-1, 0)
        elif self.next_action == 's':
            self.try_move(1, 0)
        elif self.next_action == 'a':
            self.try_move(0, -1)
        elif self.next_action == 'd':
            self.try_move(0, 1)

    def try_move(self, row_offset, col_offset):
        new_cell = self.try_get_cell_by_offset(row_offset, col_offset)
        if new_cell is not None:
            self.change_cell(new_cell)
            return True
        return False

    def try_get_cell_by_offset(self, row_offset, col_offset):
        return self.world.get_cell(self.row + row_offset, self.col + col_offset)

    def world_state(self):
        los = self.line_of_stats().ljust(self.world.rows)
        los = list(los)
        worldmap = self.world.get_world(player_id=self.id)
        worldmap.append(los)
        return worldmap
