import uuid, random
from cell import Cell
import gameObject

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
            for i in range(self.cols):
                current_cell = Cell()
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