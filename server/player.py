import uuid, random
from cell import Cell
import gameObject


class Player(gameObject.GameObject):
    def __init__(self, _id, _world, _cell):
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
        # self.cell = self.get_starting_cell()

    def action(self, _dir):
        self.next_action = _dir
        print(self.next_action)

    def line_of_stats(self):
        return 'hp: {health} ore: {ore} row: {row} col: {col}'.format(health=self.health,
                                                                      ore=self.ore_quantity,
                                                                      row=self.row,
                                                                      col=self.col)

    """  # Commented out functions for moving for this conflict fix
    def input(self, key):

        if key == 'w':
            self.try_move(0, 1, 'col')
        elif key == 's':
            self.try_move(0, -1, 'col')
        elif key == 'a':
            self.try_move(-1, 0, 'row')
        elif key == 'd':
           self.try_move(1, 0, 'row')

    def try_move(xOffset, yOffset):
        new_cell = self.try_get_cell_by_offset(xOffset, yOffset)
        if(new_cell):
            self.change_cell(new_cell)
            return True
        return False
    """

    def world_state(self):
        los = self.line_of_stats().ljust(self.world.rows)
        los = list(los)
        worldmap = self.world.get_world(player_id=self.id)
        worldmap.append(los)
        return worldmap

    """
    def get_starting_cell(self):
        return self.world.get_random_cell()
    """
