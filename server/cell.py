import uuid, random
import gameObject


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

    def destroy(self):
        self.world = None
        self.contents = None
        for obj in self.contents:
            obj.leave_cell(self)

    def add_object(self, obj):
        if obj.cell != self:
            obj.cell = self

        self.contents.append(obj)

    def remove_object(self, object_id):
        for i in range(0, len(self.contents)):
            if self.contents[i].obj_id == object_id:
                del self.contents[i]

    def contains_object_type(self, obj_type_name):
        for obj in self.contents:
            if obj.__class__.__name__ == obj_type_name:
                return True, obj.obj_id
        return False, ''

    def render(self, **keyword_parameters):

        priority = ['Player', 'OreDeposit', 'EmptySpace']

        if 'player_id' in keyword_parameters:
            player_id = keyword_parameters['player_id']

            for i in priority:
                if self.contains_object_type(i)[0]:
                    for obj in self.contents:
                        if obj.__class__.__name__ == i:
                            if obj.obj_id == player_id:
                                return obj.inner_icon
                            else:
                                return obj.icon
            return '#'  # Returns Empty Space
        else:
            for i in priority:
                if self.contains_object_type(i)[0]:
                    for obj in self.contents:
                        if obj.__class__.__name__ == i:
                            return obj.icon
            return '#'  # Returns Empty Space
    """
    def can_enter(self):
        for obj in self.contents:
            if not obj.can_enter:
                return False

        return True

    def try_get_cell_by_offset(self, row_offset, col_offset):
        return self.world.get_cell(self.row + row_offset, self.col + col_offset)
    """
