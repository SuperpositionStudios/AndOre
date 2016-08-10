import uuid, random, datetime
from child_game.cell import Cell
from child_game.player import Player
from child_game.corporation import Corporation
import warnings
from child_game import helper_functions
import requests


class World:  # World is not really world, it's more Level

    def __init__(self, master_node_address):
        self.master_node_address = master_node_address
        self.rows = 20  # (9 * 3 - 2) - 5
        self.cols = 55  # (16 * 3) + 7
        self.world = []
        self.world_age = 1
        self.last_tick = datetime.datetime.now()
        self.microseconds_per_tick = 350000
        #self.microseconds_per_tick = 35000
        self.players = dict()
        self.corporations = dict()
        self.buildings = dict()

        for row in range(self.rows):
            current_row = []
            for col in range(self.cols):
                current_cell = Cell(self, row, col)
                current_row.append(current_cell)
            self.world.append(current_row)

        self.respawn_cell = self.get_cell(0, 0)

        assert(len(self.world) == self.rows)
        assert(len(self.world[0]) == self.cols)

    def tick(self):
        self.last_tick = datetime.datetime.now()
        self.world_age += 1
        self.tick_corp_buildings()
        self.update_values()

    def update_values(self):
        data = {
            'corporations': dict()
        }
        for corp_id in self.corporations:
            corp_obj = self.corporations[corp_id]
            data['corporations'][corp_id] = {
                'ore_delta': corp_obj.pending_requests['ore_delta']
            }
        req = requests.post(self.master_node_address + '/update_values', json=data)
        response = req.json()
        if response['Successful_Request']:
            for corp_id in response['corporations']:
                if corp_id in self.corporations:
                    corp_obj = self.corporations[corp_id]
                    corp_obj.pending_requests['ore_delta'] = 0
                    corp_obj.set_ore_quantity(response['corporations'][corp_id]['ore_quantity'])

    def tick_corp_buildings(self):
        for corp_id, corp in self.corporations.items():
            corp.tick_buildings()

    def render_world(self, **keyword_parameters):
        if 'player_id' in keyword_parameters:
            player_id = keyword_parameters['player_id']
            rendered_world = []
            for row in range(self.rows):
                current_row = []
                for col in range(self.cols):
                    rendered = self.world[row][col].render(player_id=player_id)
                    current_row.append(rendered)
                rendered_world.append(current_row)
        else:
            rendered_world = []
            for row in range(self.rows):
                current_row = []
                for col in range(self.cols):
                    rendered = self.world[row][col].render()
                    current_row.append(rendered)
                rendered_world.append(current_row)
        assert(len(rendered_world) == 31, "Age: {} Len: {} Full: {}".format(self.world_age, len(rendered_world), rendered_world))
        return rendered_world

    def corp_exists(self, corp_id):
        return corp_id in self.corporations

    def new_player(self, player_id=None, corp_id=None, corp_ore_quantity=0):
        spawn_location = self.random_can_enter_cell()
        assert(spawn_location.__class__.__name__ == 'Cell')

        # Player ID
        if player_id is None:
            player_id = str(uuid.uuid4())

        # Corporation
        if corp_id is None:
            # If we weren't passed a corp_id, we generate one here
            corp_id = self.new_corporation().corp_id
        else:
            # If the corp does not exist in our node we create it here
            if self.corp_exists(corp_id) is False:
                self.new_corporation(corp_id=corp_id)
        # at this point, we know there is a corp in our node with the corp_id that was either passed in or generated.
        _corp = self.corporations[corp_id]
        # We update our ore quantity for the corp here
        _corp.ore_quantity = corp_ore_quantity

        new_player = Player(player_id, self, spawn_location, _corp)
        spawn_location.add_game_object(new_player)
        helper_functions.drint("Old players list")
        helper_functions.drint(self.players)
        self.players[player_id] = new_player
        helper_functions.drint("New player list")
        helper_functions.drint(self.players)
        helper_functions.drint("Successfully had a player transfer in")
        return player_id

    def random_can_enter_cell(self):
        random_cell = self.get_random_cell()
        max_tries = self.rows * self.cols
        attempt = 1
        while random_cell.can_enter() is False:
            random_cell = self.get_random_cell()
            attempt += 1
            if attempt == max_tries:
                return 'too many players'
        return random_cell

    def new_corporation(self, corp_id=None):
        new_corp = Corporation(self, corp_id=corp_id)
        self.corporations[new_corp.corp_id] = new_corp
        return new_corp

    def spawn_ore_deposits(self, num=1):
        assert(num <= self.rows * self.cols)

        for i in range(num):
            random_cell = self.get_random_cell()
            max_tries = self.rows * self.cols
            attempt = 1
            while random_cell.can_enter() is False:
                random_cell = self.get_random_cell()
                attempt += 1
                if attempt == max_tries:
                    return
            random_cell.add_ore_deposit()

    def spawn_hospitals(self, num=1):
        warnings.warn("Do not use this as this creates hospitals without an owner, which you cannot do", DeprecationWarning)
        assert (num <= self.rows * self.cols)

        for i in range(num):
            random_cell = self.get_random_cell()
            max_tries = self.rows * self.cols
            attempt = 1
            while random_cell.can_enter() is False:
                random_cell = self.get_random_cell()
                attempt += 1
                if attempt == max_tries:
                    return
            random_cell.add_hospital()

    def get_world(self, **keyword_parameters):
        if 'player_id' in keyword_parameters:
            player_id = keyword_parameters['player_id']
            return self.render_world(player_id=player_id)
        else:
            return self.render_world()

    def valid_player_id(self, _id):
        helper_functions.drint("Trying to find player with id {}".format(_id))
        return _id in self.players

    def get_cell(self, row, col):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        return self.world[row][col]

    def get_random_cell(self):
        row = random.randint(0, self.rows - 1)  # randint is inclusive
        col = random.randint(0, self.cols - 1)  # randint is inclusive
        return self.get_cell(row, col)
