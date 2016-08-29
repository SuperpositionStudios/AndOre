import uuid
from child_game import standing_colors, gameObject, world, corporation


class Cell:

    def __init__(self, _world: 'world.World', _row: int, _col: int):
        self.world = _world
        self.obj_id = str(uuid.uuid4())
        self.row = _row  # type: int
        self.col = _col  # type: int
        self.contents = []

    def try_get_cell_by_offset(self, row_offset: int, col_offset: int):
        fetched_cell = self.world.get_cell(self.row + row_offset, self.col + col_offset)
        if fetched_cell is False or fetched_cell is None:
            return False
        else:
            return fetched_cell

    def next_to_ore_deposit(self):
        directions = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]]
        for tup in directions:
            _cell = self.try_get_cell_by_offset(tup[0], tup[1])
            if _cell is not False:
                struct = _cell.contains_object_type('OreDeposit')
                if struct[0]:
                    od = _cell.get_game_object_by_obj_id(struct[1])
                    if od[0]:
                        od_obj = od[1]
                        assert (od_obj.__class__.__name__ == 'OreDeposit')
                        return True
        return False

    def damage_first_player(self, attacking_corp: 'corporation.Corporation', damage):
        struct = self.contains_object_type('Player')
        if struct[0]:
            player = self.get_game_object_by_obj_id(struct[1])
            if player[0]:
                player_obj = player[1]
                standing = attacking_corp.fetch_standing(player_obj.corp.corp_id)
                if standing == 'N' or standing == 'E':
                    player_obj.take_damage(damage)
                    return True
        return False

    def add_game_object(self, x):
        self.contents.append(x)

    def add_fence(self):
        a = gameObject.Fence(self)
        self.add_game_object(a)
        return a.ore_cost_to_deploy

    def add_ore_deposit(self):
        a = gameObject.OreDeposit(self)
        self.contents.append(a)

    def add_building(self, owner_corp: 'corporation.Corporation', building_type: str):
        assert (owner_corp.__class__.__name__ == 'Corporation')
        a = None
        if building_type == 'SentryTurret':
            a = gameObject.SentryTurret(self, owner_corp)
        elif building_type == 'SpikeTrap':
            a = gameObject.SpikeTrap(self, owner_corp)
        elif building_type == 'RespawnBeacon':
            a = gameObject.RespawnBeacon(self, owner_corp)
        elif building_type == 'Door':
            a = gameObject.Door(self, owner_corp)
        elif building_type == 'Pharmacy':
            a = gameObject.Pharmacy(self, owner_corp)
        elif building_type == 'Hospital':
            a = gameObject.Hospital(self, owner_corp)
        elif building_type == 'OreGenerator':
            a = gameObject.OreGenerator(self, owner_corp)
        self.add_game_object(a)

    def remove_object(self, object_id: str):
        for i in range(0, len(self.contents)):
            if self.contents[i].obj_id == object_id:
                del self.contents[i]
                return

    def contains_object_type(self, obj_type_name: str):
        # obj_type_name is the class name, example: 'Cell'
        # Returns a tuple, a boolean answering if the cell contains an object with the same class name as the input
        # and a string, if the boolean is true then it will return the object's obj_id
        # Returns as soon as one of the objects is found, so this may be unreliable in some use cases
        for obj in self.contents:
            if obj.__class__.__name__ == obj_type_name:
                return True, obj.obj_id
        return False, ''

    def get_game_object_by_obj_id(self, obj_id: str):
        for obj in self.contents:
            if obj.obj_id == obj_id:
                return True, obj
        return False, None

    def render(self, **keyword_parameters):

        priority = ['Player', 'SentryTurret', 'SpikeTrap', 'OreDeposit', 'Hospital', 'Pharmacy', 'OreGenerator', 'Loot', 'Fence', 'Door', 'RespawnBeacon']

        if 'player_id' in keyword_parameters:
            player_id = keyword_parameters['player_id']
            player_obj = self.world.players[player_id]

            for i in priority:
                if self.contains_object_type(i)[0]:
                    for obj in self.contents:
                        if obj.__class__.__name__ == i:
                            obj_class_name = obj.__class__.__name__

                            types_of_rendering = {
                                'Player': 'a',
                                'SentryTurret': 'b',
                                'SpikeTrap': 'b',
                                'Pharmacy': 'b',
                                'Hospital': 'b',
                                'Door': 'b',
                                'RespawnBeacon': 'b',
                                'OreGenerator': 'c',
                                'OreDeposit': 'd',
                                'Loot': 'd',
                                'Fence': 'd'
                            }

                            if types_of_rendering[obj_class_name] == 'a':
                                if player_obj.obj_id == obj.obj_id:
                                    return obj.inner_icon
                                else:
                                    standings_towards_player = player_obj.corp.fetch_standing_for_player(obj.obj_id)
                                    return obj.icons[standings_towards_player]
                            elif types_of_rendering[obj_class_name] == 'b':
                                owners = obj.owner_corp
                                owner_standings_towards_us = owners.fetch_standing_for_player(player_id)
                                return obj.icons[owner_standings_towards_us]
                            elif types_of_rendering[obj_class_name] == 'c':
                                generator_owners = obj.owner_corp
                                corp_standing_to_generator_owner_corp = player_obj.corp.fetch_standing(generator_owners.corp_id)
                                return obj.icons[corp_standing_to_generator_owner_corp]
                            else:
                                return obj.icon
            return ['.', standing_colors.mane['N']]  # Returns Empty Space
        else:
            for i in priority:
                if self.contains_object_type(i)[0]:
                    for obj in self.contents:
                        if obj.__class__.__name__ == i:
                            return obj.icon
            return ['.', standing_colors.mane['N']]  # Returns Empty Space

    def can_enter(self, player_obj=None):
        if player_obj is not None:
            assert(player_obj.__class__.__name__ == 'Player')
            for obj in self.contents:
                if obj.__class__.__name__ == 'OreDeposit' or obj.__class__.__name__ == 'Fence':
                    obj_standing = 'N'
                else:
                    obj_standing = obj.owner_corp.fetch_standing_for_player(player_obj.obj_id)
                if obj.passable[obj_standing] is False:
                    return False
            return True
        else:
            for obj in self.contents:
                obj_standing = 'N'
                if obj.passable[obj_standing] is False:
                    return False
            return True
