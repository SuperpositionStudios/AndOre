import uuid, random
from cell import Cell
from player import Player


class World:  # World is not really world, it's more Level

    def __init__(self):
        self.rows = 31
        self.cols = 32
        self.world = []
        self.players = dict()

        for row in range(self.rows):
            current_row = []
            for col in range(self.cols):
                current_cell = Cell(self, row, col)
                current_row.append(current_cell)
            self.world.append(current_row)

        assert(len(self.world) == self.rows)
        assert(len(self.world[0]) == self.cols)

    def new_player(self):
        random_cell = self.get_random_cell()
        max_tries = self.rows * self.cols
        attempt = 1
        while random_cell.can_enter() is False:
            random_cell = self.get_random_cell()
            attempt += 1
            if attempt == max_tries:
                return 'too many players'

        player_id = str(uuid.uuid4())

        new_player = Player(player_id, self, random_cell)
        random_cell.add_game_object(new_player)
        self.players[player_id] = new_player

        return player_id

    def get_world(self, **keyword_parameters):

        rendered_world = []

        if 'player_id' in keyword_parameters:
            player_id = keyword_parameters['player_id']

            for row in range(self.rows):
                current_row = []
                for col in range(self.cols):
                    rendered = self.world[row][col].render(player_id=player_id)
                    current_row.append(rendered)
                rendered_world.append(current_row)
        else:
            for row in range(self.rows):
                current_row = []
                for col in range(self.cols):
                    rendered = self.world[row][col].render()
                    current_row.append(rendered)
                rendered_world.append(current_row)
        return rendered_world

    def get_cell(self, row, col):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return self.world[row][col]

    def get_random_cell(self):
        row = random.randint(0, self.rows - 1)  # randint is inclusive
        col = random.randint(0, self.cols - 1)  # randint is inclusive
        return self.get_cell(row, col)
