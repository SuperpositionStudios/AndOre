import uuid, random
from cell import Cell
from player import Player


#world is not really world, it's more Level
class World:
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
        row = random.randint(0, self.rows - 1)  # randint is inclusive
        col = random.randint(0, self.cols - 1)  # randint is inclusive
        player_id = str(uuid.uuid4())

        new_player = Player(player_id, self, self.world[row][col])
        self.world[row][col].add_game_object(new_player)
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
    """
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
    """
