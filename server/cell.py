import uuid, random
import gameObject
import warnings


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

    def add_hospital(self):
        a = gameObject.Hospital(self)
        self.add_game_object(a)

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
        for obj in self.contents:
            if obj.__class__.__name__ == obj_type_name:
                return True, obj.obj_id
        return False, ''

    def get_game_object_by_obj_id(self, obj_id):
        for obj in self.contents:
            if obj.obj_id == obj_id:
                return True, obj
        return False

    def render(self, **keyword_parameters):

        priority = ['Player', 'OreDeposit', 'Hospital', 'Loot', 'Fence', 'EmptySpace']

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

    def can_enter(self):
        for obj in self.contents:
            if obj.passable is False:
                return False
        return True
    """
    def try_get_cell_by_offset(self, row_offset, col_offset):
        return self.world.get_cell(self.row + row_offset, self.col + col_offset)
    """
