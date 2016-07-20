import uuid, random
from cell import Cell
from gameObject import GameObject


class World:
    def __init__(self):
        self.rows = 31
        self.cols = 32
        self.world = []

        for row in range(self.rows):
            current_row = []
            for col in range(self.cols):
                current_cell = Cell(row, col)
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
