import uuid, random
from cell import Cell


class Player:
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

    def action(self, _dir):
        self.next_action = _dir
        print(self.next_action)

    def line_of_stats(self):
        return 'hp: {health} ore: {ore} row: {row} col: {col}'.format(health=self.health,
                                                                      ore=self.ore_quantity,
                                                                      row=self.row,
                                                                      col=self.col)

    def world_state(self):
        los = self.line_of_stats().ljust(self.world.rows)
        los = list(los)
        worldmap = self.world.get_world(player_id=self.id)
        worldmap.append(los)
        return worldmap
