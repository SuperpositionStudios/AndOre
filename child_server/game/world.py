import datetime
from cell import Cell


class World:

    def __init__(self):
        self.rows = 20  # (9 * 3 - 2) - 5
        self.cols = 55  # (16 * 3) + 7
        self.world = []
        self.world_age = 1
        self.last_tick = datetime.datetime.now()
        self.microseconds_per_tick = 350000
        self.player_characters = dict()
        self.corporations = dict()
        self.buildings = dict()

        for row in range(self.rows):
            current_row = []
            for col in range(self.cols):
                current_cell = Cell(self, row, col)
                current_row.append(current_cell)
            self.world.append(current_row)

        self.respawn_cell = self.get_cell(0, 0)

        assert (len(self.world) == self.rows)
        assert (len(self.world[0]) == self.cols)

    def tick(self):
        self.last_tick = datetime.datetime.now()
        self.world_age += 1
        self.tick_corp_buildings()

    def tick_corp_buildings(self):
        for corp_id, corp in self.corporations.items():
            corp.tick_buildings()

    def get_cell(self, row, col):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return self.world[row][col]

