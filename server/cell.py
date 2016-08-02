import uuid, random
import gameObject
import warnings
from corporation import Corporation


class Cell:

    def __init__(self, _world, _row, _col):
        self.world = _world
        self.obj_id = str(uuid.uuid4())
        self.row = _row
        self.col = _col
        self.contents = []

    def add_game_object(self, x):
        self.contents.append(x)

    def add_ore_deposit(self):
        a = gameObject.OreDeposit(self)
        self.contents.append(a)

    def add_pharmacy(self, owner_corp):
        assert(owner_corp.__class__.__name__ == 'Corporation')
        a = gameObject.Pharmacy(self, owner_corp)
        self.add_game_object(a)

    def add_hospital(self, owner_corp):
        assert(owner_corp.__class__.__name__ == 'Corporation')
        a = gameObject.Hospital(self, owner_corp)
        self.add_game_object(a)

        return a.price_to_construct

    def add_ore_generator(self, owner_corp):
        assert(owner_corp.__class__.__name__ == 'Corporation')
        a = gameObject.OreGenerator(self, owner_corp)
        self.add_game_object(a)

        return a.price_to_construct

    def add_fence(self):
        a = gameObject.Fence(self)
        self.add_game_object(a)
        return a.ore_cost_to_deploy

    def destroy(self):
        self.world = None
        self.contents = None
        for obj in self.contents:
            obj.leave_cell(self)

    def add_object(self, obj):
        warnings.warn("Use add_game_object instead", DeprecationWarning)  #
        if obj.cell != self:
            obj.cell = self

        self.contents.append(obj)

    def remove_object(self, object_id):
        for i in range(0, len(self.contents)):
            #print("{} out of {}".format(i, len(self.contents)))
            if self.contents[i].obj_id == object_id:
                del self.contents[i]
                return

    def contains_object_type(self, obj_type_name):
        # obj_type_name is the class name, example: 'Cell'
        # Returns a tuple, a boolean answering if the cell contains an object with the same class name as the input
        # and a string, if the boolean is true then it will return the object's obj_id
        # Returns as soon as one of the objects is found, so this may be unreliable in some use cases
        for obj in self.contents:
            if obj.__class__.__name__ == obj_type_name:
                return True, obj.obj_id
        return False, ''

    def get_game_object_by_obj_id(self, obj_id):
        for obj in self.contents:
            if obj.obj_id == obj_id:
                return True, obj
        return False, None

    def render(self, **keyword_parameters):

        priority = ['Player', 'OreDeposit', 'Hospital', 'Pharmacy', 'OreGenerator', 'Loot', 'Fence', 'EmptySpace']

        if 'player_id' in keyword_parameters:
            player_id = keyword_parameters['player_id']
            player_obj = self.world.players[player_id]

            for i in priority:
                if self.contains_object_type(i)[0]:
                    for obj in self.contents:
                        if obj.__class__.__name__ == i:
                            if obj.__class__.__name__ == 'Player':
                                if obj.obj_id == player_id:
                                    return obj.inner_icon
                                elif player_obj.corp.check_if_in_corp(obj.obj_id):
                                    return obj.corp_member_icon
                                else:
                                    return player_obj.corp.fetch_standing(obj.corp.corp_id)
                            elif obj.__class__.__name__ == 'Hospital':
                                hospital_owners = obj.owner_corp
                                owner_standings_towards_us = hospital_owners.fetch_standing_for_player(player_id)
                                return obj.icons[owner_standings_towards_us]
                            elif obj.__class__.__name__ == 'OreGenerator':
                                generator_owners = obj.owner_corp
                                corp_standing_to_generator_owner_corp = player_obj.corp.fetch_standing(generator_owners.corp_id)
                                return obj.icons[corp_standing_to_generator_owner_corp]
                            elif obj.__class__.__name__ == 'Pharmacy':
                                owners = obj.owner_corp
                                corp_standing_to_owners = player_obj.corp.fetch_standing(owners.corp_id)
                                return obj.icons[corp_standing_to_owners]
                            else:
                                return obj.icon
            return '.'  # Returns Empty Space
        else:
            for i in priority:
                if self.contains_object_type(i)[0]:
                    for obj in self.contents:
                        if obj.__class__.__name__ == i:
                            return obj.icon
            return '.'  # Returns Empty Space

    def can_enter(self, player_obj=None):
        if player_obj is not None:
            assert(player_obj.__class__.__name__ == 'Player')
            for obj in self.contents:
                if obj.__class__.__name__ == 'OreDeposit':
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
    """
    def try_get_cell_by_offset(self, row_offset, col_offset):
        return self.world.get_cell(self.row + row_offset, self.col + col_offset)
    """
