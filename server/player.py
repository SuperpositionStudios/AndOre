import uuid, random
import gameObject
class Player(gameObject.GameObject):

    def __init__(self, _id, _world):
        assert(_world != None)

        self.id = _id
        self.world = _world
        self.health = 100
        self.ore_quantity = 0
        self.inner_icon = '@'
        self.icon = '!'
        self.cell = self.get_starting_cell()


    def input(self, key):

        if key == 'w':
            self.try_move(0, 1, 'col')
        elif key == 's':
            self.try_move(0, -1, 'col')
        elif key == 'a':
            self.try_move(-1, 0, 'row')
        elif key == 'd':
           self.try_move(1, 0, 'row')

    def line_of_stats(self):
        return 'hp: {health} ore: {ore} x: {x} y: {y}'.format(health=self.health,
                                                                  ore=self.ore_quantity,
                                                                  x=self.cell.x,
                                                                  y=self.cell.y)

    def try_move(xOffset, yOffset):
        new_cell = self.try_get_cell_by_offset(xOffset, yOffset)
        if(new_cell):
            self.change_cell(new_cell)
            return True
        return False

    def world_state(self):
        los = self.line_of_stats().ljust(self.world.rows)
        los = list(los)
        worldmap = self.world.get_world()
        worldmap.append(los)
        return worldmap

    def get_starting_cell(self):
        return self.world.get_random_cell()