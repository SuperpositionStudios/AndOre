import uuid, random
from cell import Cell
import gameObject

#world is not really world, it's more Level
class World:
    def __init__(self):
        self.rows = 31
        self.cols = 32
        self.world = []
        """
        row = []
        for l in range(0, world_size['col']):
            a = Cell()
            row.append(a)
        for l in range(0, world_size['row']):
            self.world.append(row)"""

        for i in range(self.rows):
            current_row = []
            x = i
            for i in range(self.cols):
                y = i
                current_cell = Cell(self, x, y)
                current_row.append(current_cell)
            self.world.append(current_row)

    def get_world(self):
        rendered_world = []
        e_r = []
        for l in range(0, self.cols):
            e_r.append(" ")

        for l in range(0, self.rows):
            rendered_world.append(e_r)

        for row in range(0, self.rows):
            for col in range(0, self.cols):
                rendered_world[row][col] = self.world[row][col].render()
        return rendered_world

    def get_cell(self, x, y):
        if x < 0 or x >= self.cols:
            return false
        if y < 0 or y >= self.rows:
            return false
        return self.world[x][y]

    def get_random_cell(self):
        x = random.randint(0, self.rows)
        y = random.randint(0, self.cols)
        return self.get_cell(x,y)
