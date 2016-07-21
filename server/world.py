import uuid, random
from cell import Cell
from player import Player


class World:
    def __init__(self):
        self.rows = 31
        self.cols = 32
        self.world = []
        self.players = dict()

        for row in range(self.rows):
            current_row = []
            for col in range(self.cols):
                current_cell = Cell(row, col)
                current_row.append(current_cell)
            self.world.append(current_row)

        assert(len(self.world) == self.rows)
        assert(len(self.world[0]) == self.cols)

    def new_player(self):
        row = random.randint(0, self.rows - 1)  # randint is inclusive
        col = random.randint(0, self.cols - 1)  # randint is inclusive
        player_id = str(uuid.uuid4())

        new_player = Player(player_id, self, self.world[row][col])
        self.world[row][col].add_game_object(new_player)
        self.players[player_id] = new_player

        return player_id

    def get_world(self):
        rendered_world = []

        for row in range(self.rows):
            current_row = []
            for col in range(self.cols):
                rendered = self.world[row][col].render()
                current_row.append(rendered)
            rendered_world.append(current_row)

        return rendered_world
